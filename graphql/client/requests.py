def request_games(finished: str):
    inp = ""
    if finished:
        inp = "(finished:{})".format(finished)
    return f"""
        {{
            games{inp} {{
                id
                finished
                score {{
                    mafia
                    citizen
                }}
                comments {{
                    author
                    content
                }}
            }}
        }}
        """

def request_game(id: str):
    return """
        {{
            game(id:{}) {{
                score {{
                    mafia
                    citizen
                }}
                comments {{
                    author
                    content
                }}
            }}
        }}
        """.format(id)

def request_game_score(id: str):
    return """
        {{
            game(id:{}) {{
                score {{
                    mafia
                    citizen
                }}
            }}
        }}
        """.format(id)

def request_add_comment(game_id: str, author: str, content: str):
    return f"""
        mutation {{
            comment(
                gameId:{game_id},comment:{{
                    author:"{author}",
                    content:"{content}",
                }}
            )
            {{
                id
                author
                content
            }}
        }}
        """