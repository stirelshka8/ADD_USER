import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import subprocess
import yaml

def execute_playbook():
    selected_servers = [server_data[i] for i in server_checkboxes if server_checkboxes[i].get() == 1]
    selected_users = [users_data['users'][i] for i in user_checkboxes if user_checkboxes[i].get() == 1]

    if not selected_servers:
        messagebox.showerror("Ошибка", "Выберите хотя бы один сервер.")
        return

    if not selected_users:
        messagebox.showerror("Ошибка", "Выберите хотя бы одного пользователя.")
        return

    try:
        temp_inventory_file = 'temp_inventory.ini'
        with open(temp_inventory_file, 'w') as temp_inventory:
            temp_inventory.write('[servers]\n')
            for server_info in selected_servers:
                hostname = server_info['hostname']
                ssh_port = server_info.get('port', 22)
                temp_inventory.write(f'{hostname} ansible_ssh_port={ssh_port} ansible_ssh_host={hostname}\n')

        if authentication_var.get() == 'pass':
            password = simpledialog.askstring("Ввод пароля", "Введите пароль для SSH-авторизации:", show='*')
        else:
            password = None

        ansible_playbook = {
            'name': 'Add users and SSH keys',
            'hosts': 'servers',
            'become': 'yes',
            'gather_facts': 'no',
            'vars': {
                'users_data': selected_users,
                'ansible_ssh_pass': password,
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

        with open('add_users.yml', 'w') as playbook_file:
            yaml.dump([ansible_playbook], playbook_file, default_flow_style=False)

        process = subprocess.Popen(['ansible-playbook', '-i', temp_inventory_file, 'add_users.yml'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        output_text.config(state=tk.NORMAL)
        output_text.delete(1.0, tk.END)
        while process.poll() is None:
            root.update_idletasks()
            line = process.stdout.readline()
            output_text.insert(tk.END, line)
            root.update_idletasks()
        output_text.config(state=tk.DISABLED)
        messagebox.showinfo("Успех", "Плейбук успешно выполнен.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Что-то пошло не так: {str(e)}")
    finally:
        subprocess.call(['rm', temp_inventory_file, 'add_users.yml'])

root = tk.Tk()
root.title("Автоматизация добавления пользователей и SSH-ключей")
root.geometry("800x600")

with open('servers.yml', 'r') as server_file:
    server_data = yaml.safe_load(server_file)

with open('users.yml', 'r') as users_file:
    users_data = yaml.safe_load(users_file)

# Создаем фрейм для выбора серверов в одной колонке
server_frame = ttk.LabelFrame(root, text="Выберите серверы")
server_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

canvas = tk.Canvas(server_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

server_scrollbar = ttk.Scrollbar(server_frame, orient="vertical", command=canvas.yview)
server_scrollbar.pack(side=tk.RIGHT, fill="y")
canvas.configure(yscrollcommand=server_scrollbar.set)

server_inner_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=server_inner_frame, anchor="nw")

server_checkboxes = {}
for i, server_info in enumerate(server_data):
    server_name = server_info['hostname']
    server_checkboxes[i] = tk.IntVar()
    ttk.Checkbutton(server_inner_frame, text=server_name, variable=server_checkboxes[i]).grid(row=i, column=0, sticky="w")

server_inner_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Создаем фрейм для выбора пользователей в нескольких колонках
user_frame = ttk.LabelFrame(root, text="Выберите пользователей")
user_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

canvas = tk.Canvas(user_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

user_scrollbar = ttk.Scrollbar(user_frame, orient="vertical", command=canvas.yview)
user_scrollbar.pack(side=tk.RIGHT, fill="y")
canvas.configure(yscrollcommand=user_scrollbar.set)

user_inner_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=user_inner_frame, anchor="nw")

user_checkboxes = {}
col = 0
for i, user_info in enumerate(users_data['users']):
    if i % 10 == 0:
        col += 1
    username = user_info['username']
    user_checkboxes[i] = tk.IntVar()
    ttk.Checkbutton(user_inner_frame, text=username, variable=user_checkboxes[i]).grid(row=i, column=col, sticky="w")

user_inner_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Фрейм для выбора метода авторизации
auth_frame = ttk.LabelFrame(root, text="Выберите метод авторизации")
auth_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

authentication_var = tk.StringVar()
authentication_var.set('pass')
ttk.Radiobutton(auth_frame, text="Пароль", variable=authentication_var, value='pass').grid(row=0, column=0)
ttk.Radiobutton(auth_frame, text="SSH-ключ", variable=authentication_var, value='key').grid(row=0, column=1)

# Кнопка для выполнения плейбука
execute_button = ttk.Button(root, text="Выполнить плейбук", command=execute_playbook)
execute_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Текстовое окно вывода
output_text = scrolledtext.ScrolledText(root, height=10, width=60)
output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
output_text.configure(font=("Courier", 12))  # Устанавливаем шрифт Courier с размером 12

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
