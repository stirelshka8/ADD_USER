# Открываем файл с IP-адресами для чтения
with open('ip_addresses.txt', 'r') as ip_file:
    ip_addresses = ip_file.readlines()

# Открываем файл 'servers.yml' для записи
with open('servers.yml', 'w') as yml_file:
    for ip in ip_addresses:
        ip = ip.strip()  # Удаляем лишние пробелы и символы новой строки
        if not ip:
            continue  # Пропускаем пустые строки, если они есть
        # Разделяем IP-адрес и порт по символу ':', если порт не указан, присваиваем 22 по умолчанию
        parts = ip.split(':')
        hostname = parts[0]
        port = parts[1] if len(parts) > 1 else '22'
        server_entry = f'- hostname: {hostname}\n  port: {port}\n'
        yml_file.write(server_entry)

print("Готово! Данные были добавлены в servers.yml и удалены из ip_addresses.txt")
