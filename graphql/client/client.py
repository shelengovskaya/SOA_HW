from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
import argparse
import sys
import json
from pygments import highlight, lexers, formatters

from requests import request_games, request_game, request_game_score, request_add_comment

ENDPOINT = "http://localhost:8000"


def main():

    transport = AIOHTTPTransport(url=ENDPOINT)

    client = Client(transport=transport, fetch_schema_from_transport=True)

    name = sys.argv[1]
    print('Hello, {}'.format(name))

    try:
        while True:
            command = input()

            parts = command.split(' ')

            if parts[0] == "all" and parts[1] == "games":
                query = gql(request_games(None))
            elif parts[0] == "games":
                if parts[1] == 'finished':
                    finished = 'true'
                elif parts[1] == 'unfinished':
                    finished = 'false'
                else:
                    print('Bad command!')
                    continue
                query = gql(request_games(finished))
            elif parts[0] == "game":
                id = parts[1]
                if len(parts) < 3:
                    query = gql(request_game(id))
                elif parts[2] == 'score':
                    query = gql(request_game_score(id))
                else:
                    print('Bad command!')
                    continue
            elif parts[0] == "add" and parts[1] == 'comment':
                id = parts[2]
                comment = ' '.join(parts[3:])
                query = gql(request_add_comment(id, name, comment))
            elif parts[0] == 'exit':
                print("Good day!")
                return
            else:
                print('Bad command!')
                continue

            result = client.execute(query)

            formatted_json = json.dumps(result, indent=4)
            colorful_json = highlight(formatted_json.encode('UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
            print(colorful_json)

    except KeyboardInterrupt:
        print("\nGood day!")
        return


if __name__ == '__main__':
    main()