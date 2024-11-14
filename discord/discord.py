import os
from requests import Session
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# HTTPセッションの初期化
session = Session()

# Discord WebhookのURLを環境変数から取得
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_to_discord(message):
    """
    DiscordのWebhookにメッセージを送信する関数

    :param message: 送信するメッセージの内容（文字列）
    """
    # Discordに送信するデータをJSON形式で作成
    data = {"content": message}

    # Webhook URLにPOSTリクエストを送信
    response = session.post(WEBHOOK_URL, json=data)

    # レスポンスのステータスコードをチェック
    if response.status_code != 204:
        # ステータスコードが204以外の場合はエラーと見なす
        print(f"メッセージの送信に失敗しました: {response.status_code}, {response.text}")
    else:
        # メッセージが正常に送信された場合
        print("メッセージが正常に送信されました")
