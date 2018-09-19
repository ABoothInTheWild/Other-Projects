# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 20:29:18 2018

@author: Alexander
"""

#imports
import json
from tweepy.streaming import StreamListener
from time import sleep

#Listener Class Override
class StdOutListener(StreamListener):
    #Inits
    foundStatus = ""
    foundTweetData = ""
    foundScreenName = ""
    foundTweetId = ""
    foundTweetLink = ""

    def GetLink(self):
       return "https://twitter.com/" + self.foundScreenName + "/status/" + self.foundTweetId

    #Functions
    def on_data(self, data):
        try:
            tweetData = json.loads(data)
            #make sure tweet is not retweet or quote
            if "retweeted_status" not in tweetData and 'quoted_status' not in tweetData:
                #load data
                self.foundTweetData = tweetData
                self.foundScreenName = tweetData["user"]["screen_name"]
                self.foundTweetId = tweetData["id_str"]
                self.foundTweetLink = self.GetLink()
                #print("*****************************************")
                #Get Tweet Text
                if "extended_tweet" in tweetData:
                    #print(tweetData["extended_tweet"]["full_text"])
                    self.foundStatus = tweetData["extended_tweet"]["full_text"]
                else:
                    #print(tweetData['text'])
                    self.foundStatus = tweetData['text']
                #returning False in on_data disconnects the stream
                return False
            else:
                #ignore this tweet and continue listening
                pass
        except BaseException as e:
            print('failed ondata,', str(e))
            return True # To continue listening

    def on_error(self, status):
        print(status)
        if status == 420:
            sleep(120)
            return False # To continue listening
        else:
            sleep(10)
            return False # To continue listening

    def on_timeout(self):
        sleep(120)
        return True # To continue listening

####################################################################
def findWordinStream(stream, myListener, word, stopWords, counter=0):
    rtnBool = False
    stream.filter(track=[word], languages=['en'])
    if word.lower() in myListener.foundStatus.lower() and not any(x.lower() in myListener.foundStatus.lower().strip().split() for x in stopWords):
        rtnBool = True
    elif counter < 50:
        print(myListener.foundStatus.lower().strip().split())
        sleep(5)
        rtnBool = findWordinStream(stream, myListener, word, stopWords, counter + 1)
    else:
        print("Exceeded maximum tries for some reason for word " + word)
        rtnBool = False
    return rtnBool