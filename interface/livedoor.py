import requests

class Livedoor:
    def get_today_weather(self, url, city):
        # LiveDoor API から今日の天気情報を取得する
        payload = {'city': city}
        res = requests.get(url, params=payload)
        forecast = res.json()['forecasts'][1]
        # たまに取れないことがあるので、取れない場合は例外を捕捉して"--"とする
        try:
            weather = forecast['telop']
        except:
            print('Can not get weather on %s'%city)
            weather = '--'
        try:
            max_t = forecast['temperature']['max']['celsius']
        except:
            print('Can not get max temperature on %s'%city)
            max_t = '--'
        try:
            min_t = forecast['temperature']['min']['celsius']
        except:
            print('Can not get min temperature on %s'%city)
            min_t = '--'
        return {'weather': weather, 'max': max_t, 'min': min_t}