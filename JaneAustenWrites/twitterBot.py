# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 18:21:39 2017

@author: Alexander
"""

# Twitter Bot

# Imports
# prepare for Python version 3x features and functions
from __future__ import division, print_function
from time import sleep
import tweepy
import sys
import requests
import json
import random
from abc import ABCMeta, abstractmethod
import datetime
from listenerOverride import *
from tweepy import Stream

class TwitterBot(object):

    __metaclass__ = ABCMeta

    #Get time. Don't post in the middle of the night
    timeStart = datetime.datetime.strptime('7:00AM', "%I:%M%p").time()
    timeEnd = datetime.datetime.strptime('11:00PM', "%I:%M%p").time()
    timeMOTS = datetime.datetime.strptime('2:00AM', "%I:%M%p").time()
    timeMOTE= datetime.datetime.strptime('3:00AM', "%I:%M%p").time()

    #inits
    screen_name = ""
    retweetTags = []
    favoriteTags = []
    followTags = []
    logFile = ""

    def __init__(self, ckey, csec, akey, asec, fb_url):
        self.fb_url = fb_url

        auth = tweepy.OAuthHandler(ckey, csec)
        auth.set_access_token(akey, asec)
        self.auth = auth
        self.api = tweepy.API(auth)
        self.myListener = StdOutListener()
        self.stream = Stream(auth, self.myListener)

    def addFollower(self, tag, minRetweetCount=5, minFavCount = 10):
        rtnBool = True
        try:
            retweetDB = "tweets.json"
            favDB = "favTweets.json"
            check = False
            c = tweepy.Cursor(self.api.search, q=tag).items(500)
            for tweet in c:
                if (tweet.retweet_count > minRetweetCount) and (tweet.favorite_count > minFavCount):
                    if not tweet.user.following:
                        tweet.user.follow()
                        # file-append
                        f = open(self.logFile,'a')
                        f.write('\n' + 'Followed the user: @' + tweet.user.screen_name)
                        f.close()
                        check = True
                        #Also favorite it half the time
                        if (random.random() >= .5) and (self.checkTweetNotInDB(tweet, favDB)):
                            tweet.favorite()
                            db_tweet = {"id": tweet.id}
                            requests.post(self.fb_url + favDB, json.dumps(db_tweet))
                            # file-append
                            f = open(self.logFile,'a')
                            f.write('\n' + 'Favorited Tweet Id: ' + str(tweet.id))
                            f.close()
                        #Also retweet it occaisionally
#                        if (random.random() >= .8) and (self.checkTweetNotInDB(tweet, retweetDB)):
#                            self.api.retweet(tweet.id)
#                            db_tweet = {"id": tweet.id}
#                            requests.post(self.fb_url + retweetDB, json.dumps(db_tweet))
#                            # file-append
#                            f = open(self.logFile,'a')
#                            f.write('\n' + 'Retweeted Tweet Id: ' + str(tweet.id))
#                            f.close()
                        break
                else:
                    continue

            if check == False:
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Failed to Follow Anyone for Tag: " + tag)
                f.close()
                rtnBool = False

            # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            rtnBool = False
        return rtnBool

    def postRetweet(self, tag, minRetweetCount=20):
        rtnBool = True
        try:
            retweetDB = "tweets.json"
            favDB = "favTweets.json"

            c = tweepy.Cursor(self.api.search, q=tag).items(100)
            for tweet in c:
                if tweet.retweet_count > minRetweetCount:
                    if self.checkTweetNotInDB(tweet, retweetDB):
                        self.api.retweet(tweet.id)
                        db_tweet = {"id": tweet.id}
                        requests.post(self.fb_url + retweetDB, json.dumps(db_tweet))
                        # file-append
                        f = open(self.logFile,'a')
                        f.write('\n' + 'Retweeted Tweet Id: ' + str(tweet.id))
                        f.close()
                        #Also favorite it half the time
                        if (random.random() >= .5) and (self.checkTweetNotInDB(tweet, favDB)):
                            tweet.favorite()
                            db_tweet = {"id": tweet.id}
                            requests.post(self.fb_url + favDB, json.dumps(db_tweet))
                            # file-append
                            f = open(self.logFile,'a')
                            f.write('\n' + 'Favorited Tweet Id: ' + str(tweet.id))
                            f.close()
                        #Also follow sometimes
                        if (random.random() <= .2) and (not tweet.user.following):
                            tweet.user.follow()
                            # file-append
                            f = open(self.logFile,'a')
                            f.write('\n' + 'Followed the user: @' + tweet.user.screen_name)
                            f.close()
                        break
        # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            rtnBool = False
        return rtnBool

    def addFavorite(self, tag, minFavoriteCount=20):
        rtnBool = True
        try:
            retweetDB = "tweets.json"
            favDB = "favTweets.json"
            check = False
            c = tweepy.Cursor(self.api.search, q=tag).items(500)
            for tweet in c:
                if tweet.favorite_count > minFavoriteCount:
                    if self.checkTweetNotInDB(tweet, favDB):
                        tweet.favorite()
                        db_tweet = {"id": tweet.id}
                        requests.post(self.fb_url + favDB, json.dumps(db_tweet))
                        # file-append
                        f = open(self.logFile,'a')
                        f.write('\n' + 'Favorited Tweet Id: ' + str(tweet.id))
                        f.close()
                        check = True
                        #Also retweet it occaisionally
#                        if (random.random() >= .75) and (self.checkTweetNotInDB(tweet, retweetDB)):
#                            self.api.retweet(tweet.id)
#                            db_tweet = {"id": tweet.id}
#                            requests.post(self.fb_url + retweetDB, json.dumps(db_tweet))
#                            # file-append
#                            f = open(self.logFile,'a')
#                            f.write('\n' + 'Retweeted Tweet Id: ' + str(tweet.id))
#                            f.close()
                        #Also follow sometimes
                        if (random.random() <= .25) and (not tweet.user.following):
                            tweet.user.follow()
                            # file-append
                            f = open(self.logFile,'a')
                            f.write('\n' + 'Followed the user: @' + tweet.user.screen_name)
                            f.close()
                        break
                else:
                    continue

            if check == False:
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Failed to Favorite Anything for Tag: " + tag)
                f.close()
                rtnBool = False

        # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            rtnBool = False
        return rtnBool

    def followFollowers(self):
        try:
            for user in self.api.followers():
                if not user.following:
                    user.follow()
                    # file-append
                    f = open(self.logFile,'a')
                    f.write('\n' + 'Followed the user: @' + user.screen_name)
                    f.close()
        # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            pass

    def updateRetweetDatabase(self):
        try:
            retweetDB = "tweets.json"
            tweets = self.api.user_timeline(screen_name = self.screen_name, count = 100, include_rts = True)
            for tweet in tweets:
                if tweet._json["retweeted"]:
                    if self.checkTweetNotInDB(tweet, retweetDB):
                        db_tweet = {"id": tweet.id}
                        requests.post(self.fb_url + retweetDB, json.dumps(db_tweet))
                # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            pass

    def updateFavoriteDatabase(self):
        try:
            favDB = "favTweets.json"
            tweets = tweepy.Cursor(self.api.favorites,id=self.screen_name).items(100)
            for tweet in tweets:
                if self.checkTweetNotInDB(tweet, favDB):
                    db_tweet = {"id": tweet.id}
                    requests.post(self.fb_url + favDB, json.dumps(db_tweet))
                # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            pass

    def checkTweetNotInDB(self, tweet, dataBase):
        rtnBool = True
        try:
            r = requests.get(self.fb_url + dataBase)
            r = r.json()
            for i in r:
                if tweet.id == r[i]["id"]:
                    rtnBool = False
                    break
       # Exceptions
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + str(e))
            f.close()
            pass
        return rtnBool

    @staticmethod
    def isNowInTimePeriod(startTime, endTime, nowTime):
        rtnBool = False
        if startTime < endTime:
            rtnBool = nowTime >= startTime and nowTime <= endTime
        else: #Over midnight
            rtnBool = nowTime >= startTime or nowTime <= endTime
        return rtnBool

    @staticmethod
    def sleepyBaby(self):
        time1 = random.randint(1, 4)
        if time1 == 1:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Sleeping for 8.5min...")
            f.close()
            sleep(2100/4) #Tweet every 8.5 minutes
        elif time1 == 2:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Sleeping for 16min...")
            f.close()
            sleep(3900/4) #Tweet every 16 minutes
        elif time1 == 3:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Sleeping for 12.5min...")
            f.close()
            sleep(2760/4) #Tweet every 12.5 minutes
        else:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Sleeping for 6min...")
            f.close()
            sleep(1410/4) #Tweet every 6 minutes

    @abstractmethod
    def getStatus(self):
        """"Return a string to update as the status"""
        pass

    def postStatus(self, status):
        rtnBool = True
        if status and not status is None:
            try:
                self.api.update_status(status)
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + 'Created a Status: ' + status)
                f.close()
            # Additions below
            except KeyboardInterrupt:
                sys.exit("KeyboardInterrupt")
            except Exception as e:
                print(e)
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + str(e))
                f.close()
        else:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Failed to create a status this time")
            f.close()
            rtnBool = False
        return rtnBool

    def doAction(self):
        # file-append
        f = open(self.logFile,'a')
        f.write('\n' + "Trying to do an Action...")
        f.close()
        #Update probabilities here
        potentialActions = ["follow", "favorite", "favorite", "status", "status", "status", "status", "status", "status", "nothing"]
        action = random.choice(potentialActions)
        statBool = True
        #For Central from UTC time zone in pythonAnywhere
        timeNow = (datetime.datetime.now() - datetime.timedelta(hours=6)).time()
        if self.isNowInTimePeriod(self.timeStart, self.timeEnd, timeNow):
            if action == "retweet":
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Chose Retweet")
                f.close()
                statBool = self.postRetweet(random.choice(self.retweetTags))
            elif action == "status":
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Chose Status")
                f.close()
                statBool = self.postStatus(self.getStatus())
            elif action == "favorite":
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Chose Favorite")
                f.close()
                rInt = random.randint(1, 5)
                for x in range(0, rInt):
                    statBool = self.addFavorite(random.choice(self.favoriteTags))
                    if (statBool == False) and (x > 0):
                        statBool = True
                        break
                    if statBool == False:
                        break
            elif action == "follow":
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Chose Follow")
                f.close()
                rInt = random.randint(1, 3)
                for x in range(0, rInt):
                    statBool = self.addFollower(random.choice(self.followTags))
                    if (statBool == False) and (x > 0):
                        statBool = True
                        break
                    if statBool == False:
                        break
            else:
                # file-append
                f = open(self.logFile,'a')
                f.write('\n' + "Chose to do Nothing this time... *shrug*")
                f.close()
                statBool = True
                pass
        else:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Outside time to do any actions... " + str(timeNow))
            f.close()

        #Check for manual retweets and favorites not logged in db
        #Also follow any new followers
        if self.isNowInTimePeriod(self.timeMOTS, self.timeMOTE, timeNow):
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Middle of the night... " + str(timeNow))
            f.write('\n' + "Updating Databases")
            self.updateRetweetDatabase()
            self.updateFavoriteDatabase()
            f.write('\n' + "Following Followers")
            f.close()
            self.followFollowers()

        if statBool:
            self.sleepyBaby(self)
        else:
            # file-append
            f = open(self.logFile,'a')
            f.write('\n' + "Failed to complete an action. Trying again in 2.5min")
            f.close()
            sleep(250)