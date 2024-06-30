import json
import time
from requests import Session
from pprint import pprint
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import difflib

# .envファイルを読み込む
load_dotenv()

# 初期化
session = Session()

# 認証情報の読み込み
with open("./test_conf.json", "r", encoding="utf-8") as f:
    conf = json.load(f)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PREVIOUS_LOG_FILE = "./previous_logs.txt"
SENT_LOG_FILE = "./sent_logs.txt"

def bearer_header():
    """Bearer認証用ヘッダを生成"""
    return {"Authorization": "Bearer " + conf["access_token"]}

def refresh():
    """access_tokenを再取得し、conf.jsonを更新"""
    url = "https://api.fitbit.com/oauth2/token"
    params = {
        "grant_type": "refresh_token",
        "refresh_token": conf["refresh_token"],
        "client_id": conf["client_id"],
    }
    res = session.post(url, data=params)
    res_data = res.json()
    if res_data.get("errors"):
        print(res_data["errors"][0])
        return
    conf["access_token"] = res_data["access_token"]
    conf["refresh_token"] = res_data["refresh_token"]
    with open("./test_conf.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

def is_expired(res_obj):
    """トークンの失効をチェック"""
    errors = res_obj.get("errors")
    if not errors:
        return False
    for err in errors:
        if err.get("errorType") == "expired_token":
            pprint("TOKEN_EXPIRED!!!")
            return True
    return False

def request(method, url, **kw):
    """リクエスト実行関数"""
    res = method(url, **kw)
    res_data = res.json()
    # pprint(res_data)  # レスポンスを表示
    if is_expired(res_data):
        refresh()
        kw["headers"] = bearer_header()
        res = method(url, **kw)
    return res

def get_sleep_log_by_date(date="today"):
    """指定日の睡眠ログを取得"""
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
    headers = bearer_header()
    res = request(session.get, url, headers=headers)
    return res

def send_to_discord(message):
    """DiscordのWebhookにメッセージを送信"""
    data = {"content": message}
    response = session.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"メッセージの送信に失敗しました: {response.status_code}, {response.text}")
    else:
        print("メッセージが正常に送信されました")

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

def check_for_sleep(date="today"):
    """指定日の睡眠ログをチェックし、睡眠の開始・終了をアラート表示およびDiscord通知"""
    res = get_sleep_log_by_date(date)
    data = res.json()
    new_logs = []
    if data.get("sleep"):
        for sleep_log in data["sleep"]:
            previous_level = None
            for entry in sleep_log["levels"]["data"]:
                if previous_level == "wake" and entry["level"] in ["light", "deep", "rem"]:
                    message = f"Alert: Sleep started at {entry['dateTime']}"
                    new_logs.append(message)
                elif previous_level in ["light", "deep", "rem"] and entry["level"] == "wake":
                    message = f"Alert: Sleep ended at {entry['dateTime']}"
                    new_logs.append(message)
                previous_level = entry["level"]
    else:
        print(f"No sleep detected on {date}")
    return new_logs

def main():
    """メインループ"""
    while True:
        end_date = datetime.now().strftime('%Y-%m-%d')
        previous_logs = get_previous_logs().splitlines()
        new_logs = check_for_sleep(end_date)
        diff = list(difflib.unified_diff(previous_logs, new_logs, lineterm=''))
        diff = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]

        if diff:
            new_diff_message = "\n".join(diff)
            print(new_diff_message)
            send_to_discord(new_diff_message)
            save_current_logs("\n".join(new_logs))
            save_sent_logs(new_diff_message)
        
        time.sleep(60)

if __name__ == "__main__":
    main()
