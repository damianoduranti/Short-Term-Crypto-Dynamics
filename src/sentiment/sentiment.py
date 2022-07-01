import os
import json
import tweepy 
import json
import textblob 
import time
import psycopg2
from kafka import KafkaProducer
import json

api_key = "G5fb3JHnxGxNaWkv1knLy0aXf"
api_secret = "9t71GuX9Usw2vtbrTzQshSBYyvv4HjolzNnLuhuxjKcIHTqB5t"
bearer_token = "AAAAAAAAAAAAAAAAAAAAABWcawEAAAAAt015sEVLzFcDFx8GwueLGgXEK08%3Deydp7U1eBbs1KpXnyr84j0Ma6aVSeKCyLCIiBlB6vs8dk33MNY"
access_token = "1508800983169736715-Nx6uZjXAJsmdw3wH0kqaTTc58O41dR"
access_token_secret = "Cb7ObCVzXbSj6trytDrJglJRVYNbV3JQY5NKl5nXzCKfL"
auth = tweepy.OAuthHandler( api_key,api_secret )
auth.set_access_token(access_token, access_token_secret )
api = tweepy.API(auth, wait_on_rate_limit=True) #N.B. I omitted the " wait_on_rate_limit_notify = True " setting
#check:
if(api.verify_credentials):
    print("credentials verified")
    
producer = KafkaProducer(
    bootstrap_servers=[os.environ["KAFKA_HOST"]],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    api_version=(0, 11),
)

with open('symbols.json') as json_file:
    data = json.load(json_file)

coins = os.environ["COINS"].split(",")
    
keywords = {}  
for coin in coins:
    print(coin[:-4])
    keywords[coin[:-4]] = [obj for obj in data if obj['symbol']==coin[:-4]][0]['name']   
print(keywords)

hostname = "bigdatapostgres-federicozilli-bf3a.aivencloud.com"
database = "CRYPTODB"
username = "avnadmin"
pswrd = "AVNS_1owyZsR6_lLL93247eQ"
port_id = 18580

conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)

cur = conn.cursor()

while True:
    
    for coin in coins:
        keyword = keywords[coin[:-4]]
        number_tweets= 20
        tweets = tweepy.Cursor(api.search_tweets , q = keyword , count=number_tweets , tweet_mode = "extended").items(number_tweets)

        polarity = 0
        number = 0
        subj = 0
        for tweet in tweets:

            tweet = tweet._json

            text = tweet["full_text"]
            analysis = textblob.TextBlob(text)
            subj += analysis.subjectivity
            polarity += analysis.polarity
            number += 1

        msubj = subj/number
        mpol = polarity/number
        print(coin)
        print(msubj)
        print(mpol)
        print(" ")
        
        try:
            value = {'coin': coin, 'msubj': msubj, 'mpol': mpol}
            producer.send("Sentiment", value=value)
            producer.flush()
            print(value)
        except:
            pass
        
    time.sleep(3600)