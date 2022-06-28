import psycopg2
import pandas
import datetime
import pandas
import time
import requests
from typing import *

hostname = "bigdatapostgres-federicozilli-bf3a.aivencloud.com"
database = "CRYPTODB"
username = "avnadmin"
pswrd = "AVNS_1owyZsR6_lLL93247eQ"
port_id = 18580

conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)
cur = conn.cursor()
last = cur.execute('SELECT * FROM BTC ORDER BY id DESC LIMIT 1')
results = cur.fetchall()
last_entry = datetime.datetime.combine(results[0][0], results[0][1]).timestamp()

print(last_entry)

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
    return datetime.datetime.utcfromtimestamp(ms / 1000)

def ms_to_dt_local(ms: int) -> datetime:
    return datetime.datetime.fromtimestamp(ms / 1000)

def GetDataFrame(data):
    df = pandas.DataFrame(data, columns=['Timestamp', "Open", "High", "Low", "Close", "Volume"])
    df["Timestamp"] = pandas.to_datetime(df["Timestamp"].apply(lambda x: ms_to_dt_local(x)))
    df['Date'] = pandas.to_datetime(df["Timestamp"].dt.strftime("%Y-%m-%d"), errors='coerce')
    df['Time'] = pandas.to_datetime(df["Timestamp"].dt.strftime("%H:%M:%S"), errors='coerce')
    column_names = ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]
    df = df.set_index('Timestamp')
    df = df.reindex(columns=column_names)

    return df

def GetHistoricalData(client, symbol, start_time, end_time, limit=1500):
    collection = []

    while start_time <= end_time:
        print(ms_to_dt_local(start_time))
        print(ms_to_dt_local(end_time))
        data = client.get_historical_data(symbol, start_time=start_time, end_time=end_time, limit=limit)
        print(client.exchange + " " + symbol + " : Collected " + str(len(data)) + " missing data from "+ str(ms_to_dt_local(data[0][0])) +" to " + str(ms_to_dt_local(data[-1][0])))
        start_time = int(data[-1][0] + 60000)
        collection +=data
        time.sleep(1.1)

    return collection
    
client = BinanceClient(futures=False)
symbol = "BTCUSDT"
interval = "1m"
fromDate = (int(last_entry) * 1000) + 60000
toDate = int(datetime.datetime.now().timestamp())*1000

data = GetHistoricalData(client, symbol, fromDate, toDate)
df = GetDataFrame(data)
for index, row in df.iterrows():
    try:
        cur.execute(
            "INSERT INTO BTC VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (row['Date'],row['Time'],row['Open'],row['High'],row['Low'],row['Close'],row['Volume'])
        )
        conn.commit()
    except: continue
    
conn.close()
    
print("Filled")