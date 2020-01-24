import os
import re
import time
import datetime
import schedule
import threading
from configparser import ConfigParser
from jinja2 import Template, Environment, FileSystemLoader
from interface.pcmax import Pcmax
from interface.wikipedia import Wikipedia
from interface.livedoor import Livedoor

from definition import MY_NAME
from definition import PAGE_THRESHOLD
from definition import LISTEN_INTERVAL_MINUTES
from definition import TODAY
from definition import TOMORROW
from definition import WEEKDAYS
from definition import NUMBER
from definition import YEAR_PATTERN
from definition import CITIES
from definition import MORNING_TIME
from definition import NIGHT_TIME
from definition import PURE
from definition import PURE_TAG
from definition import ADULT
from definition import ADULT_TAG

from definition import LISTEN_PATTERN
from definition import WEATHER_PATTERN
from definition import EVENT_PATTERN
from definition import TODAY_PATTERN
from definition import TOMORROW_PATTERN
from definition import DAY_AFTER_TOMORROW_PATTERN
from definition import SOON_PATTERN
from definition import YESTERDAY_PATTERN
from definition import DAY_BEFORE_YESTERDAY_PATTERN
from definition import DATE_PATTERN

from city_code_map import CITY_PATTERN
from city_code_map import CITY_CODE_MAP

config = ConfigParser()
config.read('settings.ini')

def try_wrapper(func, args=None):
    # 例外でbotが死なないようにラップする
    try:
        if args:
            func(args)
        else:
            func()
    except Exception as e:
        now = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
        print('[%s] some exception was captured, skip process'%now)
        print('-----')
        print(e)
        print('-----')

def listener(room, tag):
    # つぶやきを確認し、トリガーとなるつぶやきがあるかを確認する
    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')

    pcmax = Pcmax(login_url, login_user, login_password)

    # つぶやき一覧を取得する
    tweet_list = []
    for i in range(1, PAGE_THRESHOLD+1):
        tweet_list_url = config.get('pcmax', 'tweet_list_url').replace('ROOM', room).replace('PAGE', str(i))
        tweet_list += pcmax.get_tweet_list(tweet_list_url, tag)
    # 一覧の中にトリガーとなるワードを含むつぶやきがあるかを確認する
    target_tweet_list = get_target_tweet_list(tweet_list)
    
    today = datetime.date.today()
    # 時間帯によってあいさつを分ける
    greeting = get_greeting(datetime.datetime.now().hour)

    for target_tweet in target_tweet_list:
        # 対象のつぶやきに対してコメントをPOSTする
        thread = threading.Thread(target=post_comment, args=[target_tweet, today, greeting, room])
        thread.start()

def get_target_tweet_list(tweet_list):
    # 特定ワードを含むつぶやきを抽出する
    return [tweet for tweet in tweet_list if LISTEN_PATTERN.search(tweet['text'])]

def post_comment(tweet, today, greeting, room):
    # コメントをPOSTする
    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')
    pcmax = Pcmax(login_url, login_user, login_password)
    comment_list_url = config.get('pcmax', 'comment_list_url').replace('ROOM', room).replace('ID', tweet['id'])
    comment_list = pcmax.get_comment_list(comment_list_url)

    for comment in comment_list:
        # すでにコメントしている場合は処理をスキップ
        if comment['user'] == MY_NAME:
            return 0

    # つぶやきのテキストを解析してコメント文を作成する
    data = parser(tweet['text'], today, greeting)
    data['greeting'] = greeting
    data['user'] = tweet['user']

    text = generate_from_template('template', 'comment.j2', data).encode('shift_jis', 'replace')
    comment_input = pcmax.get_comment_input(comment_list_url)
    
    # コメントのPOST
    print('/*--- comment ---*/')
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
    print(pcmax.post_comment(comment_list_url, comment_input, text).status_code)
    print('Bot is aliving...')
    print('')

def forecast_data4comment(month, day, city, city_code, date):
    # 天気予報のコメント用データを取得する
    livedoor = Livedoor()
    url = config.get('livedoor', 'weather_forecast_url')
    forecast = livedoor.get_weather(url, city_code, date)
    return {'pattern': 'forecast', 'month': month, 'day': day, 'city': city, 'weather': forecast['weather'], 'max': forecast['max'], 'min': forecast['min']}

def event_data4comment(month, day, date):
    # 今日は何の日のコメント用データを取得する
    wikipedia = Wikipedia()
    url = config.get('wikipedia', 'url').replace('MONTH', month)
    event = wikipedia.get_date_event(url, date)
    end_word = get_end_word(event)
    return {'pattern': 'event', 'month': month, 'day': day, 'event': event, 'end_word': end_word}

def parser(text, today, greeting):
    # つぶやきを解析する
    if WEATHER_PATTERN.search(text):
        # 天気について解析
        city_match = CITY_PATTERN.search(text)
        if city_match:
            # 市町村を解析
            city = city_match.group()
            city_code = CITY_CODE_MAP[city]

            tomorrow_match = TOMORROW_PATTERN.search(text)
            if tomorrow_match:
                # 明日を解析
                date = TOMORROW
                d = today + datetime.timedelta(days=1)
                return forecast_data4comment(str(d.month), str(d.day), city, city_code, date)
            
            today_match = TODAY_PATTERN.search(text)
            if today_match:
                # 今日を解析
                date = TODAY
                d = today
                return forecast_data4comment(str(d.month), str(d.day), city, city_code, date)

            date_match = DATE_PATTERN.search(text)
            if date_match:
                # 日付を解析
                matches = date_match.groups()
                month_day = str_date2int(matches[0], matches[1])
                if month_day == (today.month, today.day):
                    # 日付が今日の場合
                    date = TODAY
                    d = today
                    return forecast_data4comment(str(d.month), str(d.day), city, city_code, date)

                tomorrow = today + datetime.timedelta(days=1)
                if month_day == (tomorrow.month, tomorrow.day):
                    # 日付が明日の場合
                    date = TOMORROW
                    d = today + datetime.timedelta(days=1)
                    return forecast_data4comment(str(d.month), str(d.day), city, city_code, date)
            
            # 日付が無効(今日か明日のみ有効)
            return {'pattern': 'null'}
        else:
            # 地名が無効
            return {'pattern': 'null'}

    elif EVENT_PATTERN.search(text):
        # 何の日かを解析
        soon_match = SOON_PATTERN.search(text)
        if soon_match:
            # しあさってを解析
            d = today + datetime.timedelta(days=3)
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)

        day_after_tomorrow_match = DAY_AFTER_TOMORROW_PATTERN.search(text)
        if day_after_tomorrow_match:
            # あさってを解析
            d = today + datetime.timedelta(days=2)
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)
        
        tomorrow_match = TOMORROW_PATTERN.search(text)
        if tomorrow_match:
            # 明日を解析
            d = today + datetime.timedelta(days=1)
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)

        today_match = TODAY_PATTERN.search(text)
        if today_match:
            # 今日を解析
            d = today
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)

        day_before_yesterday_match = DAY_BEFORE_YESTERDAY_PATTERN.search(text)
        if day_before_yesterday_match:
            # 一昨日を解析
            d = today - datetime.timedelta(days=2)
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)

        yesterday_match = YESTERDAY_PATTERN.search(text)
        if yesterday_match:
            # 昨日を解析
            d = today - datetime.timedelta(days=1)
            date = '%s月%s日' % (str(d.month), str(d.day))
            return event_data4comment(str(d.month), str(d.day), date)

        date_match = DATE_PATTERN.search(text)
        if date_match:
            # 日付を解析
            matches = date_match.groups()
            month_day = str_date2int(matches[0], matches[1])
            if month_day:
                date = '%s月%s日' % (str(month_day[0]), str(month_day[1]))
                return event_data4comment(str(month_day[0]), str(month_day[1]), date)

        return {'pattern': 'null'}
    else:
        return {'pattern': 'null'}

def get_greeting(hour):
    # あいさつ文の生成
    if 3 < hour and hour < 12:
        return 'オハヨウゴザイマス'
    elif 11 < hour and hour < 19:
        return 'コンニチハ'
    else:
        return 'コンバンハ'

def str_date2int(month_str, day_str):
    # 日付の文字列をintに変換する
    month = []
    for month_char in month_str:
        try:
            month.append(NUMBER[char_str])
        except:
            month.append(month_char)
    day = []
    for day_char in day_str:
        try:
            day.append(NUMBER[day_char])
        except:
            day.append(day_char)

    year = datetime.date.today().year
    month = int(''.join(month))
    day = int(''.join(day))
    try:
        # うるう年を考慮
        if month==2 and day==29:
            return [month, day]
        date = datetime.date(year, month, day)
        return [date.month, date.day]
    except:
        return False

def generate_from_template(directory, template_file, data):
    # jinja2テンプレートからつぶやきを生成する
    env = Environment(loader=FileSystemLoader(directory))
    template = env.get_template(template_file)
    return str(template.render(data))

def generate_data_wrapper(pattern):
    # pattern毎に必要なデータを取得する
    if pattern == 'morning':
        return generate_data_for_morning()
    elif pattern == 'night':
        return generate_data_for_night()
    else:
        # patternに一致しない場合は例外で終了
        raise ValueError('Pattern "%s" is not defined')

def get_end_word(event):
    # 歴史上の出来事なのか記念日なのかで語尾を使い分ける
    if YEAR_PATTERN.search(event):
        return 'ガアッタ日ダソウデス。'
    else:
        return 'ダソウデス。'

def generate_data_for_morning():
    # 朝のつぶやき用の情報を取得する
    today = datetime.date.today()
    month = str(today.month)
    day = str(today.day)
    weekday = WEEKDAYS[today.weekday()]
    # WikipediaのAPIから「今日は何の日」かを取得する
    wikipedia = Wikipedia()
    url = config.get('wikipedia', 'url').replace('MONTH', month)
    date = '%s月%s日' % (month, day)
    event = wikipedia.get_date_event(url, date)
    end_word = get_end_word(event)
    return {'pattern': 'morning',
            'month': month,
            'day': day,
            'weekday': weekday,
            'event': event,
            'end_word': end_word}

def generate_data_for_night():
    # 夜のつぶやき用の情報を取得する
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    month = str(tomorrow.month)
    day = str(tomorrow.day)
    weekday = WEEKDAYS[tomorrow.weekday()]
    # LivedoorのAPIから東京/大阪/名古屋の天気と気温を取得する
    livedoor = Livedoor()
    url = config.get('livedoor', 'weather_forecast_url')
    forecasts = []
    for city in CITIES:
        city_code = CITY_CODE_MAP[city]
        forecast = livedoor.get_weather(url, city_code, TOMORROW)
        forecast['city'] = city
        forecasts.append(forecast)
    return {'pattern': 'night',
            'month': month,
            'day': day,
            'weekday': weekday,
            'forecasts': forecasts}

def post_tweet(pattern):
    # PCMAXにログインしてつぶやきを投稿するためのインスタンスを生成し、つぶやきをPOSTする
    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')

    pcmax = Pcmax(login_url, login_user, login_password)
    tweet_post_url = config.get('pcmax', 'tweet_post_url').replace('ROOM', PURE)
    tweet_input = pcmax.get_tweet_input(tweet_post_url)

    data = generate_data_wrapper(pattern)
    tweet_text = generate_from_template('template', '%s.j2'%pattern, data).encode('shift_jis', 'replace')

    # つぶやきのPOST
    print('/*--- tweet ---*/')
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
    print(pcmax.post_tweet(tweet_post_url, tweet_input, tweet_text).status_code)
    print('Bot is aliving...')

def main():
    schedule.every(LISTEN_INTERVAL_MINUTES).minutes.do(try_wrapper, listener, ADULT, ADULT_TAG)
    schedule.every(LISTEN_INTERVAL_MINUTES).minutes.do(try_wrapper, listener, PURE, PURE_TAG)
    schedule.every().day.at(MORNING_TIME).do(try_wrapper, post_tweet, 'morning')
    schedule.every().day.at(NIGHT_TIME).do(try_wrapper, post_tweet, 'night')
    print('Tweet schedule set at %s, %s'%(MORNING_TIME, NIGHT_TIME))
    print('Listener active every %s minutes'%str(LISTEN_INTERVAL_MINUTES))
    print('')
    print('Bot is aliving...')
    print('')
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    main()
