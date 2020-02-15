import requests

class Unsei:
    def get_unsei(self, url, today, umare_month):
        # APIから今日の○月生まれの運勢を取得する
        return requests.get(url).json()['horoscope'][today][umare_month-1]