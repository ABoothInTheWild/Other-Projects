# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 14:04:41 2017

@author: Alexander Booth
"""

import time
import nltk
import string
import re
import os
import json

from nltk.tokenize.moses import MosesDetokenizer
detokenizer = MosesDetokenizer()

def tokenizeProperly(myString):
    return nltk.word_tokenize(detokenizer.detokenize(myString, return_str=True))

def createSentenceFromGutenSent(sentence):
    words = tokenizeProperly(sentence)
    
    returnStr = words[0]
    
    for x in range(1, len(words)):
        
        if re.match("^[A-Za-z0-9_-]*$", words[x]) and  returnStr in string.punctuation:
            returnStr = "".join(returnStr+""+words[x])
        
        elif re.match("^[A-Za-z0-9_-]*$", words[x]):
            returnStr = "".join(returnStr+" "+words[x])
        
        elif (words[x].startswith("'")) and (len(words[x]) > 1):
            returnStr = "".join(returnStr+""+words[x])
        
        elif words[x] in string.punctuation:
            returnStr = "".join(returnStr+""+words[x])
    
    return returnStr


#"".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in words])
    
    
alice = nltk.corpus.gutenberg.sents('carroll-alice.txt')

for x in range(0,10):
    print(createSentenceFromGutenSent(alice[x]))


createSentenceFromGutenSent(alice[3])


words = tokenizeProperly(alice[3])

re.sub(r'[^\w\s]', '', returnStr).strip()


#Listener Class Override
class StdOutListener(StreamListener):

    def on_data(self, data):
        try:
            tweetText = json.loads(data)['text']
            if "trump" in re.sub(r'[^\w\s]', '', tweetText).strip():
                print(tweetText)
                return False
        except BaseException as e:
            #print('failed ondata,', str(e))
            return True

    def on_error(self, status):
        print(status)
        if status == 420:
            #returning False in on_data disconnects the stream
            return False

import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
from twitCredentials import *
l = StdOutListener()
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
stream = Stream(auth, l)

quote = "Trump is an orange"
#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
stream.filter(track=["the"], languages=['en'])
