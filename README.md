# memo

150req/1h

アクセス・トークン8時間で失効。

失効時はリフレッシュ・トークンを使って再取得が必要。

[リフレッシュ・トークンのdocs](https://dev.fitbit.com/build/reference/web-api/authorization/refresh-token/)

- Get Sleep Log by Date: 指定した日の睡眠ログエントリを取得します。
- Get Sleep Log by Date Range: 指定した期間の睡眠ログエントリを取得します。
- Get Sleep Log List: 指定した日付前後の睡眠ログエントリのリストを取得します。

## Directory Structure

- `auth/`: Contains authentication related functions.
- `fitbit/`: Contains functions to interact with the Fitbit API.
- `discord/`: Contains functions to send messages to Discord.
- `file_operations/`: Contains functions to handle file operations.
- `config/`: Contains configuration files.
- `main.py`: Main entry point of the application.
- `.env`: Environment variables.
- `requirements.txt`: Python dependencies.

## de

認証情報の読み込み:

./test_conf.json ファイルから認証情報（client_id, access_token, refresh_token）を読み込みます。
Bearer認証ヘッダの生成:

bearer_header 関数で、リクエストヘッダに Authorization: Bearer {access_token} を設定します。
アクセストークンのリフレッシュ:

refresh 関数で、トークンが失効した際に新しい access_token と refresh_token を取得し、test_conf.json ファイルを更新します。
トークン失効のチェック:

is_expired 関数で、レスポンスからトークンの失効を確認します。
リクエスト実行関数:

request 関数で、リクエストを実行し、必要に応じてトークンをリフレッシュして再リクエストします。
指定日の睡眠ログ取得:

get_sleep_log_by_date 関数で、指定日の睡眠ログをFitbit APIから取得します。
睡眠の開始・終了のチェック:

check_for_sleep 関数で、指定日の睡眠ログをチェックし、睡眠の開始（"wake"から"asleep"）と終了（"asleep"から"wake"）時にアラートを表示します。
1分ごとに実行するループ:

while True ループで、毎分指定日の睡眠ログをチェックし、アラートを表示します。
このコードは、Fitbit APIを使って睡眠ログを監視し、睡眠の開始と終了をリアルタイムで検知してアラートを表示するシステムを構築します。

(venv) hitto@hitto:~/Fitbit-sleep$ tree
.
├── README.md
├── auth
│   └── auth.py
├── config
│   └── test_conf.json
├── discord
│   └── discord.py
├── file_operations
│   └── file_operations.py
├── fitbit
│   └── fitbit_api.py
├── main.py
└── requirements.txt

5 directories, 8 files

```auth/auth.py```:

```python
import json
import os
from requests import Session

session = Session()

def load_conf():
    with open("./config/test_conf.json", "r", encoding="utf-8") as f:
        return json.load(f)

conf = load_conf()

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
    with open("./config/test_conf.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

def is_expired(res_obj):
    """トークンの失効をチェック"""
    errors = res_obj.get("errors")
    if not errors:
        return False
    for err in errors:
        if err.get("errorType") == "expired_token":
            print("TOKEN_EXPIRED!!!")
            return True
    return False

def request(method, url, **kw):
    """リクエスト実行関数"""
    res = method(url, **kw)
    res_data = res.json()
    if is_expired(res_data):
        refresh()
        kw["headers"] = bearer_header()
        res = method(url, **kw)
    return res
```

```fitbit/fitbit_api.py```:

```python
from datetime import datetime, timedelta
from auth.auth import session, request, bearer_header

# Note: This function is not used in the main.py file
def get_sleep_log_by_date(date="today"):
    """指定日の睡眠ログを取得"""
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
    headers = bearer_header()
    res = request(session.get, url, headers=headers)
    return res

def get_sleep_log_list(after_date=None, before_date=None, sort="asc", limit=100, offset=0):
    """
    Fitbit APIから睡眠ログリストを取得する

    :param after_date: 開始日の指定 (例: '2020-05-01')
    :param before_date: 終了日の指定 (例: '2020-06-01')
    :param sort: ソート順 ('asc' または 'desc')
    :param limit: 取得するログの数
    :param offset: オフセット
    :return: 睡眠ログのリスト
    """
    print(f"Getting sleep logs from {after_date} to {before_date}")
    base_url = "https://api.fitbit.com/1.2/user/-/sleep/list.json"
    params = {
        "sort": sort,
        "limit": limit,
        "offset": offset
    }

    if after_date:
        params["afterDate"] = after_date
    if before_date:
        params["beforeDate"] = before_date

    headers = bearer_header()
    res = request(session.get, base_url, headers=headers, params=params)
    return res

def check_for_sleep(date=None):
    """指定日の睡眠ログをチェックし、睡眠の開始・終了をアラート表示およびDiscord通知"""
    print(f"Checking for sleep on {date}")
    res = get_sleep_log_list(after_date=(datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d"))
    data = res.json()
    print(data)
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
```

```discord/discord.py```:

```python
import os
from requests import Session

session = Session()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_to_discord(message):
    """DiscordのWebhookにメッセージを送信"""
    print(f"webhook url: {WEBHOOK_URL}")
    data = {"content": message}
    response = session.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"メッセージの送信に失敗しました: {response.status_code}, {response.text}")
    else:
        print("メッセージが正常に送信されました")
```

```file_operations/file_operations.py```:

```python
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
```

```main.py```:

```python
import time
from datetime import datetime
import difflib
from fitbit.fitbit_api import check_for_sleep
from discord.discord import send_to_discord
from file_operations.file_operations import get_previous_logs, save_current_logs, save_sent_logs

def main():
    """メインループ"""
    while True:
        date = datetime.now().strftime('%Y-%m-%d')
        previous_logs = get_previous_logs().splitlines()
        new_logs = check_for_sleep(date)
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
    try:
        main()
    except KeyboardInterrupt:
        print("プログラムを終了します...")
```

```config/test_conf.json```:

```json
{
    "client_id": "YOUR
    "access_token : "YOUR_ACCESS
    "refresh_token : "YOUR_REFRESH
}
```

```.env```:

```env
WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL
```
