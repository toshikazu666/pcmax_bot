import re

MY_NAME = 'ﾓﾋｶﾝ社畜bot'

PURE = '1'
ADULT = '2'

PAGE_THRESHOLD = 2

LISTEN_INTERVAL_MINUTES = 3

MORNING_TIME = '07:00'
NIGHT_TIME = '23:00'

CITIES = ['東京', '大阪', '名古屋', '札幌',]

TODAY = 0
TOMORROW = 1

YEAR_PATTERN = re.compile(r'（.+年.*?）$')
LISTEN_PATTERN = re.compile(r'([oO][kK]|[hH][eE][yY]|[hH][iI]|[hH][aAeEuU][lL][lL][oO]|[おオ]ー[けケ]ー|[へヘ][いイ]|[はハ][ろロ]ー)( |　|\n|\r|\r\n)*?(,|\.|、|。)?( |　|\n|\r|\r\n)*?([bB][oO][tT]|[ぼボ][っッ][とト])')
TODAY_PATTERN = re.compile(r'今日|きょう')
TOMORROW_PATTERN = re.compile(r'明日|あす|あした')
DAY_AFTER_TOMORROW_PATTERN = re.compile(r'明後日|あさって')
SOON_PATTERN = re.compile(r'明々後日|明明後日|しあさって')
YESTERDAY_PATTERN = re.compile(r'昨日|きのう')
DAY_BEFORE_YESTERDAY_PATTERN = re.compile(r'一昨日|おととい')
DATE_PATTERN = re.compile(r'([0-9０-９]?[0-9０-９])[月/／]([0-9０-９]?[0-9０-９])')
WEATHER_PATTERN = re.compile(r'天気|てんき')
EVENT_PATTERN = re.compile(r'(なに|なん|何)(があった|の)(ひ|日)')

WEEKDAYS = {
    0: '月',
    1: '火',
    2: '水',
    3: '木',
    4: '金',
    5: '土',
    6: '日'
}

NUMBER = {
    '０': '0',
    '１': '1',
    '２': '2',
    '３': '3',
    '４': '4',
    '５': '5',
    '６': '6',
    '７': '7',
    '８': '8',
    '９': '9'
}



