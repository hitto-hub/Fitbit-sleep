import os
from datetime import datetime

# ログファイルのパスを定義
PREVIOUS_LOG_FILE = "./previous_logs.txt"      # 前回取得したログを保存するファイル
SENT_LOG_FILE = "./sent_logs.txt"              # 送信済みのログを保存するファイル
LAST_FETCH_TIME_FILE = "./last_fetch_time.txt" # 最終取得日時を保存するファイル

def get_previous_logs():
    """
    前回取得したログをファイルから読み込む関数

    :return: 前回のログデータ（文字列）。ファイルが存在しない場合は空文字列を返す。
    """
    if not os.path.exists(PREVIOUS_LOG_FILE):
        return ""  # ファイルが存在しない場合は空文字列を返す
    with open(PREVIOUS_LOG_FILE, 'r') as file:
        return file.read()  # ファイルからデータを読み込み、文字列として返す

def get_sent_logs():
    """
    送信済みのログをファイルから読み込む関数

    :return: 送信済みログデータ（文字列）。ファイルが存在しない場合は空文字列を返す。
    """
    if not os.path.exists(SENT_LOG_FILE):
        return ""  # ファイルが存在しない場合は空文字列を返す
    with open(SENT_LOG_FILE, 'r') as file:
        return file.read()  # ファイルからデータを読み込み、文字列として返す

def save_current_logs(logs):
    """
    現在のログをファイルに保存する関数

    :param logs: 保存するログデータ（文字列）
    """
    with open(PREVIOUS_LOG_FILE, 'w') as file:
        file.write(logs)  # ファイルにログデータを書き込む

def save_sent_logs(logs):
    """
    送信済みのログをファイルに保存する関数

    :param logs: 保存するログデータ（文字列）
    """
    with open(SENT_LOG_FILE, 'w') as file:
        file.write(logs)  # ファイルに送信済みログデータを書き込む

def get_last_fetch_time():
    """
    最後にデータを取得した日時を読み込む関数

    :return: 最後の取得日時（文字列）。ファイルが存在しない場合は空文字列を返す。
    """
    if not os.path.exists(LAST_FETCH_TIME_FILE):
        return ""  # ファイルが存在しない場合は空文字列を返す
    with open(LAST_FETCH_TIME_FILE, 'r') as file:
        return file.read().strip()  # ファイルから日時を読み込み、前後の空白を削除して返す

def save_last_fetch_time(fetch_time=None):
    """
    最後にデータを取得した日時をファイルに保存する関数

    :param fetch_time: 保存する日時（文字列、デフォルトは現在日時）
    """
    # fetch_timeが指定されていない場合、現在の日時を使用
    if fetch_time is None:
        fetch_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    with open(LAST_FETCH_TIME_FILE, 'w') as file:
        file.write(fetch_time)  # ファイルに日時を書き込む
