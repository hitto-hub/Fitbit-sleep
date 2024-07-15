from datetime import datetime, timedelta
from auth.auth import session, request, bearer_header

def get_sleep_log_list(after_date=None, before_date=None, sort="asc", limit=100, offset=0):
    """
    Fitbit APIから睡眠ログリストを取得する

    :param after_date: 開始日の指定 (例: '2020-05-01')
    :param before_date: 終了日の指定 (例: '2020-06-01')
    :param sort: ソート順 ('asc' または 'desc')
    :param limit: 取得するログの数
    :param offset: オフセット
    :return: 睡眠ログのリスト
    """
    base_url = "https://api.fitbit.com/1.2/user/-/sleep/list.json"
    params = {
        "sort": sort,
        "limit": limit,
        "offset": offset
    }

    if after_date:
        params["afterDate"] = after_date
    if before_date:
        params["beforeDate"] = before_date

    headers = bearer_header()
    res = request(session.get, base_url, headers=headers, params=params)
    return res

def check_for_sleep(date=None):
    """指定日の睡眠ログをチェックし、睡眠の開始・終了をアラート表示およびDiscord通知"""
    res = get_sleep_log_list(after_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), before_date=date)
    data = res.json()
    new_logs = []
    if data.get("sleep"):
        for sleep_log in data["sleep"]:
            previous_level = None
            for entry in sleep_log["levels"]["data"]:
                if previous_level == "wake" and entry["level"] in ["light", "deep", "rem"]:
                    message = f"Alert: Sleep started at {entry['dateTime']}"
                    new_logs.append(message)
                elif previous_level in ["light", "deep", "rem"] and entry["level"] == "wake":
                    message = f"Alert: Sleep ended at {entry['dateTime']}"
                    new_logs.append(message)
                previous_level = entry["level"]
    else:
        print(f"No sleep detected on {date}")
    return new_logs
