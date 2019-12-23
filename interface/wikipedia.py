import re
import random
import requests

WIKI_PATTERN = re.compile(r'\[\[(.+?)\]\]')

class Wikipedia:
    def get_date_event(self, url, date_str):
        # Wikipedia APIから今日が何の日かを取得する
        def remove_wiki_tag(string):
            # Wikiフォーマットの整形用
            links = WIKI_PATTERN.findall(string)
            for link in links:
                string = string.replace(link, link.split('|')[0])
            return string.replace('==', '').replace('[[', '').replace(']]', '').replace('*', '').strip()
        
        def get_valid_events(event_list):
            # 要素がコメントアウトされていない、かつ60文字より少ないイベントのみ対象
            events = []
            for event in event_list:
                if '<!--' not in event:
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