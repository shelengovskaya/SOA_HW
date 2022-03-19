import grpc
from concurrent import futures
import time
import sys
import threading

from queue import Queue

import mafia_service_pb2_grpc as pb2_grpc
import mafia_service_pb2 as pb2


def listen_for_messages(stub, queue):
    responses = stub.Connect(pb2.ConnectMessage(name=sys.argv[1]))
    for response in responses:
        print(response)
        if response.HasField("new_session_message"):
            queue.put(response.new_session_message.session_id)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pb2_grpc.MafiaStub(channel)

        queue = Queue()
        threading.Thread(target=listen_for_messages, daemon=False, args=[stub, queue]).start()

        session_id = queue.get()
        print("session_id = " + session_id)

        while True:
            command = input()
            if command.startswith("say "):
                stub.Say(pb2.SayMessage(session_id=session_id, name=sys.argv[1], message=command[len("say "):]))
            elif command.startswith("kill "):
                stub.Kill(pb2.KillMessage(session_id=session_id, name=sys.argv[1], name_to_kill=command[len("kill "):]))
            elif command == "close":
                stub.CloseDay(pb2.CloseDayMessage(session_id=session_id, name=sys.argv[1]))
            else:
                print("Invalid command, expected one of [say, ]")

if __name__=='__main__':
    run()
