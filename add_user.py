from getpass import getpass
import pass_hash
import subprocess
import yaml

try:
    # Чтение данных о серверах из файла YAML
    with open('servers.yml', 'r') as server_file:
        server_data = yaml.safe_load(server_file)

    # Генерация временного инвентарного файла
    temp_inventory_file = 'temp_inventory.ini'
    with open(temp_inventory_file, 'w') as temp_inventory:
        temp_inventory.write('[servers]\n')
        for server_info in server_data:
            hostname = server_info['hostname']
            ssh_port = server_info.get('port', 22)  # По умолчанию используется порт 22, если не указан другой
            temp_inventory.write(f'{hostname} ansible_ssh_port={ssh_port} ansible_ssh_host={hostname}\n')

    # Выбор авторизации
    authentication_choice = input("Выберите метод авторизации (pass/key): ").strip().lower()

    if authentication_choice not in ['pass', 'key']:
        print("Неправильный выбор авторизации. Введите 'pass' или 'key'.")
        exit(1)

    if authentication_choice == 'pass':
        password = getpass("Введите пароль для SSH-авторизации: ")

    # Чтение данных о пользователях из файла
    with open('users.yml', 'r') as users_file:
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
        },
        'tasks': [
            {
                'name': 'Create users',
                'user': {
                    'name': '{{ item.username }}',
                    'createhome': 'yes',
                    'shell': '/bin/bash',
                    'password': '{{ item.hash_pass  }}',
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
                'user': {
                    'name': '{{ item.username }}',
                    'groups': 'sudo',
                },
                'loop': '{{ users_data }}',
            },
        ],
    }

    # Сохранение плейбука в файл
    with open('add_users.yml', 'w') as playbook_file:
        yaml.dump([ansible_playbook], playbook_file, default_flow_style=False)

    # Выполнение плейбука с использованием временного инвентарного файла
    subprocess.call(['ansible-playbook', '-i', temp_inventory_file, 'add_users.yml'])
except:
    print("\n\n\nЧто то пошло не так, что конкретно хз...\n\n\n")
finally:
    # Удаление временных файлов
    subprocess.call(['rm', temp_inventory_file, 'add_users.yml'])
