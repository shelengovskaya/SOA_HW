## Запуск сервера:
```
sudo apt-get install -y rabbitmq-server
sudo systemctl start rabbitmq-server
pip install -r requirements.txt
python3 rpc_server.py
```
## Запуск клиента:
```
python3 rpc_client.py [url1] [url2]
```
### Пример 1:
```
python3 rpc_client.py https://en.wikipedia.org/wiki/Camel_case https://en.wikipedia.org/wiki/Tall_Man_lettering
```
Результат:
```
 [x] Requesting: https://en.wikipedia.org/wiki/Camel_case, https://en.wikipedia.org/wiki/Tall_Man_lettering
 [.] Got 1
```
### Пример 2:
```
python3 rpc_client.py https://en.wikipedia.org/wiki/Robert_de_Umfraville https://en.wikipedia.org/wiki/Order_of_chivalry
```
Результат:
```
 [x] Requesting: https://en.wikipedia.org/wiki/Robert_de_Umfraville, https://en.wikipedia.org/wiki/Order_of_chivalry
 [.] Got 2
```
