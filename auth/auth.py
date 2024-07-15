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
