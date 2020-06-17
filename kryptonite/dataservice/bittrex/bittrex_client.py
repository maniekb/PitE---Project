import calendar
from datetime import datetime

import requests


class BittrexClient:

    def get_chart_data(self, symbol, start, end, interval):
        days_range = (end.date() - start.date()).days

        url = "https://api.bittrex.com/v3/markets/{}/candles/{}/recent".format(symbol, interval)
        response = requests.get(url=url)
        data = response.json()
        data = self._swap_datetime_with_mili_timestamp(data)
        data = [record for record in data if
                datetime.fromtimestamp(record["startsAt"] / 1000) >= start]

        return data

    def _swap_datetime_with_mili_timestamp(self, data):
        for record in data:
            record["startsAt"] = int(
                calendar.timegm(datetime.strptime(record["startsAt"], "%Y-%m-%dT%H:%M:%SZ").utctimetuple())) * 1000
        return data