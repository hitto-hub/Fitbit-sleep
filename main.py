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
        print(f"{date}の睡眠ログを取得中...")
        # 前回のログを取得
        previous_logs = get_previous_logs().splitlines()
        # 新しい睡眠ログを取得
        new_logs = check_for_sleep(date)
        # 差分を確認
        diff = list(difflib.unified_diff(previous_logs, new_logs, lineterm=''))
        diff = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]
        # 差分があれば通知と保存
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