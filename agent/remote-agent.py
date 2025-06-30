import time
import requests
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

def poll_commands(server_id, control_center_url):
    while True:
        try:
            resp = requests.get(f"{control_center_url}/get_command/{server_id}")
            data = resp.json()
            if "command" in data:
                print(f"Отримано команду: {data['command']}")
                result = subprocess.run(
                    data["command"], shell=True,
                    capture_output=True, text=True
                )
                payload = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "code": result.returncode
                }
                requests.post(f"{control_center_url}/post_result/{server_id}", json=payload)
                print("Результат відправлено")
            else:
                print("Немає нових команд")
        except Exception as e:
            print(f"Помилка: {e}")
        time.sleep(5)

def start_polling():
    server_id = entry_server_id.get().strip()
    control_center_url = entry_control_url.get().strip()

    if not server_id or not control_center_url:
        messagebox.showerror("Помилка", "Будь ласка, заповніть обидва поля.")
        return

    # Ховаємо вікно GUI після введення
    root.withdraw()

    # Запускаємо командний цикл у окремому потоці
    threading.Thread(target=poll_commands, args=(server_id, control_center_url), daemon=True).start()

# Інтерфейс користувача
root = tk.Tk()
root.title("Налаштування сервера")

tk.Label(root, text="Server ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_server_id = tk.Entry(root, width=30)
entry_server_id.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Control Center URL:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_control_url = tk.Entry(root, width=30)
entry_control_url.grid(row=1, column=1, padx=10, pady=5)

btn_start = tk.Button(root, text="OK", command=start_polling)
btn_start.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
