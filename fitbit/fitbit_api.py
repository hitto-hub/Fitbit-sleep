from datetime import datetime, timedelta
from auth.auth import session, request, bearer_header

# Note: This function is not used in the main.py file
def get_sleep_log_by_date(date="today"):
    """
    指定された日付の睡眠ログを取得する関数

    :param date: 睡眠ログを取得する日付。デフォルトは "today"。
    :return: Fitbit APIのレスポンスオブジェクト
    """
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
    headers = bearer_header()  # Bearer認証用のヘッダーを取得
    res = request(session.get, url, headers=headers)  # GETリクエストを送信
    return res

def get_sleep_log_list(after_date=None, before_date=None, sort="asc", limit=100, offset=0):
    """
    指定された期間の睡眠ログリストを取得する関数

    :param after_date: 開始日を指定 (例: '2020-05-01')
    :param before_date: 終了日を指定 (例: '2020-06-01')
    :param sort: ソート順 ('asc' または 'desc')
    :param limit: 取得するログの最大件数
    :param offset: 結果のオフセット
    :return: Fitbit APIのレスポンスオブジェクト
    """
    print(f"Getting sleep logs from {after_date} to {before_date}")

    base_url = "https://api.fitbit.com/1.2/user/-/sleep/list.json"
    params = {
        "sort": sort,    # ソート順
        "limit": limit,  # 最大取得件数
        "offset": offset # 結果のオフセット
    }

    # 開始日と終了日をパラメータに追加
    if after_date:
        params["afterDate"] = after_date
    if before_date:
        params["beforeDate"] = before_date

    headers = bearer_header()  # Bearer認証用のヘッダーを取得
    res = request(session.get, base_url, headers=headers, params=params)  # GETリクエストを送信
    return res

def check_for_sleep(date=None):
    """
    指定された日付の睡眠ログをチェックし、睡眠の開始・終了をアラートとして生成する関数

    :param date: チェックする日付（例: '2023-11-01'）
    :return: 睡眠開始・終了を示す新しいログのリスト
    """
    # 前日の日付を計算
    res = get_sleep_log_list(after_date=(datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d"))
    data = res.json()  # APIのレスポンスをJSON形式で解析
    new_logs = []  # 新しいログを格納するリスト

    if data.get("sleep"):  # "sleep"データが存在するかを確認
        for sleep_log in data["sleep"]:
            previous_level = None  # 前回の睡眠レベルを初期化
            for entry in sleep_log["levels"]["data"]:
                # 睡眠開始を検出
                if previous_level == "wake" and entry["level"] in ["light", "deep", "rem"]:
                    message = f"Alert: Sleep started at {entry['dateTime']}"
                    new_logs.append(message)
                # 睡眠終了を検出
                elif previous_level in ["light", "deep", "rem"] and entry["level"] == "wake":
                    message = f"Alert: Sleep ended at {entry['dateTime']}"
                    new_logs.append(message)

                # 現在のレベルを次のループのために保存
                previous_level = entry["level"]
    else:
        print(f"No sleep detected on {date}")  # データがない場合の出力

    return new_logs  # 新しいログを返す
