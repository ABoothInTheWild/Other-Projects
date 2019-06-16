# https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c
# https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f
# https://github.com/cjhutto/vaderSentiment
# http://docs.tweepy.org/en/latest/streaming_how_to.html
# https://towardsdatascience.com/extracting-twitter-data-pre-processing-and-sentiment-analysis-using-python-3-0-7192bd8b47cf

#Imports
import tweepy
import pandas as pd
import numpy as np
import os
import time
import sys
import requests
import json
import random
from datetime import datetime, timezone
from listenerOverride import *
from tweepy import Stream
from dateutil.parser import *
from textblob import TextBlob
import matplotlib.pyplot as plt
import nltk
import re

#Sentiment analysis Imports
from textblob import TextBlob
import matplotlib.pyplot as plt
import nltk
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

#Load twitter credentials
from credentials import *
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
myListener = StdOutListener()
stream = Stream(auth, myListener)

def findWordinStream(stream, myListener, word, stopWords, counter=0):
    rtnBool = False
    stream.filter(track=[word], languages=['en'])
    if word.lower() in myListener.foundStatus.lower() and not any(x.lower() in myListener.foundStatus.lower().strip().split() for x in stopWords):
        rtnBool = True
    elif counter < 50:
        print(myListener.foundStatus.lower().strip().split())
        time.sleep(5)
        rtnBool = findWordinStream(stream, myListener, word, stopWords, counter + 1)
    else:
        print("Exceeded maximum tries for some reason for word " + word)
        rtnBool = False
    return rtnBool

#Tokenize Sentences properly
def format_sentence(sent):
    return({word: True for word in nltk.word_tokenize(sent)})

#Simple Function to Clean Tweets
def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters,
    and usernames using simple regex statements.
    '''
    tweet = tweet.lower().strip()
    return ' '.join(re.sub("(@[A-Za-z0-9_]+)|([^0-9A-Za-z'\-])|(\w+:\/\/\S+)", " ", tweet).split())

#Leave caps and emojiis for VADER
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt

def clean_tweet2(tweet):
    # Happy Emoticons
    emoticons_happy = set([
        ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
        ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
        '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
        'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
        '<3'
        ])
    # Sad Emoticons
    emoticons_sad = set([
        ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
        ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
        ':c', ':{', '>:\\', ';('
        ])
    #combine sad and happy emoticons
    emoticons = emoticons_happy.union(emoticons_sad)
    #Emoji patterns
    emoji_pattern = re.compile("["
             u"\U0001F600-\U0001F64F"  # emoticons
             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
             u"\U0001F680-\U0001F6FF"  # transport & map symbols
             u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
             u"\U00002702-\U000027B0"
             u"\U000024C2-\U0001F251"
             "]+", flags=re.UNICODE)
    
    # remove twitter Return handles (RT @xxx:)
    tweet = remove_pattern(tweet, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    tweet = remove_pattern(tweet, "@[\w]*")
    # remove URL links (httpxxx)
    tweet = remove_pattern(tweet, "https?://[A-Za-z0-9./]*")
    return tweet
    #don't remove emojiis, or send to lower for VADER processing

def DoWork(tag, limit):
    #Ignore tweets with these words in the text
    stopWords = ['RT @']
    matrix = []
    limit = int(limit)
    #Load up current tweets so we don't write them twice if they are still in scope
    tweetsDB = "tweets.json"
    r = requests.get(FB_URL + tweetsDB)
    r = r.json()
    keys = []
    ids = []
    if r:
        data = [r[i] for i in r]
        df = pd.DataFrame.from_dict(data, orient='columns')
        ids = np.unique(df.TweetID)
        tags = np.unique([x.lower() for x in df['Tag']])
        keys = [(row.TweetID, row.Tag) for index, row in df.iterrows()] #clustered primary key

    pages = tweepy.Cursor(api.search, q=tag, tweet_mode='extended', include_entities=True, lang='en').pages(limit)
    for page in pages:
        for tweetData in page:
            tweet = tweetData.__dict__
            if not tweet["retweeted"] and not any(substring in tweet["_json"]["full_text"] for substring in stopWords):
        #endtime=time.time()+500.0 #1minute
        #while (time.time()<endtime):
        #    if findWordinStream(stream, myListener, tag, stopWords):
                #tweet = myListener.foundTweetData
                if not (tweet["id_str"], tag) in keys:
                    #included URLS
                    url = ""
                    hashtags = ""
                    if tweet["entities"]["urls"]:
                        if tweet["entities"]["urls"][0]["expanded_url"]:
                            url = tweet["entities"]["urls"][0]["expanded_url"]
                    if tweet['entities']['hashtags']:
                        hashtags = "|".join([hashtag_item['text'] for hashtag_item in tweet['entities']['hashtags']]) #concat on pipe
                    #Add columns that we want to track            
                    tweetLink = "https://twitter.com/" + tweet["user"].__dict__["screen_name"] + "/status/" + tweet["id_str"]
                    matrix.append([tweet["id_str"],
                    tweet["created_at"],
                    tweet["user"].__dict__["screen_name"],
                    tweet["user"].__dict__["name"],
                    tweet["user"].__dict__["verified"],
                    tweet["user"].__dict__["location"],
                    tweet["_json"]["full_text"],            
                    url,
                    tweet["favorite_count"],
                    tweet["retweet_count"],
                    tweetLink,
                    hashtags])
                    ids = np.append(ids, tweet["id_str"])
                #sleep(5)

    #Create dataframe
    if matrix:
        columnNames = ["TweetID", "CreatedAt", "User_ScreenName", "User_Name", "User_IsVerified",
                    "User_Loc", "Tweet_Text", "Tweet_Urls", "Tweet_FavCount", "Tweet_RTCount", "Tweet_Link", "Hashtags"]
        df = pd.DataFrame(matrix)
        df.columns = columnNames
    df["Tag"] = tag
    #df["CreatedAtLocal"] = [parse(created).replace(tzinfo=timezone.utc).astimezone(tz=None) for created in df.CreatedAt]
    df["CreatedAtLocal"] = df.CreatedAt.dt.tz_localize('utc').dt.tz_convert('US/Central')
    df["Clean_Date"] = [datetime.strftime(created, '%D %I:%M%p') for created in df.CreatedAtLocal]
    df['CreatedAt'] = df['CreatedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['CreatedAtLocal'] = df['CreatedAtLocal'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df["Clean_Text"] = [clean_tweet(i) for i in df.Tweet_Text]
    df["Less_Clean_Text"] = [clean_tweet2(i) for i in df.Tweet_Text]
    df["Sentiment"] = [TextBlob(cleanedTweet).sentiment.polarity for cleanedTweet in df.Clean_Text]
    df["Sentiment_VADER"] = [analyser.polarity_scores(cleanedTweet)["compound"] for cleanedTweet in df.Less_Clean_Text]
    df["Sentiment_Comb"] = (df.Sentiment + df.Sentiment_VADER) / 2

    df.sort_values(by='CreatedAtLocal', inplace=True)
    df.reset_index(inplace=True, drop=True)

    #Save to database
    # for x in range(0, len(df)):
    #     tweet = df.iloc[x]
    #     db_tweet = tweet.to_json()
    #     requests.post(FB_URL + tweetsDB, db_tweet) #slow, fix this

    import firebase_admin
    from firebase_admin import db

    ref = db.reference('tweets')
    [ref.push(tweet.to_dict()) for index, tweet in df.iterrows()]

    return "Done"

def GetRollingMeans(df, vader=True):
    #Plot
    vader = True
    if vader:
        df["rolling_mean"] = df.Sentiment_VADER.rolling(window=20).mean()#.fillna(0)
        df["rolling_mean2"] = df.Sentiment_VADER.rolling(window=50).mean()#.fillna(0)
    else:
        df["rolling_mean"] = df.Sentiment.rolling(window=20).mean()#.fillna(0)
        df["rolling_mean2"] = df.Sentiment.rolling(window=50).mean()#.fillna(0)
    return df
 
def DoWorkForUserTwitter(userName, count):
    #Ignore tweets with these words in the text
    stopWords = ['RT @']
    matrix = []
    count = int(count)
    #Load up current tweets so we don't write them twice if they are still in scope
    tweetsDB = "tweets.json"
    r = requests.get(FB_URL + tweetsDB)
    r = r.json()
    keys = []
    ids = []
    if r:
        data = [r[i] for i in r]
        df = pd.DataFrame.from_dict(data, orient='columns')
        ids = np.unique(df.TweetID)
        tags = np.unique([x.lower() for x in df['Tag']])
        keys = [(row.TweetID, row.Tag) for index, row in df.iterrows()] #clustered primary key

    tweets = api.user_timeline("@" + userName, count=count, tweet_mode='extended', include_entities=True, lang='en')
    for tweetData in tweets:
        tweet = tweetData.__dict__
        if not tweet["retweeted"] and not any(substring in tweet["_json"]["full_text"] for substring in stopWords):
    #endtime=time.time()+500.0 #1minute
    #while (time.time()<endtime):
    #    if findWordinStream(stream, myListener, tag, stopWords):
            #tweet = myListener.foundTweetData
            if not (tweet["id_str"], userName) in keys:
                #included URLS
                url = ""
                hashtags = ""
                if tweet["entities"]["urls"]:
                    if tweet["entities"]["urls"][0]["expanded_url"]:
                        url = tweet["entities"]["urls"][0]["expanded_url"]
                if tweet['entities']['hashtags']:
                    hashtags = "|".join([hashtag_item['text'] for hashtag_item in tweet['entities']['hashtags']]) #concat on pipe
                #Add columns that we want to track            
                tweetLink = "https://twitter.com/" + tweet["user"].__dict__["screen_name"] + "/status/" + tweet["id_str"]
                matrix.append([tweet["id_str"],
                tweet["created_at"],
                tweet["user"].__dict__["screen_name"],
                tweet["user"].__dict__["name"],
                tweet["user"].__dict__["verified"],
                tweet["user"].__dict__["location"],
                tweet["_json"]["full_text"],            
                url,
                tweet["favorite_count"],
                tweet["retweet_count"],
                tweetLink,
                hashtags])
                ids = np.append(ids, tweet["id_str"])
            #sleep(5)

    #Create dataframe
    if matrix:
        columnNames = ["TweetID", "CreatedAt", "User_ScreenName", "User_Name", "User_IsVerified",
                    "User_Loc", "Tweet_Text", "Tweet_Urls", "Tweet_FavCount", "Tweet_RTCount", "Tweet_Link", "Hashtags"]
        df = pd.DataFrame(matrix)
        df.columns = columnNames
    df["Tag"] = userName
    #df["CreatedAtLocal"] = [parse(created).replace(tzinfo=timezone.utc).astimezone(tz=None) for created in df.CreatedAt]
    df["CreatedAtLocal"] = df.CreatedAt.dt.tz_localize('utc').dt.tz_convert('US/Central')
    df["Clean_Date"] = [datetime.strftime(created, '%D %I:%M%p') for created in df.CreatedAtLocal]
    df['CreatedAt'] = df['CreatedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['CreatedAtLocal'] = df['CreatedAtLocal'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df["Clean_Text"] = [clean_tweet(i) for i in df.Tweet_Text]
    df["Less_Clean_Text"] = [clean_tweet2(i) for i in df.Tweet_Text]
    df["Sentiment"] = [TextBlob(cleanedTweet).sentiment.polarity for cleanedTweet in df.Clean_Text]
    df["Sentiment_VADER"] = [analyser.polarity_scores(cleanedTweet)["compound"] for cleanedTweet in df.Less_Clean_Text]
    df["Sentiment_Comb"] = (df.Sentiment + df.Sentiment_VADER) / 2

    df.sort_values(by='CreatedAtLocal', inplace=True)
    df.reset_index(inplace=True, drop=True)

    #Save to database
    # for x in range(0, len(df)):
    #     tweet = df.iloc[x]
    #     db_tweet = tweet.to_json()
    #     requests.post(FB_URL + tweetsDB, db_tweet) #slow, fix this

    import firebase_admin
    from firebase_admin import db

    ref = db.reference('tweets')
    [ref.push(tweet.to_dict()) for index, tweet in df.iterrows()]

    return "Done"