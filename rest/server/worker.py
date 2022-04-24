import os
import pika
import sys
import json
from fpdf import FPDF
import pathlib



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')

    def make_result(body):
        body =os.getenv('RABBITMQ_HOST', 'localhost')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 15)
        avatar_fname = player_dict.get('avatar', None)
        if avatar_fname:
            pdf.image(name=str(pathlib.Path('./img').absolute() / avatar_fname), w=70, h=70)

        for k in ('username', 'gender', 'email', 'total_sessions', 'total_victories', 'total_defeats', 'total_time'):
            pdf.cell(70, 10, f'{k}: {player_dict[k]}', ln=1)
        path = str(pathlib.Path('./pdf').absolute() / f"{player_dict['id']}.pdf")
        pdf.output(path).encode('latin-1')
        return path

    def callback(ch, method, properties, body):
        print(' [*] Data received')
        path = make_result(body)
        print(f' [*] PDF created: {path}')

    channel.basic_consume(queue='rpc_queue',
                          on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


main()
