import time
import os
import csv
import json
import requests
from typing import *
import datetime
from kafka import KafkaProducer
import pandas as pd

producer = KafkaProducer(
    bootstrap_servers=[os.environ["KAFKA_HOST"]],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    api_version=(0, 11),
)

class BinanceClient:
    def __init__(self, futures=False):
        self.exchange = "BINANCE"
        self.futures = futures

        if self.futures:
            self._base_url = "https://fapi.binance.com"
        else:
            self._base_url = "https://api.binance.com"

        self.symbols = self._get_symbols()

    def _make_request(self, endpoint: str, query_parameters: Dict):
        try:
            response = requests.get(self._base_url + endpoint, params=query_parameters)
        except Exception as e:
            print("Connection error while making request to %s: %s", endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            print("Error while making request to %s: %s (status code = %s)",
                         endpoint, response.json(), response.status_code)
            return None

    def _get_symbols(self) -> List[str]:

        params = dict()

        endpoint = "/fapi/v1/exchangeInfo" if self.futures else "/api/v3/exchangeInfo"
        data = self._make_request(endpoint, params)

        symbols = [x["symbol"] for x in data["symbols"]]

        return symbols

    def get_historical_data(self, symbol: str, interval: Optional[str] = "1m", start_time: Optional[int] = None, end_time: Optional[int] = None, limit: Optional[int] = 1500):

        params = dict()

        params["symbol"] = symbol
        params["interval"] = interval
        params["limit"] = limit

        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        endpoint = "/fapi/v1/klines" if self.futures else "/api/v3/klines"
        raw_candles = self._make_request(endpoint, params)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append((float(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]),))
            return candles
        else:
            return None

def ms_to_dt_utc(ms: int) -> datetime:
    return datetime.utcfromtimestamp(ms / 1000)

def ms_to_dt_local(ms: int) -> datetime:
    return datetime.datetime.fromtimestamp(ms / 1000)

def GetDataFrame(data):
    df = pd.DataFrame(data, columns=['Timestamp', "Open", "High", "Low", "Close", "Volume"])
    df["Timestamp"] = df["Timestamp"].apply(lambda x: ms_to_dt_local(x))
    df['Date'] = df["Timestamp"].dt.strftime("%d/%m/%Y")
    df['Time'] = df["Timestamp"].dt.strftime("%H:%M:%S")
    column_names = ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]
    df = df.set_index('Timestamp')
    df = df.reindex(columns=column_names)

    return df

def GetHistoricalData(client, symbol, start_time, end_time, limit=1500):
    data = client.get_historical_data(symbol, start_time=start_time, end_time=end_time, limit=limit)

    return data

symbols = os.environ["COINS"].split(",")
client = BinanceClient(futures=False)
interval = "1m"

# Messages will be serialized as JSON 
def serializer(message):
    return json.dumps(message).encode('utf-8')

headers = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']

while True:
    try:
        for symbol in symbols:
            start = time.time()
            fromDate = int((datetime.datetime.now() - datetime.timedelta(minutes=2)).timestamp() * 1000)
            toDate = int(datetime.datetime.now().timestamp() * 1000)
            data = GetHistoricalData(client, symbol, fromDate, toDate)
            date1=ms_to_dt_local(data[1][0]).strftime('%Y-%m-%d')
            time1=(ms_to_dt_local(data[1][0])+datetime.timedelta(hours=2)).strftime('%H:%M:%S')
            data1=list(data[1])
            data1.pop(0)
            data1.insert(0, time1)
            data1.insert(0, date1)
            value = {headers[i]: data1[i] for i in range(len(headers))}
            producer.send(symbol, value=value)
            end = time.time()
            producer.flush()
            print(value)
        print((end - start))
        time.sleep(60-(end - start))
    except:
        end = time.time()
        time.sleep(60-(end - start))
