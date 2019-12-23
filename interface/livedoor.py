import requests
from bs4 import BeautifulSoup

class Livedoor:
    def get_weather(self, weather_forecast_url, city_code, date=0):
        # LiveDoor API から翌日の天気情報を取得する
        payload = {'city': city_code}
        res = requests.get(weather_forecast_url, params=payload)
        forecast = res.json()['forecasts'][date]
        # タイミングによって取れないことがあるので、取れない場合は例外を捕捉して"--"とする
        try:
            weather = forecast['telop']
        except:
            print('Can not get weather on %s'%city_code)
            weather = '--'
        try:
            max_t = forecast['temperature']['max']['celsius']
        except:
            print('Can not get max temperature on %s'%city_code)
            max_t = '--'
        try:
            min_t = forecast['temperature']['min']['celsius']
        except:
            print('Can not get min temperature on %s'%city_code)
            min_t = '--'
        return {'weather': weather, 'max': max_t, 'min': min_t}

    def get_city_code_dict(self, city_code_map_url):
        # 市町村とコードの対応付を辞書にして返す
        res = requests.get(city_code_map_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        city_infos = soup.find_all('city')
        return {str(city_info.get('title')): str(city_info.get('id')) for city_info in city_infos}