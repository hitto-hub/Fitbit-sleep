from datetime import datetime, timedelta
from auth.auth import session, request, bearer_header
import json

def get_sleep_log_by_date(date="today"):
    """
    指定された日付の睡眠ログを取得する関数

    :param date: 睡眠ログを取得する日付（デフォルトは "today"）。
                 形式は 'YYYY-MM-DD'。今日の日付を取得する場合は "today" を指定。
    :return: Fitbit APIのレスポンスオブジェクト
    """
    # Fitbit APIのエンドポイントURLを設定
    url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"

    # Bearer認証用ヘッダーを取得
    headers = bearer_header()

    # APIリクエストを実行してレスポンスを取得
    res = request(session.get, url, headers=headers)

    # レスポンス内容を整形して表示
    print("Response from get_sleep_log_by_date:")
    print(json.dumps(res.json(), indent=4, ensure_ascii=False))

    return res  # レスポンスオブジェクトを返す

def get_sleep_log_list(after_date=None, before_date=None, sort="asc", limit=100, offset=0):
    """
    指定された期間の睡眠ログリストを取得する関数

    :param after_date: 開始日を指定 (例: '2020-05-01')。指定しない場合はNone。
    :param before_date: 終了日を指定 (例: '2020-06-01')。指定しない場合はNone。
    :param sort: ソート順 ('asc' または 'desc')。デフォルトは 'asc'。
    :param limit: 取得するログの最大件数。デフォルトは100。
    :param offset: 結果のオフセット値。デフォルトは0。
    :return: Fitbit APIのレスポンスオブジェクト
    """
    print(f"Getting sleep logs from {after_date} to {before_date}")

    # Fitbit APIのエンドポイントURLを設定
    base_url = "https://api.fitbit.com/1.2/user/-/sleep/list.json"

    # クエリパラメータを設定
    params = {
        "sort": sort,    # ソート順
        "limit": limit,  # 最大取得件数
        "offset": offset # オフセット
    }

    # after_dateおよびbefore_dateが指定されている場合、パラメータに追加
    if after_date:
        params["afterDate"] = after_date
    if before_date:
        params["beforeDate"] = before_date

    # Bearer認証用ヘッダーを取得
    headers = bearer_header()

    # APIリクエストを実行してレスポンスを取得
    res = request(session.get, base_url, headers=headers, params=params)

    # レスポンス内容を整形して表示
    print("Response from get_sleep_log_list:")
    print(json.dumps(res.json(), indent=4, ensure_ascii=False))

    return res  # レスポンスオブジェクトを返す

from datetime import datetime, timedelta

def check_for_sleep(date=None):
    """
    指定された日付の睡眠ログをチェックし、睡眠の開始・終了をアラートとして生成する関数

    :param date: チェックする開始日時（例: '2023-11-01T20:43:47'）
    :return: 睡眠開始・終了を示す新しいログのリスト
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    after_date = (datetime.strptime(date, "%Y-%m-%dT%H:%M:%S") + timedelta(days=-1)).strftime("%Y-%m-%d")
    res = get_sleep_log_list(after_date=after_date)  # APIからログを取得
    data = res.json()
    
    alerts = []

    if "sleep" in data:
        for sleep_log in data["sleep"]:
            previous_level = None
            for entry in sleep_log["levels"]["data"]:
                timestamp = datetime.strptime(entry["dateTime"], "%Y-%m-%dT%H:%M:%S.%f")
                if previous_level == "wake" and entry["level"] in ["light", "deep", "rem"]:
                    alerts.append((timestamp, f"Alert: Sleep started at {entry['dateTime']}"))
                elif previous_level in ["light", "deep", "rem"] and entry["level"] == "wake":
                    alerts.append((timestamp, f"Alert: Sleep ended at {entry['dateTime']}"))
                previous_level = entry["level"]
    else:
        print(f"No sleep detected after {after_date}")

    # タイムスタンプでソート
    alerts.sort(key=lambda x: x[0])
    
    # メッセージ部分だけを抽出して返す
    return [message for _, message in alerts]
