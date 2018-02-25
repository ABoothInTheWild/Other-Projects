# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 14:11:23 2017

@author: Alexander
"""
#Imports
from tweepy.streaming import StreamListener
from tweepy import Stream, OAuthHandler
from time import sleep
import os
import json
import re
import urllib

os.chdir("C:/Users/Alexander/Documents/baseball/bot/Monkeys")

from twitCredentials import *

#################################################################

#Listener Class Override
class StdOutListener(StreamListener):
    #Inits
    foundStatus = ""
    foundTweetData = ""
    foundScreenName = ""
    
    #Functions
    def on_data(self, data):
        try:
            tweetData = json.loads(data)
            #make sure tweet is not retweet or quote
            if "retweeted_status" not in tweetData and 'quoted_status' not in tweetData:
                #load data
                self.foundTweetData = tweetData
                self.foundScreenName = tweetData["user"]["screen_name"]
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
def findWordinStream(stream, myListener, word, counter=0):
    rtnBool = False
    stream.filter(track=[word], languages=['en'])
    if word.lower() in myListener.foundStatus.lower():
        #print(word + " found!!!!!")
        rtnBool = True
    elif counter < 5:
        sleep(5)
        rtnBool = findWordinStream(stream, myListener, word, counter + 1)
    else:
        print("Exceeded maximum tries for some reason")
        rtnBool = False
    return rtnBool

####################################################################

# =============================================================================
# quote = "Trump isn't an orange."
# words = quote.split(" ")
# 
# #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
# for word in words:
#     cleanWord = re.sub(r"[^\w']", '', word).strip()
#     findWordinStream(stream, cleanWord)
#     sleep(5)
# 
# =============================================================================

target_url = "http://www.gutenberg.org/cache/epub/42671/pg42671.txt"    
raw = urllib.urlopen(target_url).read().replace("\xe2\x80\x99","'")
cleanTxt = re.sub(r'[^\x00-\x7f]',r'', raw)
cleanTxt = cleanTxt.replace("_", "")
cleanTxt = cleanTxt.replace("*", "")
cleanTxt = cleanTxt.replace("-", " ")
cleanTxt = cleanTxt.replace("o morrow", "omorrow")
cleanTxt = ' '.join(cleanTxt.split())

start = "PRIDE & PREJUDICE."
end = "END OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE"
truncTxt = re.search('%s(.*)%s' % (start, end), cleanTxt).group(1)

from textblob import TextBlob
myBlob = TextBlob(truncTxt)
pride = myBlob.sentences

#from getSentences import *
#alice2 = split_into_sentences(truncTxt)

myListener = StdOutListener()
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
stream = Stream(auth, myListener)

for sentence in pride[0:2]:
    for word in str(sentence).strip().split():
        cleanWord = re.sub(r"[^\w']", '', word).strip().lower()
        if findWordinStream(stream, myListener, cleanWord):
            print(word + " found in status made by " + myListener.foundScreenName + 
                  " which said " + myListener.foundStatus)
            print("*****************************************")
        sleep(5)
    
    
    
    