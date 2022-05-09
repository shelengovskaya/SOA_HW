FROM python:3.7

WORKDIR /usr/src/app

EXPOSE 8000

RUN pip install 'strawberry-graphql[debug-server]'

COPY server.py ./

CMD [ "strawberry", "server", "server" ]