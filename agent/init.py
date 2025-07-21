import os
import json
import tkinter as tk
from tkinter import messagebox
import requests
import zipfile

CONFIG_PATH    = "C:/Script/agent/config.json"
TEMP_DIR      = "downloaded_binaries"
REPO          = "sigilvayne/py-remote-control"
RELEASE_TAG   = "install"  

session = requests.Session()

def verify_token(control_url, token):
    try:
        resp = session.get(control_url + "/health", headers={"X-Agent-Token": token})
        return resp.status_code == 200
    except Exception as e:
        messagebox.showerror("Помилка перевірки токена", str(e))
        return False


def download_all_assets_from_tagged_release():
    try:
        api_url = f"https://api.github.com/repos/{REPO}/releases/tags/{RELEASE_TAG}"
        resp = requests.get(api_url)
        resp.raise_for_status()
        release = resp.json()

        assets = release.get("assets", [])
        if not assets:
            raise Exception(f"У релізі з тегом '{RELEASE_TAG}' немає файлів для завантаження.")

        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        for asset in assets:
            name = asset["name"]
            download_url = asset["browser_download_url"]
            messagebox.showinfo("Завантаження", f"Завантажую файл: {name}")

            r = session.get(download_url, stream=True)
            r.raise_for_status()

            filepath = os.path.join(TEMP_DIR, name)
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            if name.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(filepath, "r") as z:
                        z.extractall(TEMP_DIR)
                    os.remove(filepath)
                except zipfile.BadZipFile:
                    messagebox.showwarning("Увага", f"Файл {name} не є валідним zip-архівом.")

        messagebox.showinfo("Успіх", f"Усі файли з релізу '{RELEASE_TAG}' завантажено та розпаковано (де можливо).")
    except Exception as e:
        messagebox.showerror("Помилка завантаження", str(e))

if not os.path.exists(CONFIG_PATH):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    def save():
        server_id   = e1.get().strip()
        control_url = e2.get().strip().rstrip('/')
        token       = e3.get().strip()

        if not all([server_id, control_url, token]):
            messagebox.showerror("Помилка", "Усі поля обов’язкові!")
            return

        if not verify_token(control_url, token):
            messagebox.showerror("Помилка", "Невірний токен або неможливо перевірити доступ")
            return

        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "server_id": server_id,
                "control_center_url": control_url,
                "agent_token": token
            }, f)

        try:
            resp = session.post(control_url + "/register_server", json={
                "server_id": server_id,
                "control_center_url": control_url
            }, headers={"X-Agent-Token": token})
            if resp.status_code == 201:
                messagebox.showinfo("Успіх", "Сервер зареєстровано.")
            elif resp.status_code == 200:
                messagebox.showinfo("Інформація", "Цей сервер вже зареєстровано.")
            else:
                messagebox.showerror("Помилка", f"Статус: {resp.status_code}\n{resp.text}")
                return
        except Exception as e:
            messagebox.showerror("Помилка реєстрації", str(e))
            return

        download_all_assets_from_tagged_release()
        root.destroy()

    root = tk.Tk()
    root.title("Налаштування агента")

    tk.Label(root, text="Server ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    e1 = tk.Entry(root, width=30); e1.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Control URL:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    e2 = tk.Entry(root, width=30); e2.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Agent Token:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    e3 = tk.Entry(root, width=30, show="*"); e3.grid(row=2, column=1, padx=10, pady=5)

    tk.Button(root, text="Зберегти", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()

else:
    print("[INFO] Конфіг уже існує. Повторна ініціалізація не потрібна.")
