# REST API

## Запуск:

```
git clone https://github.com/shelengovskaya/SOA_HW.git
cd SOA_HW/rest
docker-compose build
docker-compose up
```

## REST API

`GET /all_users` - вывод всех пользователей

`POST /add_user` - регистрация пользователя (получение jwt-token)

`POST /login` - вход (получение jwt-token)

`GET /user/{user_id}` - получить информацию о пользователе

`PATCH /user/{user_id}` - изменить информацию о себе

`DELETE /user/{user_id}` - удалить себя

`GET /user/statistics/{user_id}` - получить свою статистику

`PATCH /user/statistics/{user_id}` - изменить свою стаистику в играх

`POST /user/pdf/{user_id}` - сформировать pdf с информацией о пользователе

`GET /users/pdf/{user_id}` - получить pdf с информацией о пользователе
