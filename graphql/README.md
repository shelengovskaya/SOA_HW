# GraphQL Python Mafia game

### Запуск сервера

`docker run -p 8000:8000 shellizaveta/graphql-mafia-server`

или

`cd server
docker build -t graphql-mafia-server .
docker run -p 8000:8000 graphql-mafia-server`

### Запуск клиента

`cd client
pip install -r requirements.txt
python3 client.py "<YOUR_NAME>"`

### Команды

'all games' - вывести все игры
'games finished' - вывести все законченные игры
'games unfinished' - вывести все незаконченные игры
'game <id>' - получить всю информацию об игре
'game <id> score' - получить счет игры
'add comment <id> <comment>' - добавить комментарий к игре
'exit' or Ctrl^C - выйти из программы

### Посмотреть пример работы через bash

`cat example.txt`

### При разработке использовались:
+ https://github.com/graphql-python/gql
+ https://github.com/strawberry-graphql/strawberry