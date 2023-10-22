## Инструкция

В файле server.yml в формате:

``` bash
- hostname: admlib.ddns.net
  port: 1522
- hostname: 192.168.1.111
```
прописать сервера на которых необходимо выполнить добавление пользователей. Если не указать порт то будет использован стандартный.

В файле users.yml в формате:

``` bash
users:
  - username: user1
    password: "user1password"
    ssh_key: ssh-rsa AAAA1234...
  - username: user2
    password: "user2password"
    ssh_key: ssh-rsa BBBB5678...
```
необходимо добавить пользователей и их публичные ssh ключи. Пароль в ОБЯЗАТЕЛЬНОМ порядке в ковычках.
После запуска в файле появится поле hash_pass с зашифрованным паролем. При каждом запуске будет обновлятся.

При запуске необходимо выбрать метод авторизации (ssh ключ или пароль).

## Установка и запуск

Создание виртуального окружения:
``` sh
python3 -m venv venv
```

Активация:

``` sh
source venv/bin/activate
```

Деактивация:

``` sh
deactivate
```

Установка зависимостей:

``` python
pip install -r req.txt
```


Запускать командой:

``` python
sudo python3 add_user.py
```