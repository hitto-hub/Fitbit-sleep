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

def check_for_sleep(date=None):
    """
    指定された日付の睡眠ログをチェックし、睡眠の開始・終了をアラートとして生成する関数

    :param date: チェックする日付（例: '2023-11-01'）。形式は 'YYYY-MM-DD'。
    :return: 睡眠開始・終了を示す新しいログのリスト
    """
    # 日付が指定されていない場合はエラーを防ぐために現在の日付をデフォルトに設定
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    # 前日の日付を計算して`after_date`に設定
    after_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")

    # 指定された範囲の睡眠ログを取得
    res = get_sleep_log_list(after_date=after_date)
    data = res.json()  # APIのレスポンスをJSON形式で解析

    # レスポンス内容を整形して表示
    print("Response from check_for_sleep:")
    print(json.dumps(data, indent=4, ensure_ascii=False))

    # 新しい睡眠ログを格納するリスト
    new_logs = []

    # "sleep"データが存在するかを確認
    if data.get("sleep"):
        for sleep_log in data["sleep"]:  # 各睡眠ログを処理
            previous_level = None  # 前回の睡眠レベルを初期化
            for entry in sleep_log["levels"]["data"]:  # 各レベルのデータを処理
                # "wake"から他のレベルへの遷移で睡眠開始を検出
                if previous_level == "wake" and entry["level"] in ["light", "deep", "rem"]:
                    message = f"Alert: Sleep started at {entry['dateTime']}"
                    new_logs.append(message)
                # 他のレベルから"wake"への遷移で睡眠終了を検出
                elif previous_level in ["light", "deep", "rem"] and entry["level"] == "wake":
                    message = f"Alert: Sleep ended at {entry['dateTime']}"
                    new_logs.append(message)

                # 現在のレベルを次のループのために保存
                previous_level = entry["level"]
    else:
        # 指定された日付に睡眠データがない場合のメッセージ
        print(f"No sleep detected on {date}")

    return new_logs  # 新しい睡眠開始・終了ログのリストを返す
