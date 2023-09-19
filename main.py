# Импорт библиотек | Importing libraries
import paramiko # PIP, SSH
import os #files
import subprocess #cmd

# Выполнение команд на удаленном хосте | Executing commands on a remote host
def executeCommandOnRemoteHost(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8')

# Получение информации о накопителях | Getting information about drives
def getStorageInformation(host, username, password):
    try:
        # Создание SSH подключения | Creating an SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)
        
        # Получение данных о накопителях | Obtaining data about drives
        lsblk_output = executeCommandOnRemoteHost(client, 'lsblk -o NAME,SIZE,MODEL --noheadings')

        # Запись полученных данных | Recording received data
        storageInfo = []
        for line in lsblk_output.strip().split('\n'):
            values = line.split()
            if len(values) >= 2:
                name = values[0]
                size = values[1]
                model = " ".join(values[2:]) if len(values) > 2 else ""
                storageInfo.append({
                    'Name': name,
                    'Size': size,
                    'Model': model
                })
            else:
                print(f"Неверный формат записи: {line}")

        return storageInfo
    # Вывод ошибки | Error output
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    # Завершение SSH подключения | Ending the SSH connection
    finally:
        client.close()
# Отображение полученнх данных | Display of received data
def displayStorageList(storageInfo):
    tempFile = "/tmp/selected_storage.txt" 
    with open(tempFile, "w") as file:
        for device in storageInfo:
            result = subprocess.run([
                "zenity", "--list", "--width=600", "--height=400", "--title=Выберите накопитель",
                "--text", f"Имя накопителя: {str(device['Name'])}\nОбъём: {str(device['Size'])}\nМодель: {str(device['Model'])}",
                "--column=Выбор",
                "Выбрать",
                "Пропустить"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                selected_option = result.stdout.decode().strip()
                if selected_option == "Выбрать":
                    file.write(f"Имя накопителя: {device['Name']}\nОбъём: {device['Size']}\nМодель: {device['Model']}\n\n")

    
def main():
    host = input("Введите ip адресс удаленного компьютера в формате 192.168.0.0: ")
    username = input("Введите имя пользователя: ")
    password = input('Введите пароль: ')
    storageInfo = getStorageInformation(host, username, password)
    if storageInfo:
        print("Информация о накопителях на удаленном компьютере:")
        for device in storageInfo:
            print(f"Имя накопителя: {device['Name']}")
            print(f"Объем: {device['Size']}")
            print(f"Модель: {device['Model']}")
            print()
        displayStorageList(storageInfo)
        print("Список выбранных дисков сохранен в /tmp/selected_storage.txt")

if __name__ == "__main__":
    main()

