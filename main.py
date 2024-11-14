import time
from datetime import datetime
import difflib
from fitbit.fitbit_api import check_for_sleep  # Fitbit APIを使用して睡眠ログを取得
from discord.discord import send_to_discord    # Discord通知用の関数
from file_operations.file_operations import get_previous_logs, save_current_logs, save_sent_logs  # ログの操作関数

def main():
    """メインループ

    Fitbitからの睡眠ログを定期的に取得し、差分がある場合はDiscordに通知を送信する。
    """
    while True:
        # 現在の日付を取得（形式: YYYY-MM-DD）
        date = datetime.now().strftime('%Y-%m-%d')
        print(f"{date}の睡眠ログを取得中...")

        # 前回のログを取得し、行単位で分割
        previous_logs = get_previous_logs().splitlines()

        # Fitbit APIから新しい睡眠ログを取得
        new_logs = check_for_sleep(date)

        # 差分を計算（difflibを使用）
        diff = list(difflib.unified_diff(previous_logs, new_logs, lineterm=''))
        # 追加された行のみを抽出（差分行の先頭が '+' かつ '+++' ではないもの）
        diff = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]

        # 差分があれば通知とログの保存を実行
        if diff:
            new_diff_message = "\n".join(diff)  # 差分を1つのメッセージにまとめる
            print(new_diff_message)  # 差分をコンソールに出力
            send_to_discord(new_diff_message)  # Discordにメッセージを送信
            save_current_logs("\n".join(new_logs))  # 新しいログを保存
            save_sent_logs(new_diff_message)  # 送信したログを保存

        # 次回実行まで60秒間待機
        time.sleep(60)

if __name__ == "__main__":
    try:
        # メインループを開始
        main()
    except KeyboardInterrupt:
        # Ctrl+Cが押された場合、プログラムを終了
        print("プログラムを終了します...")
