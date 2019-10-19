# 概要
定刻になったら自動でピシマにつぶやきを投稿するbot

# 使い方
## 動作確認環境
- Ubuntu 18.04.2 LTS on WSL
- Python 3.6.8
    - pipenv

## 実行方法
### 環境設定
~~~
pipenv install
~~~

### ログイン情報設定
~~~
export LOGIN_USER="ログインユーザ名" LOGIN_PASSWORD="ログインパスワード"
~~~
- 環境変数にログインユーザ名(メールアドレス or 電話番号 or 会員ID)/パスワードを設定する
- exportまたはprintenvを実行し、LOGIN_USER/LOGIN_PASSWORDに値が設定されていればOK

### botのデプロイ
~~~
pipenv run python bot.py
~~~
- 実行することによってbotが常駐し、常駐している間は毎日07:00と23:00につぶやきを投稿する
    - 07:00に投稿するつぶやき
        - Wikipedia APIから「今日は何の日」の情報を取得して投稿する
    - 23:00に投稿するつぶやき
        - Livedoor APIから東京、大阪、名古屋の翌日の天気予報を取得して投稿する
- botの停止方法
    - Ctrl + Cなど