import pandas as pd
import psycopg2
from sklearn.linear_model import LinearRegression
import time

#Auxiliary functions -----------------------------------------------------------------------------------------------------------
class Coin_at_time:

    def __init__(self, date, time, open :float  , high:float, low:float, close:float, volume:float)->None:
        self._date = date
        self._time = time
        self._open = open
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume

    def __repr__(self) -> str:
        to_ret = { "date " : self._date,
                "time " : self._time,
                "open" : self._open,
                "high" : self._high, 
                "low" : self._low,
                "close" : self._close,
                "volume" : self._volume,}
        return str(to_ret)
    
    def feature_vector(self)-> list:
        return [self._open , self._high , self._low , self._close , self._volume]


class Coin_creator:
    
    def Coin_from_binance(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],raw_data[2],raw_data[3],raw_data[4],raw_data[5],raw_data[6],raw_data[7])

    def Coin_from_CSV(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],float(raw_data[2]),float(raw_data[3]),float(raw_data[4]),float(raw_data[5]), float(raw_data[6]))
    
    def Coin_from_DB(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],float(raw_data[2]),float(raw_data[3]),float(raw_data[4]),float(raw_data[5]), float(raw_data[6]))


"""List with max len"""

class list_max_len:

    def __init__(self, max_len) -> None:
        self._list = []
        self._max_len = max_len

    def access_list(self):
        return self._list

    def add(self, newel):
        if len(self._list) < self._max_len:
            self._list.append(newel)
        else:
            self._list.pop(0)
            self._list.append(newel)


hostname = "bigdatapostgres-federicozilli-bf3a.aivencloud.com"
database = "CRYPTODB"
username = "avnadmin"
pswrd = "AVNS_1owyZsR6_lLL93247eQ"
port_id = 18580

conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)

cur = conn.cursor()

coins_list = ["BTC" , "ETH"]

while True:
    # selecting all the data from the table
    for coin in coins_list:
        # cur.execute("SELECT * FROM " + coin)
        cur.execute("select * from "+coin+" ORDER BY id DESC LIMIT 10080") # last 10080 observations = last 7 days
        all = cur.fetchall()

        all = [Coin_creator.Coin_from_DB(el).feature_vector() for el in all]
        #all.reverse()

        data = pd.DataFrame(all, columns = ["open" , "high" ,"low", "close", "volume"])
        
        projection = 10 # 10 minutes ahed
        y = data["close"].shift(-projection).values[:-projection]
        x = data[["open" , "high" ,"low", "close", "volume"]].values[:-projection]

        # y = y[-7200:]
        # x = x[-7200:] 

        lin_reg = LinearRegression(normalize=True)

        lin_reg.fit(x,y)

        coefficients = lin_reg.coef_
        intercept = lin_reg.intercept_

        to_insert = "INSERT INTO "+coin+"_coef VALUES ("+ str(intercept) +", ARRAY %s )" %str(list(coefficients))
        print(to_insert)
        
        cur.execute(to_insert)

    conn.commit()
    time.sleep(3600)





