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

class JaneAustenWrites(TwitterBot):
    
    #inits
    screen_name = "AustenWrites"
    retweetTags = []
    favoriteTags = ["jane austen"]
    followTags = ["jane austen"]
    logFile = screen_name + "_log.txt"
    
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
    currSentence = 0
    currWord = 0

    def getStatus(self):
        status = "I hope you have a great day!"
        
        sentence = str(self.pride[self.currSentence]).strip().split()
        word = sentence[self.currWord]
        cleanWord = re.sub(r"[^\w']", '', word).strip().lower()
        if findWordinStream(self.stream, self.myListener, cleanWord):
            status = word + " " + self.myListener.foundTweetLink 
        
        if (self.currWord == (len(sentence) - 1)):
            self.currSentence += 1
            self.currWord = 0
        else:
            self.currWord += 1
        f = open(self.logFile,'a')
        f.write('\n' + 'Current Sentence: ' + str(self.currSentence) + " Current Word: " + str(self.currWord))
        f.close()
        return status
    
    def Disconnect(self):
        self.stream.disconnect()