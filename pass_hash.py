import yaml
from passlib.hash import sha512_crypt

def encrypt_password(password):
    return sha512_crypt.using(rounds=5000).hash(password)

def update_users_passwords(users_file_path):
    # Прочитать существующие данные из файла
    with open(users_file_path, 'r') as users_file:
        users_data = yaml.safe_load(users_file)

    # Шифрование и сохранение
    for user in users_data['users']:
        if 'password' in user:
            user['hash_pass'] = encrypt_password(user['password'])

    # Запись обновленных данных обратно в файл
    with open(users_file_path, 'w') as users_file:
        yaml.dump(users_data, users_file, default_flow_style=False)