import os
import datetime
from argparse import ArgumentParser
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

def generate_from_template(directory, template_file, data):
    # jinja2テンプレートからつぶやきを生成する
    env = Environment(loader=FileSystemLoader(directory))
    template = env.get_template(template_file)
    return str(template.render(data))

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
    return {'pattern': 'morning',
            'month': month,
            'day': day,
            'weekday': weekday,
            'event': event}

def generate_data_for_night(web):
    # 夜のつぶやき用の情報を取得する
    today = datetime.date.today()
    tommorrow = today + datetime.timedelta(days=1)
    month = str(tommorrow.month)
    day = str(tommorrow.day)
    weekday = WEEKDAYS[tommorrow.weekday()]
    # LivedoorのAPIから東京/大阪/名古屋の天気と気温を収録する
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

def morning_tweet():
    # Web用のインスタンスを生成してつぶやきをポストする(朝用)
    try:
        print('/*--- tweet begin ---*/')
        login_url = config.get('pcmax', 'login_url')
        login_user = os.environ.get('LOGIN_USER')
        login_password = os.environ.get('LOGIN_PASSWORD')
        web = WebInterface(login_url, login_user, login_password)
        tweet_url = config.get('pcmax', 'tweet_url').replace('ROOM', PURE)
        tweet_input = web.get_tweet_input(tweet_url) 
        data = generate_data_for_morning(web)
        tweet_text = generate_from_template('template', 'morning.j2', data).encode('shift_jis')
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
        print(tweet_text.decode('shift_jis'))
        print(web.post_tweet(tweet_url, tweet_input, tweet_text).status_code)
        print('/*--- tweet end ---*/')
    except Exception as e:
        print(e)

def night_tweet():
    #  Web用のインスタンスを生成してつぶやきをポストする(夜用)
    try:
        print('/*--- tweet begin ---*/')
        login_url = config.get('pcmax', 'login_url')
        login_user = os.environ.get('LOGIN_USER')
        login_password = os.environ.get('LOGIN_PASSWORD')
        web = WebInterface(login_url, login_user, login_password)
        tweet_url = config.get('pcmax', 'tweet_url').replace('ROOM', PURE)
        tweet_input = web.get_tweet_input(tweet_url) 
        data = generate_data_for_night(web)
        tweet_text = generate_from_template('template', 'night.j2', data).encode('shift_jis')
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
        print(tweet_text.decode('shift_jis'))
        print(web.post_tweet(tweet_url, tweet_input, tweet_text).status_code)
        print('/*--- tweet end ---*/')
    except Exception as e:
        print(e)

def main():
    schedule.every().day.at(MORNING_TIME).do(morning_tweet)
    schedule.every().day.at(NIGHT_TIME).do(night_tweet)
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == '__main__':
    main()