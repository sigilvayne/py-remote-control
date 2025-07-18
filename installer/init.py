import os
import json
import tkinter as tk
from tkinter import messagebox
import requests

CONFIG_PATH = "C:/Script/agent/config.json"

if not os.path.exists(CONFIG_PATH):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    def save():
        server_id = e1.get().strip()
        control_url = e2.get().strip()
        if not server_id or not control_url:
            messagebox.showerror("Помилка", "Усі поля обов’язкові!")
            return
        # Збереження конфігу
        with open(CONFIG_PATH, "w") as f:
            json.dump({"server_id": server_id, "control_center_url": control_url}, f)
        
        # Спроба відправки POST-запиту на реєстрацію
        try:
            response = requests.post(control_url + "/register_server", json={
                "server_id": server_id,
                "control_center_url": control_url
            })
            if response.status_code == 201:
                messagebox.showinfo("Успіх", "Сервер зареєстровано.")
            elif response.status_code == 200:
                messagebox.showinfo("Інформація", "Цей сервер вже зареєстровано.")
            else:
                messagebox.showerror("Помилка", f"Статус: {response.status_code}, Відповідь: {response.text}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зареєструвати сервер:\n{e}")

        root.destroy()

    root = tk.Tk()
    root.title("Налаштування агента")
    tk.Label(root, text="Server ID:").grid(row=0, column=0, padx=10, pady=5)
    e1 = tk.Entry(root, width=30)
    e1.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(root, text="Control Center URL:").grid(row=1, column=0, padx=10, pady=5)
    e2 = tk.Entry(root, width=30)
    e2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Зберегти", command=save).grid(row=2, column=0, columnspan=2, pady=10)
    root.mainloop()

else:
    print("[INFO] Конфіг уже існує. Повторна ініціалізація не потрібна.")
