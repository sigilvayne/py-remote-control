import tkinter as tk
from tkinter import messagebox
import os
import json
import subprocess
import shutil
import tempfile
import sys

CONFIG_PATH = "C:/Script/agent/config.json"
SERVICE_NAME = "AgentService"
SERVICE_EXE_NAME = "agent_service.exe"
INSTALL_DIR = "C:/Script/agent"

# Вбудований agent_service.exe
def extract_service_binary():
    temp_dir = tempfile.gettempdir()
    target_path = os.path.join(INSTALL_DIR, SERVICE_EXE_NAME)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    # agent_service.exe має бути поряд із цим .exe — або запакований в PyInstaller (див. нижче)
    shutil.copyfile(os.path.join(sys._MEIPASS, SERVICE_EXE_NAME), target_path)
    return target_path

def init_config():
    if os.path.exists(CONFIG_PATH):
        answer = messagebox.askyesno("Конфіг існує", "Бажаєте замінити конфіг файл?")
        if not answer:
            return

    def save():
        server_id = e1.get().strip()
        control_url = e2.get().strip()
        if not server_id or not control_url:
            messagebox.showerror("Помилка", "Усі поля обов’язкові!")
            return
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump({"server_id": server_id, "control_center_url": control_url}, f)
        messagebox.showinfo("Готово", "Конфігурацію збережено.")
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Налаштування агента")
    tk.Label(top, text="Server ID:").grid(row=0, column=0, padx=10, pady=5)
    e1 = tk.Entry(top, width=30)
    e1.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(top, text="Control Center URL:").grid(row=1, column=0, padx=10, pady=5)
    e2 = tk.Entry(top, width=30)
    e2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(top, text="Зберегти", command=save).grid(row=2, column=0, columnspan=2, pady=10)

def install_service():
    exe_path = extract_service_binary()

    # Створення служби
    subprocess.run(
        f'sc create {SERVICE_NAME} binPath= "{exe_path}" start= auto',
        shell=True
    )
    subprocess.run(f'sc start {SERVICE_NAME}', shell=True)
    messagebox.showinfo("Служба", "Службу встановлено та запущено.")

# ==== GUI ====
root = tk.Tk()
root.title("Agent Installer")
tk.Button(root, text="🔧 Ініціалізація конфігу", width=30, command=init_config).pack(pady=10)
tk.Button(root, text="🚀 Встановити службу", width=30, command=install_service).pack(pady=10)
tk.Button(root, text="Вихід", width=30, command=root.quit).pack(pady=10)
root.mainloop()
