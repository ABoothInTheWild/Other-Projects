# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 20:17:57 2018

@author: Alexander
"""

# Twitter Bot

# Imports
# prepare for Python version 3x features and functions
from __future__ import division, print_function
import re
from textblob import TextBlob
import urllib
from twitterBot import *
import pandas as pd
import io

class JaneAustenWrites(TwitterBot):

    #inits
    screen_name = "AustenWrites"
    retweetTags = []
    favoriteTags = ["jane austen", "england", "mr darcy", "pride and prejudice"]
    followTags = ["jane austen", "england", "mr darcy", "pride and prejudice"]
    logFile = screen_name + "_log.txt"
    dataFile = screen_name + "_DataFound.txt"

    #Data
    target_url = "http://www.gutenberg.org/cache/epub/42671/pg42671.txt"
    raw = urllib.urlopen(target_url).read().replace("\xe2\x80\x99","'")
    cleanTxt = re.sub(r'[^\x00-\x7f]',r'', raw)
    cleanTxt = cleanTxt.replace("_", "")
    cleanTxt = cleanTxt.replace("*", "")
    cleanTxt = cleanTxt.replace("-", " ")
    cleanTxt = cleanTxt.replace("&", "and")
    cleanTxt = cleanTxt.replace("o morrow", "omorrow")
    cleanTxt = ' '.join(cleanTxt.split())

    start = "PRIDE and PREJUDICE."
    end = "END OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE"
    truncTxt = start + re.search('%s(.*)%s' % (start, end), cleanTxt).group(1) + end
    myBlob = TextBlob(truncTxt)
    pride = myBlob.sentences
    stopWords = []
    with open('stopWords.csv', 'r') as f:
        for line in f.readlines():
            l = line.split(',')
            stopWords.append(l[0])

    #Update these if restarting based on log
    currSentence = 2
    currWord = 15

    def getStatus(self):
        status = "I hope you have a great day!"

        sentence = str(self.pride[self.currSentence]).strip().split()
        word = sentence[self.currWord]
        cleanWord = re.sub(r"[^\w']", '', word).strip().lower()
        f = open(self.logFile,'a')
        f.write('\n' + 'Looking for word: ' + cleanWord)
        f.close()
        if findWordinStream(self.stream, self.myListener, cleanWord, self.stopWords):
            status = word + " " + self.myListener.foundTweetLink
            f = io.open(self.dataFile,'a', encoding="utf-8")
            f.write(word + ',' + self.myListener.foundStatus.encode("utf8") + ',' + self.myListener.foundScreenName.encode("utf8") + ',' + str(self.myListener.foundTweetId) + ',' + self.myListener.foundTweetLink + '\n')
            f.close()

        if (self.currWord == (len(sentence) - 1)):
            self.currSentence += 1
            self.currWord = 0
        else:
            self.currWord += 1
        f = open(self.logFile,'a')
        f.write('\n' + 'Found! New Current Sentence: ' + str(self.currSentence) + " New Current Word: " + str(self.currWord))
        f.close()
        return status

    def Disconnect(self):
        self.stream.disconnect()