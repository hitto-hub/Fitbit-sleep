import json
import os
from requests import Session

# HTTPセッションを初期化
session = Session()

def load_conf():
    """
    設定ファイルから認証情報を読み込む関数

    :return: 設定情報を辞書形式で返す
    """
    with open("./config/test_conf.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 設定ファイルの内容を読み込み
conf = load_conf()

def bearer_header():
    """
    Bearer認証用のヘッダーを生成する関数

    :return: Bearer認証用のヘッダー辞書
    """
    return {"Authorization": "Bearer " + conf["access_token"]}

def refresh():
    """
    アクセストークンをリフレッシュし、設定ファイルを更新する関数
    
    Fitbit APIのトークンリフレッシュエンドポイントを使用。
    """
    url = "https://api.fitbit.com/oauth2/token"  # トークンリフレッシュのURL
    params = {
        "grant_type": "refresh_token",          # リフレッシュトークンを使用することを指定
        "refresh_token": conf["refresh_token"], # 現在のリフレッシュトークン
        "client_id": conf["client_id"],         # クライアントID
    }

    # リフレッシュリクエストを実行
    res = session.post(url, data=params)
    res_data = res.json()

    # エラーチェック
    if res_data.get("errors"):
        print(res_data["errors"][0])  # エラー内容を出力
        return

    # 新しいアクセストークンとリフレッシュトークンを設定
    conf["access_token"] = res_data["access_token"]
    conf["refresh_token"] = res_data["refresh_token"]

    # 更新された設定をファイルに保存
    with open("./config/test_conf.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

def is_expired(res_obj):
    """
    レスポンスオブジェクトからトークンの有効期限をチェックする関数

    :param res_obj: APIリクエストのレスポンスオブジェクト
    :return: トークンが失効している場合はTrue、それ以外はFalse
    """
    errors = res_obj.get("errors")
    if not errors:
        return False
    for err in errors:
        if err.get("errorType") == "expired_token":
            print("TOKEN_EXPIRED!!!")  # トークンの失効を通知
            return True
    return False

def request(method, url, **kw):
    """
    APIリクエストを実行する関数

    :param method: HTTPメソッド（GET, POSTなど）
    :param url: リクエストのURL
    :param kw: その他のリクエストパラメータ（headers, paramsなど）
    :return: APIリクエストのレスポンスオブジェクト
    """
    res = method(url, **kw)  # 最初のリクエストを実行
    res_data = res.json()    # レスポンスをJSON形式で解析

    # トークンの有効期限を確認
    if is_expired(res_data):
        refresh()  # トークンをリフレッシュ
        kw["headers"] = bearer_header()  # 新しいヘッダーを設定
        res = method(url, **kw)  # リトライ
    return res
