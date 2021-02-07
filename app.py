from flask import Flask, render_template, abort, request
import sys
from twython import Twython
import os
 
from dictionary import Dictionary
from textblob import TextBlob
import pymongo
import json 
import tweepy

file1 = open("MyFile.txt","a")

ckey = 'L755C7WuPy7AFnsscuONQHF9z'
csecret = 'TCUnmYXv1L9TuKV6Lzk0ofxwh1LAGIqSvDua9vwFH1zMYGUVQn'

atoken = '1046944742393561088-uXi4ER6gyotBuxZ8orhbpbl8BVd4En'
asecret = 'SFad097p9NTAOFb2JwZED6XZ4tVhKiD6x9urIIYdDafB6' 


client = pymongo.MongoClient("mongodb://localhost:27017/") 
  
 
db = client["db_twitter"] 
  
 

app = Flask(__name__)


 

class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets,count_pos,count_neg,count_subj):

        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets
        self.count_pos = count_pos
        self.count_neg = count_neg
        self.count_subj = count_subj
         

        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)
        self.length_pos = list(range(1, len(positive_tweets)+1))




def get_all_tweets(screen_name):
     
    #db = client.db_twitter
    
    collec='Tweets'+screen_name[1:] 
    tweets = db[collec] 
    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    api = tweepy.API(auth)

 
    alltweets = []
    new_tweets = api.user_timeline(screen_name=screen_name, count=100)
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:
        new_tweets = api.user_timeline(screen_name=screen_name, count=100, max_id=oldest)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1


    for tweet in alltweets:
         
        blob =TextBlob(tweet.text)
        languageTweet = blob.detect_language()  
        #if languageTweet != 'en': 
             
            #blob = blob.translate( to='en')
             
                 

        tweets.create_index("text", unique=True)
         
         
        mydict = { "text" : str(blob)  }
        tweets.insert_one(mydict)
     
    client.close()


 

def sentiment(tweet):

    blob = TextBlob(tweet)
    return blob.sentiment 
     
     

def sentiment_analysis(tweets):

    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []
    count_pos = []
    count_neg = []
    count_subj = []
    

    for tweet in tweets:
        file1.write(tweet.text)
        res = sentiment(tweet.text)
        count_subj.append(res[1])

        if res[0] < 0:
            negative_tweets.append(tweet.text )
            count_neg.append(res[0])
        elif res[0] > 0:
            positive_tweets.append(tweet.text )
            count_pos.append(res[0])
        else:
            neutral_tweets.append(tweet.text )

    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets,count_pos,count_neg,count_subj)


@app.route("/", methods=["POST","GET"])
def root():

    if request.method == "POST":
        
        #tusername=str(request.form['twitter_username'])
        #dbname = "Tweets"+tusername[1:]
         
        #get_all_tweets(request.form['twitter_username'])
                    
        #col = db[dbname] 
  
  
        #jsondata = col.find({},{'_id': 0,'text': 1  })

        #tweets=[]  
        #for data in jsondata:
            #tweetstr = json.dumps(data) 
            #tweetstr = tweetstr[10: -2]
            #tweets.append(tweetstr)
        auth = tweepy.OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        api = tweepy.API(auth)
        screen_name=request.form['twitter_username']     
        alltweets = []
        new_tweets = api.user_timeline(screen_name=screen_name, count=100)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        while len(new_tweets) > 0:
            new_tweets = api.user_timeline(screen_name=screen_name, count=100, max_id=oldest)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
        return render_template("result.html", result=sentiment_analysis(alltweets), username=request.form['twitter_username']  )
    else:
        return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
     
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
