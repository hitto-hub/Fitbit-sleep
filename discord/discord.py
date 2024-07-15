import os
from requests import Session
from dotenv import load_dotenv

load_dotenv()
session = Session()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_to_discord(message):
    """DiscordのWebhookにメッセージを送信"""
    data = {"content": message}
    response = session.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"メッセージの送信に失敗しました: {response.status_code}, {response.text}")
    else:
        print("メッセージが正常に送信されました")
