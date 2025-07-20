import os
import json
import tkinter as tk
from tkinter import messagebox
import requests
import zipfile

CONFIG_PATH = "C:/Script/agent/config.json"
TEMP_ZIP_PATH = "installer.zip"

session = requests.Session()  # Глобальна сесія з cookies

def login(control_url, username, password):
    try:
        response = session.post(control_url + "/login", data={
            "username": username,
            "password": password
        })
        if response.status_code == 200 and "Set-Cookie" in response.headers:
            return True
        elif response.status_code == 302:
            return True  # деякі Flask логіни редіректять
        else:
            messagebox.showerror("Помилка входу", f"Статус: {response.status_code}\n{response.text}")
            return False
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося увійти:\n{e}")
        return False

def download_and_extract(control_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = session.get(control_url + "/download", stream=True, headers=headers)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "zip" not in content_type.lower():
                raise Exception(f"Очікувався zip, але отримано: {content_type}")

            with open(TEMP_ZIP_PATH, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            with zipfile.ZipFile(TEMP_ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(os.getcwd())

            os.remove(TEMP_ZIP_PATH)
            messagebox.showinfo("Успіх", "Файли успішно завантажено та розпаковано.")
        else:
            messagebox.showerror("Помилка", f"Помилка при завантаженні: {response.status_code}\n{response.text}")
    except Exception as e:
        with open("debug_downloaded_content.bin", "wb") as f:
            f.write(response.content)
        messagebox.showerror("Помилка", f"Не вдалося завантажити інсталятор:\n{e}")

if not os.path.exists(CONFIG_PATH):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    def save():
        server_id = e1.get().strip()
        control_url = e2.get().strip().rstrip('/')
        username = e3.get().strip()
        password = e4.get().strip()

        if not server_id or not control_url or not username or not password:
            messagebox.showerror("Помилка", "Усі поля обов’язкові!")
            return

        # Спроба входу
        if not login(control_url, username, password):
            return

        # Збереження конфігу
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "server_id": server_id,
                "control_center_url": control_url,
                "username": username
            }, f)

        # Реєстрація сервера
        try:
            response = session.post(control_url + "/register_server", json={
                "server_id": server_id,
                "control_center_url": control_url
            })
            if response.status_code == 201:
                messagebox.showinfo("Успіх", "Сервер зареєстровано.")
            elif response.status_code == 200:
                messagebox.showinfo("Інформація", "Цей сервер вже зареєстровано.")
            else:
                messagebox.showerror("Помилка", f"Статус: {response.status_code}, Відповідь: {response.text}")
                return
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зареєструвати сервер:\n{e}")
            return

        # Завантаження та розпакування
        download_and_extract(control_url)

        root.destroy()

    # GUI
    root = tk.Tk()
    root.title("Налаштування агента")

    tk.Label(root, text="Server ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    e1 = tk.Entry(root, width=30)
    e1.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Control Center URL:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    e2 = tk.Entry(root, width=30)
    e2.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Username:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    e3 = tk.Entry(root, width=30)
    e3.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Password:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    e4 = tk.Entry(root, width=30, show="*")
    e4.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(root, text="Зберегти", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()
else:
    print("[INFO] Конфіг уже існує. Повторна ініціалізація не потрібна.")
