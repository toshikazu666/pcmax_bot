# 概要
ピシマで暮らすbot

# 使い方
## 動作確認環境
- Raspbian GNU/Linux 10 (buster)
- Python 3.7.3
    - bs4
    - jinja2
    - requests
    - schedule

## 実行方法
### 環境設定
~~~
pip install -r requirements.txt
~~~

### ログイン情報設定
~~~
export LOGIN_USER="ログインユーザ名" LOGIN_PASSWORD="ログインパスワード"
~~~
- 環境変数にログインユーザ名(メールアドレス or 電話番号 or 会員ID)/パスワードを設定する
- exportまたはprintenvを実行し、LOGIN_USER/LOGIN_PASSWORDに値が設定されていればOK

### botのデプロイ
- botとして動作するアカウントのニックネームを定義
    - definition.py の変数 MY_NAME に、上記のログイン情報設定で使用したアカウントのニックネームを記載する
    
- 地名とIDのMAPを作成(更新)する(天気予報で必要)
~~~
python upedate_city_code_map
~~~

- botを動かす
~~~
python bot.py
~~~

- botの停止方法
    - Ctrl + Cなど

## botの機能
- 定刻になったらひとりごと(通常版)につぶやきを投稿する
    - 07:00に投稿するつぶやき
        - Wikipedia APIから「今日は何の日」の情報を取得して投稿する
    - 23:00に投稿するつぶやき
        - Livedoor APIから東京、大阪、名古屋、札幌の翌日の天気予報を取得して投稿する
- ひとりごと(アダルト版)の特定のワードに反応し、つぶやきを解析してコメントする
    - 反応するワード(あいまいに解釈できるため、これだけに限らない)
        - OK, bot (おーけー、ぼっと)
        - Hey, bot (へい、ぼっと)
        - Hello, bot (はろー、ぼっと)
    - 解析できる文言(あいまいに解釈できるため、これだけに限らない)
        - 天気/(特定の)地名/何の日/日付(今日/昨日など含む)
            - 「天気」が含まれている場合は「地名」、「日付(今日か昨日のみ)」を解析し、天気予報をコメントする
            - 「何の日」が含まれている場合は「日付」を解析し、その日が何の日かをコメントする
        - 解析できる文言がなかった場合、あいさつだけコメントする

## チェッカー
### POSTするつぶやきの文面をチェック
~~~
python check_output.py
~~~
- つぶやきの文面を標準出力する

### つぶやきがPOSTできるかをチェック
~~~
python check_tweet.py
~~~
- テスト用の文面をPOSTする
