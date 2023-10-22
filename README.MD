## Инструкция

В файле server.yml в формате:

``` bash
- hostname: admlab.ddns.net
  port: 1522
- hostname: 192.168.1.111
```
прописать сервера на которых необходимо выполнить добавление пользователей. Если не указать порт то будет использован стандартный.

В файле users.yml в формате:

``` bash
users:
  - username: user1
    password: user1password
    ssh_key: ssh-rsa AAAA1234...
  - username: user2
    password: user2password
    ssh_key: ssh-rsa BBBB5678...
```
необходимо добавить пользователей и их публичные ssh ключи.

При запуске необходимо выбрать метод авторизации (ssh ключ или пароль).

## Установка и запуск

Используемые модули стандартные и есть в python из коробки, ничего ставить не нужно.

Запускать командой:

``` python
sudo python3 add_user.py
```