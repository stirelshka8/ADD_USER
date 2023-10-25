from getpass import getpass
import configparser
import subprocess
import yaml

# Создание объекта ConfigParser
config = configparser.ConfigParser()

# Чтение ini-файла
config.read('config/config.ini')

temp_inventory_file = config.get('FILES', 'temp_inventory_file_del')
file_servers = config.get('FILES', 'file_servers')
file_settnings = config.get('FILES', 'file_settnings')
file_deluser = config.get('FILES', 'file_deluser')

try:
    # Чтение данных о серверах из файла YAML
    with open(file_servers, 'r') as server_file:
        server_data = yaml.safe_load(server_file)

    # Чтение настроек из файла YAML
    with open(file_settnings, 'r') as settings_file:
        settings_data = yaml.safe_load(settings_file)
        ssh_user = settings_data['ssh_user']

    # Генерация временного инвентарного файла
    with open(temp_inventory_file, 'w') as temp_inventory:
        temp_inventory.write('[servers]\n')
        for server_info in server_data:
            hostname = server_info['hostname']
            ssh_port = server_info.get('port', 22)  # По умолчанию используется порт 22, если не указан другой
            temp_inventory.write(f'{hostname} ansible_ssh_port={ssh_port} ansible_ssh_user={ssh_user}\n')

    # Выбор авторизации
    authentication_choice = input("Выберите метод авторизации (pass/key): ").strip().lower()

    if authentication_choice not in ['pass', 'key']:
        print("Неправильный выбор авторизации. Введите 'pass' или 'key'.")
        exit(1)

    if authentication_choice == 'pass':
        password = getpass("Введите пароль для SSH-авторизации: ")

    # Генерация плейбука для удаления всех пользователей, кроме текущего пользователя
    ansible_playbook = {
        'name': 'Remove all users except the current user',
        'hosts': 'servers',
        'become': 'yes',
        'gather_facts': 'no',
        'vars': {
            'ansible_ssh_pass': password if authentication_choice == 'pass' else None,
            'ansible_ssh_user': ssh_user,
            'current_user': ssh_user,
        },
        'tasks': [
            {
                'name': 'Remove all users except the current user',
                'shell': 'for user in $(getent passwd | cut -d: -f1); do if [ "$user" != "{{ current_user }}" ] && [ "$user" != "root" ] && [ -d /home/$user ]; then userdel -r $user || true; fi; done',
            },
        ],
    }

    # Сохранение плейбука в файл
    with open(file_deluser, 'w') as playbook_file:
        yaml.dump([ansible_playbook], playbook_file, default_flow_style=False)

    # Выполнение плейбука с использованием временного инвентарного файла
    subprocess.call(['ansible-playbook', '-i', temp_inventory_file, file_deluser])

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
finally:
    # Удаление временных файлов
    try:
        subprocess.call(['rm', temp_inventory_file, file_deluser])
    except:
        print("А нечего удалять!")
