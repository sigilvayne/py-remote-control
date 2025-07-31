import json
import requests
import sys
import os

CONFIG_PATH = "C:/Script/agent/config.json"

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    server_id = cfg.get("server_id")
    control_url = cfg.get("control_center_url")
    token = cfg.get("agent_token")

    if not all([server_id, control_url, token]):
        print("Config file missing required fields.")
        sys.exit(1)

    url = control_url.rstrip("/") + "/register_server"
    headers = {"X-Agent-Token": token}
    data = {
        "server_id": server_id,
        "control_center_url": control_url
    }

    try:
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code == 201:
            print("Server registered successfully.")
        elif resp.status_code == 200:
            print("Server already registered.")
        else:
            print(f"Registration failed. Status: {resp.status_code}\n{resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error during registration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 