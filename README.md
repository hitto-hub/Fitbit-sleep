# memo

150req/1h

アクセス・トークン8時間で失効。

失効時はリフレッシュ・トークンを使って再取得が必要。

[リフレッシュ・トークンのdocs](https://dev.fitbit.com/build/reference/web-api/authorization/refresh-token/)

- Get Sleep Log by Date: 指定した日の睡眠ログエントリを取得します。
- Get Sleep Log by Date Range: 指定した期間の睡眠ログエントリを取得します。
- Get Sleep Log List: 指定した日付前後の睡眠ログエントリのリストを取得します。

## Directory Structure

- `auth/`: Contains authentication related functions.
- `fitbit/`: Contains functions to interact with the Fitbit API.
- `discord/`: Contains functions to send messages to Discord.
- `file_operations/`: Contains functions to handle file operations.
- `config/`: Contains configuration files.
- `main.py`: Main entry point of the application.
- `.env`: Environment variables.
- `requirements.txt`: Python dependencies.

## de

認証情報の読み込み:

./test_conf.json ファイルから認証情報（client_id, access_token, refresh_token）を読み込みます。
Bearer認証ヘッダの生成:

bearer_header 関数で、リクエストヘッダに Authorization: Bearer {access_token} を設定します。
アクセストークンのリフレッシュ:

refresh 関数で、トークンが失効した際に新しい access_token と refresh_token を取得し、test_conf.json ファイルを更新します。
トークン失効のチェック:

is_expired 関数で、レスポンスからトークンの失効を確認します。
リクエスト実行関数:

request 関数で、リクエストを実行し、必要に応じてトークンをリフレッシュして再リクエストします。
指定日の睡眠ログ取得:

get_sleep_log_by_date 関数で、指定日の睡眠ログをFitbit APIから取得します。
睡眠の開始・終了のチェック:

check_for_sleep 関数で、指定日の睡眠ログをチェックし、睡眠の開始（"wake"から"asleep"）と終了（"asleep"から"wake"）時にアラートを表示します。
1分ごとに実行するループ:

while True ループで、毎分指定日の睡眠ログをチェックし、アラートを表示します。
このコードは、Fitbit APIを使って睡眠ログを監視し、睡眠の開始と終了をリアルタイムで検知してアラートを表示するシステムを構築します。
