import os

PREVIOUS_LOG_FILE = "./previous_logs.txt"
SENT_LOG_FILE = "./sent_logs.txt"

def get_previous_logs():
    if not os.path.exists(PREVIOUS_LOG_FILE):
        return ""
    with open(PREVIOUS_LOG_FILE, 'r') as file:
        return file.read()

def get_sent_logs():
    if not os.path.exists(SENT_LOG_FILE):
        return ""
    with open(SENT_LOG_FILE, 'r') as file:
        return file.read()

def save_current_logs(logs):
    with open(PREVIOUS_LOG_FILE, 'w') as file:
        file.write(logs)

def save_sent_logs(logs):
    with open(SENT_LOG_FILE, 'w') as file:
        file.write(logs)
