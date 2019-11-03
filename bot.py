import os
import re
import datetime
from configparser import ConfigParser
import time
import schedule
from jinja2 import Template, Environment, FileSystemLoader
from web_interface import WebInterface
from weekdays import WEEKDAYS

PURE = '1'
ADULT = '2'

MORNING_TIME = '07:00'
NIGHT_TIME = '23:00'

config = ConfigParser()
config.read('settings.ini')

event_pattern = re.compile(r'（.+年）$')

def generate_from_template(directory, template_file, data):
    # jinja2テンプレートからつぶやきを生成する
    env = Environment(loader=FileSystemLoader(directory))
    template = env.get_template(template_file)
    return str(template.render(data))

def generate_data_wrapper(web, pattern):
    # pattern毎に必要なデータを取得する
    if pattern == 'morning':
        return generate_data_for_morning(web)
    elif pattern == 'night':
        return generate_data_for_night(web)
    else:
        # patternに一致しない場合は例外で終了
        raise ValueError('Pattern "%s" is not defined')

def generate_data_for_morning(web):
    # 朝のつぶやき用の情報を取得する
    today = datetime.date.today()
    month = str(today.month)
    day = str(today.day)
    weekday = WEEKDAYS[today.weekday()]
    # WikipediaのAPIから「今日は何の日」かを取得する
    url = config.get('event', 'url').replace('MONTH', month)
    date = '%s月%s日' % (month, day)
    event = web.get_today_event(url, date)
    if event_pattern.search(event):
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

def generate_data_for_night(web):
    # 夜のつぶやき用の情報を取得する
    today = datetime.date.today()
    tommorrow = today + datetime.timedelta(days=1)
    month = str(tommorrow.month)
    day = str(tommorrow.day)
    weekday = WEEKDAYS[tommorrow.weekday()]
    # LivedoorのAPIから東京/大阪/名古屋の天気と気温を取得する
    url = config.get('weather', 'url')
    tokyo = config.get('weather', 'tokyo')
    osaka = config.get('weather', 'osaka')
    nagoya = config.get('weather', 'nagoya')
    forecast_tokyo = web.get_today_weather(url, tokyo)
    forecast_osaka = web.get_today_weather(url, osaka)
    forecast_nagoya = web.get_today_weather(url, nagoya)
    return {'pattern': 'night',
            'month': month,
            'day': day,
            'weekday': weekday,
            'weather_tokyo': forecast_tokyo['weather'],
            'max_tokyo': forecast_tokyo['max'],
            'min_tokyo': forecast_tokyo['min'],
            'weather_osaka': forecast_osaka['weather'],
            'max_osaka': forecast_osaka['max'],
            'min_osaka': forecast_osaka['min'],
            'weather_nagoya': forecast_nagoya['weather'],
            'max_nagoya': forecast_nagoya['max'],
            'min_nagoya': forecast_nagoya['min']}

def tweet_wrapper(pattern):
    # Web用のインスタンスを生成してつぶやきをポストする
    print('/*--- tweet begin ---*/')
    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')
    web = WebInterface(login_url, login_user, login_password)
    tweet_url = config.get('pcmax', 'tweet_url').replace('ROOM', PURE)
    tweet_input = web.get_tweet_input(tweet_url)
    data = generate_data_wrapper(web, pattern)
    tweet_text = generate_from_template('template', '%s.j2'%pattern, data).encode('shift_jis')
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
    print(tweet_text.decode('shift_jis'))
    print(web.post_tweet(tweet_url, tweet_input, tweet_text).status_code)
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