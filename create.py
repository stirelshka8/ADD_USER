import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import os

class ServerUserEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактирование серверов и пользователей")

        # Загрузка данных
        self.server_data = self.load_data('servers.yml')
        self.users_data = self.load_data('users.yml')

        # Создание интерфейса
        self.create_server_frame()
        self.create_user_frame()
        self.create_servers_listbox()
        self.create_users_listbox()

    def load_data(self, filename):
        data = []
        if os.path.exists(filename):
            with open(filename, 'r') as data_file:
                data = yaml.safe_load(data_file) or []
        return data

    def save_data(self, filename, data):
        with open(filename, 'w') as data_file:
            yaml.dump(data, data_file, default_flow_style=False)

    def create_server_frame(self):
        self.server_frame = ttk.LabelFrame(self.root, text="Редактирование серверов")
        self.server_frame.grid(row=0, column=0, padx=10, pady=10)

        self.server_name_label = ttk.Label(self.server_frame, text="Hostname:")
        self.server_name_label.grid(row=0, column=0)

        self.server_name_var = tk.StringVar()
        self.server_name_entry = ttk.Entry(self.server_frame, textvariable=self.server_name_var)
        self.server_name_entry.grid(row=0, column=1)

        self.server_port_label = ttk.Label(self.server_frame, text="Порт:")
        self.server_port_label.grid(row=1, column=0)

        self.server_port_var = tk.StringVar()
        self.server_port_entry = ttk.Entry(self.server_frame, textvariable=self.server_port_var)
        self.server_port_entry.grid(row=1, column=1)

        self.add_server_button = ttk.Button(self.server_frame, text="Добавить сервер", command=self.save_server)
        self.add_server_button.grid(row=2, column=0, columnspan=2)

    def create_user_frame(self):
        self.user_frame = ttk.LabelFrame(self.root, text="Редактирование пользователей")
        self.user_frame.grid(row=1, column=0, padx=10, pady=10)

        self.username_label = ttk.Label(self.user_frame, text="Имя пользователя:")
        self.username_label.grid(row=0, column=0)

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.user_frame, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1)

        self.ssh_key_label = ttk.Label(self.user_frame, text="SSH ключ:")
        self.ssh_key_label.grid(row=1, column=0)

        self.ssh_key_var = tk.StringVar()
        self.ssh_key_entry = ttk.Entry(self.user_frame, textvariable=self.ssh_key_var)
        self.ssh_key_entry.grid(row=1, column=1)

        self.password_label = ttk.Label(self.user_frame, text="Пароль:")
        self.password_label.grid(row=2, column=0)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.user_frame, textvariable=self.password_var)
        self.password_entry.grid(row=2, column=1)

        self.add_user_button = ttk.Button(self.user_frame, text="Добавить пользователя", command=self.save_user)
        self.add_user_button.grid(row=3, column=0, columnspan=2)

    def create_servers_listbox(self):
        self.servers_listbox = tk.Listbox(self.server_frame, selectmode=tk.SINGLE)
        self.servers_listbox.grid(row=3, column=0, columnspan=2)
        self.servers_listbox.bind("<Delete>", self.delete_server)
        self.update_servers_listbox()

    def create_users_listbox(self):
        self.users_listbox = tk.Listbox(self.user_frame, selectmode=tk.SINGLE)
        self.users_listbox.grid(row=4, column=0, columnspan=2)
        self.users_listbox.bind("<Delete>", self.delete_user)
        self.update_users_listbox()

    def save_server(self):
        hostname = self.server_name_var.get()
        if not hostname:
            messagebox.showerror("Ошибка", "Поле 'Hostname' не может быть пустым.")
            return
        port = self.server_port_var.get() or 22
        self.server_data.append({"hostname": hostname, "port": int(port)})
        
        self.server_name_var.set("")
        self.server_port_var.set("")
        self.save_data('servers.yml', self.server_data)
        self.update_servers_listbox()

    def save_user(self):
        username = self.username_var.get()
        ssh_key = self.ssh_key_var.get()
        password = self.password_var.get()
        new_user = {"username": username, "ssh_key": ssh_key, "password": password}
        self.users_data.setdefault("users", []).append(new_user)
        self.username_var.set("")
        self.ssh_key_var.set("")
        self.password_var.set("")
        self.save_data('users.yml', self.users_data)
        self.update_users_listbox()

    def delete_server(self, event):
        selected_item = self.servers_listbox.curselection()
        if not selected_item:
            return
        index = selected_item[0]
        self.server_data.pop(index)
        self.save_data('servers.yml', self.server_data)
        self.update_servers_listbox()

    def delete_user(self, event):
        selected_item = self.users_listbox.curselection()
        if not selected_item:
            return
        index = selected_item[0]
        self.users_data.pop(index)
        self.save_data('users.yml', self.users_data)
        self.update_users_listbox()

    def update_servers_listbox(self):
        self.servers_listbox.delete(0, tk.END)
        for server in self.server_data:
            self.servers_listbox.insert(tk.END, f"Hostname: {server['hostname']}, Port: {server['port']}")

    def update_users_listbox(self):
        self.users_listbox.delete(0, tk.END)
        users = self.users_data.get("users", [])
        for user in users:
            self.users_listbox.insert(tk.END, f"Username: {user['username']}, SSH Key: {user['ssh_key']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerUserEditor(root)
    root.mainloop()