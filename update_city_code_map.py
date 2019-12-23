"""天気予報に必要な市町村とコードの対応付のファイルを作成/更新する
"""

import os
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser
from interface.livedoor import Livedoor

def get_city_code_re(city_code_dict):
    # 市町村のマッチングパターンを生成する
    return '|'.join(list(city_code_dict.keys()))

def output_map(city_code_re, city_code_dict):
    # 市町村のマッチングパターン、市町村とコードの対応付けをフォーマットしてファイル出力する
    text_array = []
    text_array.append('import re')
    text_array.append('')
    text = "CITY_PATTERN = re.compile(r'%s')" % city_code_re
    text_array.append(text)
    text_array.append('')
    text_array.append('CITY_CODE_MAP = {')
    for city, code in city_code_dict.items():
        text = "    '%s': '%s'," % (city, code)
        text_array.append(text)
    text_array.append('}')
    
    with open('city_code_map.py', 'w') as file:
        file.write('\n'.join(text_array))

def main():
    config = ConfigParser()
    config.read('settings.ini')
    livedoor = Livedoor()

    url = config.get('livedoor', 'city_code_map_url')
    # livedoor APIから市町村とコードの対応付を取得
    city_code_dict = livedoor.get_city_code_dict(url)
    city_code_re = get_city_code_re(city_code_dict)
    output_map(city_code_re, city_code_dict)

if __name__ == '__main__':
    main()