import time
from datetime import datetime, timedelta
import difflib
from fitbit.fitbit_api import check_for_sleep
from discord.discord import send_to_discord
from file_operations.file_operations import get_previous_logs, save_current_logs, save_sent_logs, get_last_fetch_time, save_last_fetch_time

def calculate_diff(previous_logs, new_logs):
    """
    2つのログリスト間の差分を計算する関数

    :param previous_logs: 前回のログ（リスト形式）
    :param new_logs: 新しいログ（リスト形式）
    :return: 差分ログ（リスト形式）
    """
    diff = list(difflib.unified_diff(previous_logs, new_logs, lineterm=''))
    return [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]

def main():
    """メインループ
    Fitbitからの睡眠ログを定期的に取得し、差分がある場合はDiscordに通知を送信する。
    """
    while True:
        try:
            # 前回の最終取得日時を取得
            last_fetch_time = get_last_fetch_time()
            if not last_fetch_time:
                # 初回実行の場合は1日前を基準にする
                last_fetch_time = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')

            print(f"{last_fetch_time} 以降の睡眠ログを取得中...")

            # Fitbit APIから新しい睡眠ログを取得
            new_logs = check_for_sleep(last_fetch_time)

            if new_logs:
                previous_logs = get_previous_logs().splitlines()
                diff = calculate_diff(previous_logs, new_logs)

                if diff:
                    new_diff_message = "\n".join(diff)
                    print(new_diff_message)
                    send_to_discord(new_diff_message)  # 差分をDiscordに送信
                    save_current_logs("\n".join(new_logs))  # 最新ログを保存
                    save_sent_logs(new_diff_message)  # 送信した差分を保存
                else:
                    print("差分はありません。")
            else:
                print("新しいログはありません。")

            # 最終取得日時を更新
            save_last_fetch_time(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

        except Exception as e:
            print(f"エラーが発生しました: {e}")

        # 次回実行まで待機
        time.sleep(60)

if __name__ == "__main__":
    try:
        # メインループを開始
        main()
    except KeyboardInterrupt:
        # Ctrl+Cが押された場合、プログラムを終了
        print("プログラムを終了します...")
