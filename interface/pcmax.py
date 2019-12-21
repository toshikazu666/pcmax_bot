import re
import random
import requests
from bs4 import BeautifulSoup

class Pcmax:
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
