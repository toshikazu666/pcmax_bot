import os
import datetime
from configparser import ConfigParser
from jinja2 import Template, Environment, FileSystemLoader
from bot import generate_from_template, PURE
from web_interface import WebInterface

def main():
    config = ConfigParser()
    config.read('settings.ini')

    now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')
    web = WebInterface(login_url, login_user, login_password)


    tweet_url = config.get('pcmax', 'tweet_url').replace('ROOM', PURE)
    tweet_input = web.get_tweet_input(tweet_url)
    tweet_text = generate_from_template('template', 'test.j2', {'time': now}).encode('shift-jis')
    
    print('/*--- post tweet ---*/')
    print(tweet_text.decode('shift-jis'))
    print('/*--- end ---*/')
    print('url: %s'%tweet_url)
    print(str(web.post_tweet(tweet_url, tweet_input, tweet_text)))

if __name__ == '__main__':
    main()