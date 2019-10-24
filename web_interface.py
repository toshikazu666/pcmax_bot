import re
import random
import requests
from bs4 import BeautifulSoup

wiki_pattern = re.compile(r'\[\[(.+?)\]\]')

class WebInterface:
    def __init__(self, login_url, user, password):
        # ピシマにログインしてセッションを作る
        self.session = requests.session()
        login_info = {
            'login_id': user,
            'login_pw': password,
            'save_on': 'false',
            'login': '1'
        }
        res = self.session.post(login_url, data=login_info)
        res.raise_for_status()

    def get_tweet_input(self, tweet_url):
        # つぶやきのPOSTに必要なinputを取得する
        res = self.session.get(tweet_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        write_form = soup.find(id='write_form')
        inputs = write_form.find_all('input')
        return {i['name']: i['value'] for i in inputs}

    def post_tweet(self, tweet_url, input_values, text):
        # つぶやきを投稿する
        input_values['tweet_body'] = text
        res = self.session.post(tweet_url, data=input_values)
        res.raise_for_status()
        return res

    def get_today_event(self, url, date_str):
        # Wikipedia APIから今日が何の日かを取得する
        def remove_wiki_tag(string):
            # Wikiフォーマットの整形用
            links = wiki_pattern.findall(string)
            for link in links:
                string = string.replace(link, link.split('|')[0])
            return string.replace('==', '').replace('[[', '').replace(']]', '').replace('*', '').strip()
        
        def get_valid_events(event_list):
            # 60文字より少ないイベントのみ対象(文字数制限対策)
            events = []
            for event in event_list:
                e = remove_wiki_tag(event)
                if len(e) < 60:
                    events.append(e)
            return events

        # 月を指定して、日ごとが何の日かのリストを取得する
        res = requests.get(url)
        content = list(res.json()['query']['pages'].values())[0]['revisions'][0]['*']
        events_list = content.split('\n\n')
        # 余分な要素を削除
        del events_list[0]
        del events_list[-2:]

        # リストを日付をkeyとしたdictに整形する
        event_dict = {}
        for events in events_list:
            event_list = events.split('\n')
            day = remove_wiki_tag(event_list[0])
            del event_list[0]
            event_dict[day] = get_valid_events(event_list)
        return random.choice(event_dict[date_str])

    def get_today_weather(self, url, city):
        # LiveDoor API から今日の天気情報を取得する
        payload = {'city': city}
        res = requests.get(url, params=payload)
        forecast = res.json()['forecasts'][1]
        # たまに取れないことがあるので、取れない場合は例外を捕捉して"--"とする
        try:
            weather = forecast['telop']
        except:
            print('Can not get weather on %s'%city)
            weather = '--'
        try:
            max_t = forecast['temperature']['max']['celsius']
        except:
            print('Can not get max temperature on %s'%city)
            max_t = '--'
        try:
            min_t = forecast['temperature']['min']['celsius']
        except:
            print('Can not get min temperature on %s'%city)
            min_t = '--'
        return {'weather': weather, 'max': max_t, 'min': min_t}
