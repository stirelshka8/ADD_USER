from pass_hash import update_users_passwords
from write_ip import update_servers_config
from getpass import getpass
import configparser
import subprocess
import yaml
import os

# Создание объекта ConfigParser
config = configparser.ConfigParser()

# Чтение ini-файла
config.read('config/config.ini')

temp_inventory_file = config.get('FILES', 'temp_inventory_file')
file_servers = config.get('FILES', 'file_servers')
file_settnings = config.get('FILES', 'file_settnings')
file_user = config.get('FILES', 'file_user')
file_adduser = config.get('FILES', 'file_adduser')
file_ip = config.get('FILES', 'file_ip')

update_users_passwords(file_user)
update_servers_config(file_ip, file_servers)


def get_known_hosts_path():
    home_directory = os.path.expanduser("~")
    
    known_hosts_path = os.path.join(home_directory, ".ssh", "known_hosts")
    
    return known_hosts_path

def is_host_in_known_hosts(known_hosts_file, hostname):
    with open(known_hosts_file, "r") as file:
        for line in file:
            if hostname in line:
                return True
    return False

def update_known_hosts(hostname, port):
    known_hosts_file_path = get_known_hosts_path()
    
    try:
        os.makedirs(os.path.dirname(known_hosts_file_path), exist_ok=True)
        
        known_hosts_entry = subprocess.check_output(["sudo", "ssh-keyscan", "-p", str(port), hostname], text=True)

        if not is_host_in_known_hosts(known_hosts_file_path, hostname):
            with open(known_hosts_file_path, "a") as known_hosts_file:
                known_hosts_file.write(known_hosts_entry)
        else:
            print(f"Хост '{hostname}' уже находится в known_hosts. Пропуск обновления.")

    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска ssh-keyscan: {str(e)}")
    except Exception as e:
        print(f"Ошибка при добавлении ключа хоста в known_hosts: {str(e)}")


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
            temp_inventory.write(f'{hostname} ansible_ssh_port={ssh_port} ansible_ssh_host={hostname}\n')

    update_known_hosts(hostname, ssh_port)

    # Выбор авторизации
    authentication_choice = input("Выберите метод авторизации (pass/key): ").strip().lower()

    if authentication_choice not in ['pass', 'key']:
        print("Неправильный выбор авторизации. Введите 'pass' или 'key'.")
        exit(1)

    if authentication_choice == 'pass':
        password = getpass("Введите пароль для SSH-авторизации: ")

    # Чтение данных о пользователях из файла
    with open(file_user, 'r') as users_file:
        users_data = yaml.safe_load(users_file)

    # Генерация плейбука
    ansible_playbook = {
        'name': 'Add users and SSH keys',
        'hosts': 'servers',
        'become': 'yes',
        'gather_facts': 'no',
        'vars': {
            'users_data': users_data['users'],
            'ansible_ssh_pass': password if authentication_choice == 'pass' else None,
            'ansible_ssh_user': ssh_user
        },
        'tasks': []
    }

    ansible_playbook['tasks'].extend([
        {
            'name': 'Create users',
            'user': {
                'name': '{{ item.username }}',
                'createhome': 'yes',
                'shell': '/bin/bash',
                'password': '{{ item.hash_pass }}',
            },
            'loop': '{{ users_data }}',
        },
        {
            'name': 'Add SSH keys',
            'authorized_key': {
                'user': '{{ item.username }}',
                'key': '{{ item.ssh_key }}',
            },
            'loop': '{{ users_data }}',
        },
        {
            'name': 'Add users to sudo group',
            'become': 'yes',
            'become_user': 'root',
            'command': 'usermod -aG sudo {{ item.username }}',
            'loop': '{{ users_data }}',
        },
    ])

    # Сохранение плейбука в файл
    with open(file_adduser, 'w') as playbook_file:
        yaml.dump([ansible_playbook], playbook_file, default_flow_style=False)

    # Выполнение плейбука с использованием временного инвентарного файла
    subprocess.call(['ansible-playbook', '-i', temp_inventory_file, file_adduser, '-e', 'ansible_remote_tmp=/tmp'])
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
finally:
    # Удаление временных файлов
    try:
        subprocess.call(['rm', temp_inventory_file, file_adduser])
    except:
        print("А нечего удалять!")