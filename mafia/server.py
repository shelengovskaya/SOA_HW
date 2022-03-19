import grpc
from concurrent import futures

import random
import uuid
import time
import threading

import mafia_service_pb2_grpc as pb2_grpc
import mafia_service_pb2 as pb2

class Session:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.in_progress = False
        self.clients = set()
        self.detective = None
        self.vigilante = None
        self.killed = set()
        self.vigilante_voted = None
        self.investigated = None
        self.condition = threading.Condition()
        self.messages = []
        self.is_day = True
        self.day_kill_votes = {}
        self.day_closed = set()
        self.first_day = True

    def add_client(self, name):
        if self.clients.add(name):
            pass

        if len(self.clients) == 4:
            self.in_progress = True
            r = list(random.sample(self.clients, 2))
            self.detective = r[0]
            self.vigilante = r[1]
            print('detective = ' + self.detective)
            print('vigilante = ' + self.vigilante)
            return True
        return False

    def get_client_role(self, name):
        if name == self.detective:
            return pb2.ServerMessage.GameStartedMessage.Role.DETECTIVE
        elif name == self.vigilante:
            return pb2.ServerMessage.GameStartedMessage.Role.VIGILANTE
        else:
            return pb2.ServerMessage.GameStartedMessage.Role.VILLAGER

class MafiaService(pb2_grpc.MafiaServicer):
    def __init__(self, *args, **kwargs):
        self.sessions = {}

    def find_or_create_session(self):
        for s in self.sessions.values():
            if not s.in_progress:
                return s

        s = Session()
        self.sessions[s.session_id] = s
        return s

    def Say(self, request, context):
        print(request)

        session = self.sessions.get(request.session_id)
        if session is None:
            print("Session not found " + request.session_id)
        elif not session.in_progress:
            print("Game is not started")
        elif request.name in session.killed:
            print("You are killed")
        else:
            with session.condition:
                session.messages.append(pb2.ServerMessage(chat_message=pb2.ServerMessage.ChatMessage(name=request.name, message=request.message)))
                session.condition.notify_all()

        return pb2.SayResponse()

    def end_game(self, session):
        if session.vigilante in session.killed:
            session.messages.append(pb2.ServerMessage(game_ended_message=pb2.ServerMessage.GameEndedMessage(result=pb2.ServerMessage.GameEndedMessage.VILLAGERS)))
        elif len(session.killed) == 2:
            session.messages.append(pb2.ServerMessage(game_ended_message=pb2.ServerMessage.GameEndedMessage(result=pb2.ServerMessage.GameEndedMessage.VIGILANTE)))

    def Kill(self, request, context):
        print(request)

        session = self.sessions.get(request.session_id)
        if session is None:
            print("Session not found " + request.session_id)
        elif not session.in_progress:
            print("Game is not started")
        elif request.name in session.killed:
            print("You are killed")
        elif not session.is_day:
            if session.get_client_role(request.name) != pb2.ServerMessage.GameStartedMessage.Role.VIGILANTE:
                print("Invalid role")
            else:
                with session.condition:
                    print("Killed = " + str(request.name_to_kill))

                    session.messages.append(pb2.ServerMessage(killed_message=pb2.ServerMessage.KilledMessage(name=request.name_to_kill)))
                    session.killed.add(request.name_to_kill)

                    session.vigilante_voted = request.name_to_kill

                    self.end_game(session)

                    if session.detective in session.killed or session.investigated:
                        session.messages.append(pb2.ServerMessage(day_started_message=pb2.ServerMessage.DayStartedMessage()))
                        session.is_day = True

                    session.condition.notify_all()
        else:
            session.day_kill_votes[request.name] = request.name_to_kill
            print(request.name + " voted to kill " + request.name_to_kill)

        return pb2.KillResponse()

    def get_killed(self, session):
        candidates = {}
        for name in session.day_kill_votes.values():
            if name not in candidates:
                candidates[name] = 0
            candidates[name] = candidates[name] + 1

        print(session.day_kill_votes)
        print(candidates)

        m = 0
        candidate = None
        for k, v in candidates.items():
            if v > m:
                candidate = k
                m = v

        return candidate

    def CloseDay(self, request, context):
        print("close day")
        print(request)

        session = self.sessions.get(request.session_id)
        if session is None:
            print("Session not found " + request.session_id)
        elif not session.in_progress:
            print("Game is not started")
        elif not session.is_day:
            print("Not day")
        elif len(session.day_kill_votes) < 4 - len(session.killed) and not session.first_day:
            print("Not everyone voted, voted: " + str(len(session.day_kill_votes)) + ", killed: " + str(len(session.killed)))
        else:
            session.day_closed.add(request.name)
            if len(session.day_closed) >= 4 - len(session.killed):
                with session.condition:
                    if not session.first_day:
                        killed = self.get_killed(session)
                        print("Killed = " + str(killed))

                        session.messages.append(pb2.ServerMessage(killed_message=pb2.ServerMessage.KilledMessage(name=killed)))
                        session.killed.add(killed)

                    session.day_kill_votes = {}
                    session.is_day = False
                    session.day_closed = set()
                    session.first_day = False
                    session.investigated = None
                    session.vigilante_voted = None

                    self.end_game(session)
                    session.messages.append(pb2.ServerMessage(night_started_message=pb2.ServerMessage.NightStartedMessage()))

                    session.condition.notify_all()

        return pb2.CloseDayResponse()

    def Investigate(self, request, context):
        print(request)

        session = self.sessions.get(request.session_id)
        if session is None:
            print("Session not found " + request.session_id)
        elif not session.in_progress:
            print("Game is not started")
        elif request.name in session.killed:
            print("You are killed")
        elif session.is_day:
            print("Is not allowed during day")
        else:
            if session.get_client_role(request.name) != pb2.ServerMessage.GameStartedMessage.Role.DETECTIVE:
                print("Invalid role")
            else:
                with session.condition:
                    print("Investigated = " + str(request.name_to_investigate))

                    session.investigated = request.name_to_investigate

                    if session.vigilante_voted:
                        session.messages.append(pb2.ServerMessage(day_started_message=pb2.ServerMessage.DayStartedMessage()))
                        session.is_day = True

                    session.condition.notify_all()

        return pb2.InvestigateResponse()

    def PublishInvestigation(self, request, context):
        print(request)

        session = self.sessions.get(request.session_id)
        if session is None:
            print("Session not found " + request.session_id)
        elif not session.in_progress:
            print("Game is not started")
        elif request.name in session.killed:
            print("You are killed")
        elif not session.is_day:
            print("Is not allowed during night")
        else:
            if session.get_client_role(request.name) != pb2.ServerMessage.GameStartedMessage.Role.DETECTIVE:
                print("Invalid role")
            else:
                with session.condition:
                    print("Investigated = " + str(session.investigated))

                    if session.vigilante == session.investigated:
                        session.killed.add(session.investigated)
                        session.messages.append(pb2.ServerMessage(killed_message=pb2.ServerMessage.KilledMessage(name=session.investigated)))

                        self.end_game(session)

                        session.condition.notify_all()

        return pb2.InvestigateResponse()

    def Connect(self, request, context):
        print(request)
        session = self.find_or_create_session()
        print('session = ' + session.session_id)

        game_started = session.add_client(request.name)

        with session.condition:
            session.messages.append(pb2.ServerMessage(client_connected_message=pb2.ServerMessage.ClientConnectedMessage(name=request.name)))

            if game_started:
                session.messages.append(pb2.ServerMessage.GameStartedMessage())

            session.condition.notify_all()

        yield pb2.ServerMessage(new_session_message=pb2.ServerMessage.NewSessionMessage(session_id=session.session_id))

        messages_handled = 0
        while True:
            with session.condition:
                if len(session.messages) > messages_handled:
                    for message in session.messages[messages_handled:]:
                        if isinstance(message, pb2.ServerMessage.GameStartedMessage):
                            message = pb2.ServerMessage(game_started_message=pb2.ServerMessage.GameStartedMessage(role=session.get_client_role(request.name)))

                        print('Sending to ' + request.name + ': ' + str(message))
                        yield message
                        messages_handled += 1

                session.condition.wait()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MafiaServicer_to_server(MafiaService(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
