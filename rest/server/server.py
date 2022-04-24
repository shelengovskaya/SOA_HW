import json
import os
import subprocess
import time
import uuid
import textwrap
from fpdf import FPDF
import pathlib
import textract
import hashlib

from flask import Flask, jsonify, request, abort, send_file
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class statistics(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    sessions = database.Column(database.Integer, default=0)
    victories = database.Column(database.Integer, default=0)
    defeats = database.Column(database.Integer, default=0)
    time_in_game = database.Column(database.Integer, default=0)

    ATTRS_PUBLIC = ('sessions', 'victories',
                    'defeats', 'time_in_game')

    def to_dict(self):
        result = dict(map(
            lambda attr: (attr, getattr(self, attr)),
            self.ATTRS_PUBLIC
        ))
        return result


class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(), unique=True, nullable=False)
    password = database.Column(database.String(), nullable=False)
    email = database.Column(database.String())
    gender = database.Column(database.String())
    avatar = database.Column(database.String())
    statistics_id = database.Column(database.Integer, database.ForeignKey(statistics.id))
    statistics = database.relationship(statistics, backref='statistics', uselist=False)

    ATTRS_PUBLIC = ('username', 'email', 'gender', 'avatar')
    __ATTRS_PRIVATE = ('password',)

    __ATTRS_ALL = ATTRS_PUBLIC + __ATTRS_PRIVATE

    def safe_update(self, data):
        if not self.statistics:
            self.statistics = statistics()
        for attr, value in data.items():
            if attr in (self.__ATTRS_ALL):
                setattr(self, attr, value)
        if 'statistics' in data:
            for attr, value in data['statistics'].items():
                if attr in statistics.ATTRS_PUBLIC:
                    setattr(self.statistics, attr, value)

        database.session.add(self)
        database.session.commit()

    def to_dict(self):
        result = dict(map(
            lambda attr: (attr, getattr(self, attr)),
            self.ATTRS_PUBLIC
        ))
        result['avatar'] = self.avatar
        result['user_id'] = self.id
        result['username'] = self.username
        result['user_path'] = f'/user/{self.id}'
        result['statistics_path'] = f'/user/statistics/{self.id}'  
        return result

    def delete(self):
        statistics.query.filter_by(id=self.statistics.id).delete()
        database.session.delete(self)
        database.session.commit()


def publish(user):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')
    body = json.dumps(make_data(user)).encode('utf-8')
    channel.basic_publish(exchange='', routing_key='rpc_queue',
                          body=body)
    connection.close()



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///statistics.database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


database.init_app(app)

with app.app_context():
    database.create_all()

app.config['JWT_SECRET_KEY'] = 'secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)


def check_access(user_id):
    if get_jwt_identity() != user_id:
        abort(403)



def get_data():
    data = request.json
    if data:
        return data
    data = request.form.get('json')
    if data:
        return json.loads(data)
    return {}

def handle_params(data):
    password = data.get('password', None)
    if password is not None:
        data['password'] = hashlib.sha256(password.encode('utf-8')).hexdigest()
    avatar = data.get('avatar', None)


@app.route('/all_users', methods=['GET'])
def get_all_users():
    users = list(map(lambda user: user.to_dict(), User.query.all()))
    return jsonify(users)


@app.route('/add_user', methods=['POST'])
def register():
    data = get_data()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return 'No username or password', 400

    handle_params(data)

    new_user = User()
    new_user.statistics = statistics()

    try:
        new_user.safe_update(data)
    except IntegrityError:
        return 'User exists', 400

    result = {'user': new_user.to_dict(
    ), 'token': create_access_token(identity=new_user.id)}
    return jsonify(result)


@app.route('/login', methods=['POST'])
def login():
    data = get_data()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return 'No info', 400

    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = User.query.filter_by(
        username=username, password=password).first()
    if user is None:
        return 'No user', 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'token': access_token, 'user': f'/users/{user.id}'}), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return 'No such user', 404
    return jsonify(user.to_dict())


@app.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    return get_user(get_jwt_identity())


@app.route('/user/<int:user_id>', methods=['PUT', 'PATCH', 'DELETE'])
@jwt_required()
def modify_user(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'DELETE':
        print(user.avatar)

        user.delete()
        return 'User deleted.'

    data = get_data()
    handle_params(data)
    avatar_path = data.get('avatar', None)

    user.safe_update(data)
    return get_user(user_id)


@app.route('/user/statistics/<int:user_id>', methods=['GET', 'PATCH'])
@jwt_required()
def handle_statistics(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'GET':
        return jsonify(user.statistics.to_dict())

    data = get_data()
    data = {'statistics': data}
    user.safe_update(data)
    return jsonify(user.statistics.to_dict())


def make_data(user):
    result = user.to_dict()
    result.update(user.statistics.to_dict())
    result['id'] = user.id
    result['username'] = user.username
    return result

def generate_report(user_info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 22)
    avatar_fname = user_info.get('avatar', None)
    if avatar_fname:
        pdf.image(name=str(pathlib.Path('./img').absolute() / avatar_fname), w=150, h=100)

    for k in ('username', 'gender', 'email', 'sessions', 'victories', 'defeats', 'time_in_game'):
        pdf.cell(70, 10, f'{k}: {user_info[k]}', ln=1)
    path = str(f"{user_info['id']}.pdf")
    pdf.output(path).encode('latin-1')
    return path

def make_pdf(user):
    def make_dict(user):
        result = user.to_dict()
        result.update(user.statistics.to_dict())
        result['id'] = user.id
        result['username'] = user.username
        return result

    user = make_dict(user)
    return generate_report(user)


@app.route('/user/pdf/<int:user_id>', methods=['POST', 'GET'])
@jwt_required()
def handle_statistics_file(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'POST':
        path = make_pdf(user)
        return jsonify({'request_path': f'/user/pdf/{user_id}'})
    else:
        return send_file('{}.pdf'.format(user_id), download_name=f'{user.username}.pdf')


if __name__ == '__main__':
    subprocess.Popen(['python3', 'worker.py'])
    app.run(host='0.0.0.0')
