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

from models import db, User, Stats


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


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['JWT_SECRET_KEY'] = 'my_super_secret_jwt_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False


db.init_app(app)

with app.app_context():
    db.create_all()


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


@app.route('/users', methods=['POST'])
def register():
    data = get_data()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return 'No username or password', 400

    handle_params(data)

    new_user = User()
    new_user.Stats = Stats()

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


@app.route('/users/<int:user_id>', methods=['GET'], endpoint='get_user')
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return 'No such user', 404
    return jsonify(user.to_dict())


@app.route('/users/me', methods=['GET'])
@jwt_required()
def get_me():
    return get_user(get_jwt_identity())


@app.route('/users', methods=['GET'])
def get_all_users():
    users = list(map(lambda user: user.to_dict(), User.query.all()))
    return jsonify(users)


@app.route('/users/<int:user_id>', methods=['PUT', 'PATCH', 'DELETE'], endpoint='modify_user')
@jwt_required()
def modify_user(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'DELETE':
        print(user.avatar)
        # if user.avatar:
        #     (IMG_PATH / user.avatar).unlink()
        user.delete()
        return Response(status=204)

    data = get_data()
    handle_params(data)
    avatar_path = data.get('avatar', None)
    # if avatar_path and user.avatar:
    #     (IMG_PATH / user.avatar).unlink()
    user.safe_update(data)
    return get_user(user_id)


@app.route('/users/<int:user_id>/stats', methods=['GET', 'PUT', 'PATCH'], endpoint='handle_stats')
@jwt_required()
def handle_stats(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'GET':
        return jsonify(user.stats.to_dict())

    data = get_data()
    data = {'stats': data}
    user.safe_update(data)
    return jsonify(user.stats.to_dict())


def make_data(user):
    result = user.to_dict()
    result.update(user.stats.to_dict())
    result['id'] = user.id
    result['username'] = user.username
    return result

def generate_report(player_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 15)
    avatar_fname = player_dict.get('avatar', None)
    if avatar_fname:
        pdf.image(name=str(pathlib.Path('./img').absolute() / avatar_fname), w=70, h=70)

    for k in ('username', 'gender', 'email', 'total_sessions', 'total_victories', 'total_defeats', 'total_time'):
        pdf.cell(70, 10, f'{k}: {player_dict[k]}', ln=1)
    path = str(f"{player_dict['id']}.pdf")
    pdf.output(path).encode('latin-1')
    return path

def make_pdf(user):
    def make_dict(user):
        result = user.to_dict()
        result.update(user.stats.to_dict())
        result['id'] = user.id
        result['username'] = user.username
        return result

    user = make_dict(user)
    return generate_report(user)


@app.route('/users/<int:user_id>/pdf', methods=['POST', 'GET'], endpoint='handle_stats_file')
@jwt_required()
def handle_stats_file(user_id):
    if get_jwt_identity() != user_id:
        abort(403)
    user = User.query.get(user_id)
    if request.method == 'POST':
        path = make_pdf(user)
        return jsonify({'url': f'/users/{user_id}/pdf'})
    else:
        return send_file('{}.pdf'.format(user_id), download_name=f'{user.username}_stats.pdf')


if __name__ == '__main__':
    subprocess.Popen(['python3', 'worker.py'])
    app.run(host='0.0.0.0')
