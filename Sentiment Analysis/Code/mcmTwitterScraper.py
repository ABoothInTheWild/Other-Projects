# -*- coding: utf-8 -*-
"""
Spyder Editor

Author: Alexander Booth, t2adb
Team: Found Visualize
Date: 11/29/2017

This script scrapes tweets from the Twitter API and writes them to a csv
Since the Twitter API only stores tweets less than a week old, this should be 
run daily or at least weekly

Future Work: Add a stream listener instead of making it a task

Run from the python or cmd command line to suppress warnings:
python -W ignore "K:\t2adb\Sentiment Analysis\Code\mcmTwitterScraper.py"
"""

#Imports
import tweepy
import pandas as pd
import numpy as np
import os

#Set directory
os.chdir("K:\t2adb\Sentiment Analysis\Code")

#Load twitter credentials
from twitCredentials import *
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#Ignore tweets with these words in the text
nix = ['RT @', 'trump', 'Trump', "H.R.", "@McMasterU", "Flynn"]
matrix = []

#Load up current tweets so we don't write them twice if they are still in scope
curr = pd.read_csv(r"mcmTweets.csv", encoding='latin-1')
ids = np.unique(curr.TweetID)

#Search for tweets containing these tags
tags = ["@McMasterCarr", "mcmaster carr", "mcmaster.com", "mcmastercarr"]
for tag in tags:
    c = tweepy.Cursor(api.search, q=tag, tweet_mode='extended', include_entities=True).items(100)
    for tweet in c:
        if not tweet.retweeted and not any(substring in tweet._json["full_text"] for substring in nix):
            url = ""
            if tweet.entities["urls"]:
                if tweet.entities["urls"][0]["expanded_url"]:
                    url = tweet.entities["urls"][0]["expanded_url"]
            if not tweet.id in ids: 
                #Add columns that we want to track
                matrix.append([tweet.id,
                tweet.created_at,
                tweet.user.screen_name,
                tweet.user.name,
                tweet.user.verified,
                tweet.user.location,
                tweet.full_text,
                url,
                tweet.favorite_count,
                tweet.retweet_count])
                ids = np.append(ids, tweet.id)
#Create dataframe
if matrix:
    columnNames = ["TweetID", "CreatedAt", "User_ScreenName", "User_Name", "User_IsVerified",
                   "User_Loc", "Tweet_Text", "Tweet_Urls", "Tweet_FavCount", "Tweet_RTCount"]
    df = pd.DataFrame(matrix)
    df.columns = columnNames
    try:
        #Try to encode properly without breaking
        for i in range(0, len(df)):
            df.Tweet_Text[i] = df.loc[i].Tweet_Text.encode('cp850','replace').decode('cp850')
            df.User_Name[i] = df.loc[i].User_Name.encode('cp850','replace').decode('cp850')
        with open('mcmTweets.csv', 'a') as f:
            f.write('\n')
            df.to_csv(f, header=False, index=False)
            f.close()
    except Exception as e:
        print(e)

#Fin