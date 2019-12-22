import os
import re
import datetime
from configparser import ConfigParser
import time
import schedule
from jinja2 import Template, Environment, FileSystemLoader
from interface.pcmax import Pcmax
from interface.wikipedia import Wikipedia
from interface.livedoor import Livedoor, TODAY, TOMORROW
from weekdays import WEEKDAYS
from city_code_map import CITY_CODE_MAP

PURE = '1'
ADULT = '2'

MORNING_TIME = '07:00'
NIGHT_TIME = '23:00'

CITIES = ['東京', '大阪', '名古屋', '札幌',]

config = ConfigParser()
config.read('settings.ini')

EVENT_PATTERN = re.compile(r'（.+年.*?）$')

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
    event = wikipedia.get_today_event(url, date)
    if EVENT_PATTERN.search(event):
        # 歴史上の出来事なのか記念日なのかで語尾を使い分ける
        end_word = 'ガアッタ日ダソウデス。'
    else:
        end_word = 'ダソウデス。'
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

def tweet_wrapper(pattern):
    # PCMAXにログインしてつぶやきを投稿するためのインスタンスを生成し、つぶやきをポストする
    print('/*--- tweet begin ---*/')
    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')

    pcmax = Pcmax(login_url, login_user, login_password)
    tweet_post_url = config.get('pcmax', 'tweet_post_url').replace('ROOM', PURE)
    tweet_input = pcmax.get_tweet_input(tweet_post_url)

    data = generate_data_wrapper(pattern)
    tweet_text = generate_from_template('template', '%s.j2'%pattern, data).encode('shift_jis')
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
    print(tweet_text.decode('shift_jis'))
    print(pcmax.post_tweet(tweet_post_url, tweet_input, tweet_text).status_code)
    print('/*--- tweet end ---*/')
    print('')
    print('Bot is aliving...')
    print('')

def main():
    schedule.every().day.at(MORNING_TIME).do(tweet_wrapper, 'morning')
    schedule.every().day.at(NIGHT_TIME).do(tweet_wrapper, 'night')
    print('Tweet schedule set at %s, %s'%(MORNING_TIME, NIGHT_TIME))
    print('')
    print('Bot is aliving...')
    print('')
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    main()
