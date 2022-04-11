import pika
from grabber import Grabber
from queue import Queue
import threading

def get_count(url1, url2):

    queue = Queue()
    queue.put('1 '+url1)

    prev_urls = set()

    while not queue.empty():
        urls = queue.get()
        url_split = urls.split()
        k = int(url_split[0])
        url = url_split[-1]

        prev_urls.add(url)

        grabber = Grabber(url)

        all_urls = grabber.get_internal_urls()

        print("[+] Total internal URLs:", len(grabber.get_internal_urls()))

        for url in all_urls:

            if url == url2:
                return urls + ' ' + url2

            if url not in prev_urls:
                queue.put(str(k+1)+' '+(' '.join(url_split[1:]))+' '+url)

    return None

threads = []


def on_request(ch, method, props, body):
    url1, url2 = body.decode().split()

    print(url1)
    print(url2)
    response = get_count(url1, url2)

    print('Response:', response)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=str(response.replace(' ', '\n')))
    ch.basic_ack(delivery_tag=method.delivery_tag)



connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, heartbeat=10000))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


channel.basic_qos(prefetch_count=3)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
