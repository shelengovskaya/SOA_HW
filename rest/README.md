# REST API

## Запуск:

```
git clone https://github.com/shelengovskaya/SOA_HW.git
cd rest
docker-compose build
docker-compose up
```

## REST API

`GET /users` - вывод всех пользователей

`POST /users` - регистрация пользователя (получение jwt-token)

`POST /login` - вход (получение jwt-token)

`GET /users/{user_id}` - получить информацию о пользователе

`PATCH/PUT /users/{user_id}` - изменить информацию о себе

`DELETE /users/{user_id}` - удалить себя

`GET /users/{user_id}/stats` - получить свою статистику

`PATCH/PUT /users/{user_id}/stats` - изменить свою стаистику в играх

`POST /users/{user_id}/pdf` - сформировать pdf с информацией о пользователе

`GET /users/{user_id}/pdf` - получить pdf с информацией о пользователе
