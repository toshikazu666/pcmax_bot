import os
from configparser import ConfigParser
from web_interface import WebInterface
from bot import generate_from_template, generate_data_wrapper, generate_data_for_morning, generate_data_for_night

def main():
    config = ConfigParser()
    config.read('settings.ini')

    login_url = config.get('pcmax', 'login_url')
    login_user = os.environ.get('LOGIN_USER')
    login_password = os.environ.get('LOGIN_PASSWORD')
    web = WebInterface(login_url, login_user, login_password)
    morning_data = generate_data_wrapper(web, 'morning')
    night_data = generate_data_wrapper(web, 'night')
    moring_tweet_text = generate_from_template('template', 'morning.j2', morning_data).encode('shift_jis')
    night_tweet_text = generate_from_template('template', 'night.j2', night_data).encode('shift_jis')
    
    print('/*--- moring tweet text (shift-jis) ---*/')
    print(moring_tweet_text)
    print('/*--- end ---*/')
    print('')
    print('/*--- morting tweet text (utf-8) ---*/')
    print(moring_tweet_text.decode('shift-jis'))
    print('/*--- end ---*/')
    print('')
    print('/*--- night tweet text (shift-jis) ---*/')
    print(night_tweet_text)
    print('/*--- end ---*/')
    print('')
    print('/*--- morting tweet text (utf-8) ---*/')
    print(night_tweet_text.decode('shift-jis'))
    print('/*--- end ---*/')
if __name__ == '__main__':
    main()