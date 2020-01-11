import os
from configparser import ConfigParser
from bot import generate_from_template, generate_data_wrapper, generate_data_for_morning, generate_data_for_night

def main():

    morning_data = generate_data_wrapper('morning')
    night_data = generate_data_wrapper('night')
    moring_tweet_text = generate_from_template('template', 'morning.j2', morning_data).encode('shift_jis', 'replace')
    night_tweet_text = generate_from_template('template', 'night.j2', night_data).encode('shift_jis', 'replace')
    
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