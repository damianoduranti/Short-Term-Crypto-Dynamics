import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import psycopg2
from datetime import datetime , timedelta, time
import time 
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# Initializing Website ----------------------------------------------------------------------------------------------
st.set_page_config(
    page_title = 'Real-Time Crypto Dashboard',
    page_icon = '📈',
    layout = 'wide'
)

st.title("Crypto asset short-term dynamics")

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

coins_df  = {"coins" :  ["BTC" ,"ETH"]}
coins_df = pd.DataFrame(coins_df)
chosen_coin = st.selectbox("Select the coin", pd.unique(coins_df["coins"]))

placeholder = st.empty()

# Credentials for the DB ----------------------------------------------------------------------------------------------

hostname = "bigdatapostgres-federicozilli-bf3a.aivencloud.com"
database = "CRYPTODB"
username = "avnadmin"
pswrd = "AVNS_1owyZsR6_lLL93247eQ"
port_id = 18580

conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)

cur = conn.cursor()

# Functions for model retrieval and prediction ----------------------------------------------------------------------------------
def my_model(coin):
    cur.execute("select * from "+coin+"_coef ORDER BY id DESC LIMIT 1")
    one = cur.fetchone()
    intercept , coefficients = int(one[0]) , np.array(one[1])
    model = LinearRegression(normalize=True)
    model.coef_ = coefficients
    model.intercept_= intercept
    return model

def extract_prediction(feature_vector, coin):
    model = my_model(coin)
    #feature_vector = [el * np.random.choice([0.99,1,1.01]) for el in feature_vector] # there is an added part for faking data streaming
    feature_vector = [int(el) for el in feature_vector]
    feature_vector = np.array(feature_vector).reshape(1,-1)
    to_ret = model.predict(feature_vector)
    return float(to_ret)

# Dataframe needed for plotting ----------------------------------------------------------------------------------------------

df = {"istant" :  "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20".split(","),
        "price" :  list(range(20)),
        "predicted" : list(range(20)) }

df = pd.DataFrame(df)

cur.execute("select * from %s ORDER BY id DESC LIMIT 10" %chosen_coin)
last10 = cur.fetchall()
last10_coins = [Coin_creator.Coin_from_DB(el) for el in last10 ]
last10_preds = [ extract_prediction(el.feature_vector(), chosen_coin) for el in last10_coins]
last10_preds.reverse()

last10_price = [Coin_creator.Coin_from_DB(el) for el in last10 ]
last10_price = [ el._open for el in last10_price]
last10_price.reverse()

moments = [datetime.combine(el._date,  el._time) for el in last10_coins]
moments.reverse()
istant_price = [el.strftime("%H:%M:%S") for el in moments]
istant_predicted = [el + timedelta(minutes=10) for el in moments]
istant_predicted = [el.strftime("%H:%M:%S") for el in istant_predicted]

prices = last10_price
predicted = last10_preds 
istant_price = istant_price 
istant_predicted = istant_predicted 

# Simulation of streaming data with a for loop ( we must use a while True in the final version)
for i in range(2000):
        
    # Transformations
    cur.execute("select * from %s ORDER BY id DESC LIMIT 1" %chosen_coin)
    one = cur.fetchone()    
    my_coin = Coin_creator.Coin_from_DB(one)    

    # Prediction
    feature_vector = my_coin.feature_vector()
    pred = extract_prediction(feature_vector, chosen_coin)

    # Plotting
    prices.pop(0)
    prices.append(my_coin._open) #  * np.random.choice([0.99,1,1.01])
    predicted.pop(0)
    predicted.append(pred)

    current_time = datetime.combine(my_coin._date,  my_coin._time) # timedelta(minutes=i) # since it does not change in this case i make it change

    istant_price.pop(0)
    istant_price.append(current_time.strftime("%H:%M:%S"))

    future_time = current_time + timedelta(minutes=10)
    istant_predicted.pop(0)
    istant_predicted.append(future_time.strftime("%H:%M:%S"))

    df["price"] = prices + [None]*10
    df["predicted"] = [None]*10 + predicted
    df["istant"] = istant_price + istant_predicted


    if my_coin._open < predicted[0]:
        adv = "BUY some " + chosen_coin + " 💸"
        desc = "UP 👆"
    elif my_coin._open == predicted[0]:
        adv = " DO NOTHING " + chosen_coin + "price will not change 😌"
        desc = "STAY CONSTANT 👉"
    else:
        adv = "SELL some " + chosen_coin + " 🤑"
        desc = "DOWN 👇"

    with placeholder.container():
    # create three columns
        kpi1, kpi2 = st.columns(2)

        # fill in those three columns with respective metrics or KPIs 
        kpi1.metric(label= chosen_coin + " openening price", value=my_coin._open) #  * np.random.choice([0.99,1,1.01])
        kpi2.metric(label= chosen_coin + " predicted closing price", value= predicted[0])

        kpi3, kpi4 = st.columns(2)
        kpi3.metric(label = "Our Advice is to:", value = "%s" %adv )
        kpi4.metric(label = " ", value =  chosen_coin + " will go %s in a minute" %desc )

        # create two columns for charts 
        # fig_col1,fig_col2 = st.columns(2)
        # with fig_col1:
        st.markdown("### Current price vs predicted one of " + chosen_coin)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["istant"],
            y=df["predicted"], name = "predicted price", line_shape='spline'))
        fig.add_trace(go.Scatter(
            x=df["istant"],
            y=df["price"], name = "current price", line_shape='spline'))

        st.write(fig)

    time.sleep(60)
