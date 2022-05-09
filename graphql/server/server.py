import typing
from typing import List
import strawberry
from strawberry.scalars import ID


@strawberry.type
class Score:
    id: ID
    mafia: int
    citizen: int


@strawberry.type
class Comment:
    id: ID
    author: str
    content: str


@strawberry.input
class CommentInput:
    author: str
    content: str


@strawberry.type
class Game:
    id: ID
    score: Score
    finished: bool
    comments: List[Comment]

# default info

gameDict: typing.Dict[int or ID, Game] = {
    0: Game(id=0, finished=True, score=Score(id=0, mafia=5, citizen=5),
            comments=[Comment(id=0, author='Player1', content='Good game!!!!'),
                Comment(id=1, author='Player2', content='Beautiful game!!!!'),]),
    1: Game(id=1, finished=True, score=Score(id=1, mafia=2, citizen=1),
            comments=[Comment(id=0, author='Player2', content='lalala'),
                Comment(id=1, author='Player3', content='(((((')]),
    2: Game(id=2, finished=False, score=Score(id=2, mafia=8, citizen=2),
            comments=[]),
}


@strawberry.type
class Query:
    @strawberry.field
    def games(self, finished: typing.Optional[bool] = None) -> List[Game]:
        if finished is not None:
            return list(filter(lambda game: game.finished == finished, gameDict.values()))
        else:
            return list(gameDict.values())

    @strawberry.field
    def game(self, id: int) -> Game:
        return gameDict[id]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def comment(self, gameId: int, comment: CommentInput) -> Comment:
        max_id = max([comment.id for g in gameDict.values() for comment in g.comments])
        newComment = Comment(id=int(max_id) + 1, author=comment.author, content=comment.content)
        gameDict[gameId].comments.append(newComment)
        return newComment


schema = strawberry.Schema(query=Query, mutation=Mutation)
f = open("schema.graphql", "w+")
f.write(schema.as_str())
f.close()
print(schema)
