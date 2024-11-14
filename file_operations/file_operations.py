import os

# ログファイルのパスを定義
PREVIOUS_LOG_FILE = "./previous_logs.txt"  # 前回取得したログを保存するファイル
SENT_LOG_FILE = "./sent_logs.txt"          # 送信済みのログを保存するファイル

def get_previous_logs():
    """
    前回取得したログをファイルから読み込む関数

    :return: 前回のログデータ（文字列）。ファイルが存在しない場合は空文字列を返す。
    """
    if not os.path.exists(PREVIOUS_LOG_FILE):
        # ファイルが存在しない場合は空文字列を返す
        return ""
    with open(PREVIOUS_LOG_FILE, 'r') as file:
        # ファイルからデータを読み込み、文字列として返す
        return file.read()

def get_sent_logs():
    """
    送信済みのログをファイルから読み込む関数

    :return: 送信済みログデータ（文字列）。ファイルが存在しない場合は空文字列を返す。
    """
    if not os.path.exists(SENT_LOG_FILE):
        # ファイルが存在しない場合は空文字列を返す
        return ""
    with open(SENT_LOG_FILE, 'r') as file:
        # ファイルからデータを読み込み、文字列として返す
        return file.read()

def save_current_logs(logs):
    """
    現在のログをファイルに保存する関数

    :param logs: 保存するログデータ（文字列）
    """
    with open(PREVIOUS_LOG_FILE, 'w') as file:
        # ファイルにログデータを書き込む
        file.write(logs)

def save_sent_logs(logs):
    """
    送信済みのログをファイルに保存する関数

    :param logs: 保存するログデータ（文字列）
    """
    with open(SENT_LOG_FILE, 'w') as file:
        # ファイルに送信済みログデータを書き込む
        file.write(logs)
