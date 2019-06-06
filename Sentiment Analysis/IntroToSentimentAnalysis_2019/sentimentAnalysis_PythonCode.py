# -*- coding: utf-8 -*-
"""
Spyder Editor

Author: Alexander Booth
Date: January 25, 2018

Intro to Sentiment Analysis in Python

This script examines the TextBlob lexicon and how it deals with bi and trigrams

Then a quick introduction to the Naive Bayes Classifier and a
"bag-of-words" model

Finally, we train and test these two methods on tweets to predict positive
and negative sentiment
"""

#Imports
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir("C:/Users/abooth/Documents/Docs/SMU/SentimentAnalysis")
############################################################
#Chapter 0: Introduction to TextBlob Sentiment

#Reference and Lexicon
#https://planspace.org/20150607-textblob_sentiment/
#https://github.com/sloria/TextBlob/blob/eb08c120d364e908646731d60b4e4c6c1712ff63/textblob/en/en-sentiment.xml

#Baseline
print(TextBlob("nice").sentiment) #0.6
#"Not" multiplies polarity by -0.5
print(TextBlob("not nice").sentiment) #-0.3
#Very multiplies polarity by 1.3
print(TextBlob("very nice").sentiment) #0.78
#Multiplies polarity by -0.5 * (1/1.3)
print(TextBlob("not very nice").sentiment) #-0.23
#Ignores single letter words
print(TextBlob("not a very nice").sentiment) #-0.23
#Ignores neutral words
print(TextBlob("not a very nice description").sentiment) #-0.23

############################################################
# Chapter 1: Bee Movie
f = open('beeMovieScript.txt','r')
beeMovie = f.readlines()
beeMovie = [s.strip() for s in beeMovie]

#Get chunks of 20 lines and their sentiments
beeSentiments = []
i = 0
while i < 1360:
    chunk = " ".join(beeMovie[i:(i+20)])
    beeSentiments.append(TextBlob(chunk).sentiment.polarity * 100)
    i += 20

#Create dataframe
beeIndx = range(0,1359,20)
beeDf = pd.DataFrame({'beeIndx' : beeIndx, 'beeSentiment' : beeSentiments})

#Plot
ax = beeDf.plot(x = 'beeIndx', y='beeSentiment', kind='bar', title ="Bee Movie Sentiment", figsize=(15, 10), legend=False, fontsize=12)
ax.set_xlabel("Bee Movie Line Index", fontsize=12)
ax.set_ylabel("Sentiment", fontsize=12)
plt.show()

#Compare to the one produced in R
#Negative chunks correspond to negative or stressful parts of the movie

############################################################

#Chapter 2, Machine Learning on Tweets

#Part 1: Naive Bayes Classifier and Bag-Of-Words Model

#References:
#https://en.wikipedia.org/wiki/Naive_Bayes_classifier
#https://en.wikipedia.org/wiki/Bag-of-words_model
#https://www.twilio.com/blog/2017/09/sentiment-analysis-python-messy-data-nltk.html
#https://pythonspot.com/python-sentiment-analysis/
#https://github.com/lesley2958/natural-language-processing

#Imports
import nltk
import re

#Tokenize Sentences properly
def format_sentence(sent):
    return({word: True for word in nltk.word_tokenize(sent)})

print(format_sentence("This cat isn't very cute"))

#Simple Function to Clean Tweets
def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters,
    and usernames using simple regex statements.
    '''
    tweet = tweet.lower().strip()
    return ' '.join(re.sub("(@[A-Za-z0-9_]+)|([^0-9A-Za-z'\-])|(\w+:\/\/\S+)", " ", tweet).split())

#Get Training data, an assortment of positive and negative tweets   
pos = []
with open(r"pos_tweets.txt", encoding="utf8") as f:
    for i in f:
        cleanedTweet = format_sentence(clean_tweet(i))
        pos.append([cleanedTweet, 'pos'])
        
neg = []
with open(r"neg_tweets.txt", encoding="utf8") as f:
    for i in f:
        cleanedTweet = format_sentence(clean_tweet(i))
        neg.append([cleanedTweet, 'neg'])       

#Great, ~600 positive tweets and ~1300 negative tweets

# next, split labeled data into the training and test data
training = pos[:int((.8)*len(pos))] + neg[:int((.8)*len(neg))]
test = pos[int((.2)*len(pos)):] + neg[int((.2)*len(neg)):]

#Now time to create our model
from nltk.classify import NaiveBayesClassifier
 
classifier = NaiveBayesClassifier.train(training)
classifier.show_most_informative_features()

#Basically, word frequencies are identified in each bag.
#While any given word is likely to be found somewhere in both bags, the "pos" 
#bag will contain positive-related words such as "love", "great" much more frequently, 
#while the negative bag will contain more words like "hate" and "awful"

#To classify a tweet, the Bayesian Classifier assumes that the message is a pile
#of words that has been poured out randomly from one of the two bags, and uses 
#Bayesian probability to determine which bag it is more likely to be.

example1 = "Graham is awesome!" 
print(classifier.classify(format_sentence(clean_tweet(example1))))

example2 = "Graham is awful." 
print(classifier.classify(format_sentence(clean_tweet(example2))))

#Does not take into account negation, so likely to not be perfect
example3 = "Graham is not awful!" 
print(classifier.classify(format_sentence(clean_tweet(example3))))

#Got to measure our accuracy
from nltk.classify.util import accuracy
print(accuracy(classifier, test))

#Time to take it for a spin on tweets about Trump
#https://www.dataquest.io/blog/matplotlib-tutorial/
df_full = pd.read_csv("tweets.csv")

def get_candidate(row):
    candidates = []
    text = row["text"].lower()
    if "clinton" in text or "hillary" in text:
        candidates.append("clinton")
    if "trump" in text or "donald" in text:
        candidates.append("trump")
    if "sanders" in text or "bernie" in text:
        candidates.append("sanders")
    return ",".join(candidates)
df_full["candidate"] = df_full.apply(get_candidate,axis=1)
df = df_full[df_full.candidate == "trump"] #may 2016
df = df[df.text.str.startswith("RT ")==False] #filter RTs for the most part

sentiments = []
for tweetText in df.text:
    cleanedTweet = format_sentence(clean_tweet(tweetText))
    sentiments.append(classifier.classify(cleanedTweet))

df["Sentiments"] = sentiments

print(len(df[df.Sentiments == 'pos']))
print(len(df[df.Sentiments == 'neg']))

#Do not have a neutral!
#Could train on a dataset of neutral tweets, but do not have that data :(

#Print some tweets
for niceTweet in df[df.Sentiments == 'pos']["text"][0:5]:
    print(niceTweet)
    print("")


for sadTweet in df[df.Sentiments == 'neg']["text"][0:5]:
    print(sadTweet)
    print("")
    
#TextBlob provides a numeric polarity. Let's look at our tweets with that

#Part 2: TextBlob
sentimentsTB = []
for tweetText in df.text:
    cleanedTweet = clean_tweet(tweetText)
    sentiment = TextBlob(cleanedTweet).sentiment.polarity
    if sentiment > 0:
        sentimentsTB.append("pos")
    elif sentiment < 0:
        sentimentsTB.append("neg")
    elif sentiment == 0:
        sentimentsTB.append("neu")
    
df["Sentiments_TB"] = sentimentsTB

print(len(df[df.Sentiments_TB == 'pos']))
print(len(df[df.Sentiments_TB == 'neg']))
print(len(df[df.Sentiments_TB == 'neu']))

#That looks a lot better

for niceTweet in df[df.Sentiments_TB == 'pos']["text"][0:5]:
    print(niceTweet)
    print("")


for sadTweet in df[df.Sentiments_TB == 'neg']["text"][0:5]:
    print(sadTweet)
    print("")
    
#Fin
