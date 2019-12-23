import re
import random
import requests
from bs4 import BeautifulSoup

HTML_TAG_PATTERN = re.compile(r'<[^>]*?>')

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

    def get_tweet_input(self, tweet_post_url):
        # つぶやきのPOSTに必要なinputを取得する
        res = self.session.get(tweet_post_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        write_form = soup.find(id='write_form')
        inputs = write_form.find_all('input')
        return {i['name']: i['value'] for i in inputs}

    def post_tweet(self, tweet_post_url, input_values, text):
        # つぶやきを投稿する
        input_values['tweet_body'] = text
        res = self.session.post(tweet_post_url, data=input_values)
        res.raise_for_status()
        return res

    def get_tweet_list(self, tweet_list_url, tag=''):
        # つぶやき一覧を取得する
        res = self.session.get(tweet_list_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        class_name = 'mono_box%s' % tag
        tweets = soup.find_all('div', class_=class_name)
        return [{
            'id': str(tweet.get('id')).replace('mono', ''),
            'user': self.remove_html_tag(tweet.find('p', class_='name')),
            'text': self.remove_html_tag(tweet.find('p', class_='mono_txt'))
        } for tweet in tweets]

    def get_comment_list(self, comment_list_url):
        # つぶやきに付いているのコメント一覧を取得する
        res = self.session.get(comment_list_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        comments = soup.find_all('div', class_='mono_box child')
        return [{
            'user': self.remove_html_tag(comment.find('p', class_='name')),
            'text': self.remove_html_tag(comment.find('p', class_='mono_txt'))
        } for comment in comments]

    def get_comment_input(self, comment_list_url):
        # コメントのPOSTに必要なinputを取得する
        res = self.session.get(comment_list_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        write_form = soup.find(id='comment_form')
        inputs = write_form.find_all('input')
        del inputs[-1]
        return {i['name']: i['value'] for i in inputs}

    def post_comment(self, comment_list_url, input_values, text):
        input_values['comment'] = text
        res = self.session.post(comment_list_url, data=input_values)
        res.raise_for_status()
        return res

    def remove_html_tag(self, html):
        # HTMLのタグを除去して文字列を返す
        return HTML_TAG_PATTERN.sub('', str(html)).strip()
