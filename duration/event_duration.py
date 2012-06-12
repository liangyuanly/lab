#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
#from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
#from getTweets import GetTweets;
simplejson = json
#from parser import HTMLParsers
#from parser import Utilities
import ast
#import nltk
#from nltk.tokenize import RegexpTokenizer
#from nltk.tokenize.api import *
#from tinysegmenter import *
#from operator import itemgetter
import random
#from Utility import * 
import sys
#sys.path.append('../media/earthquake/')
sys.path.append('../utility/')
#from Utility import *
from tokenExtract import *
from boundingBox import *

g_tweets = {};

#the begin and end time the users are involved in an event
def getUserTweetsTime2(tweets, user_timelist):
    count = 0;
    for tweet in tweets:
        #id = tweet['id'];
        #if id in g_tweets.keys():
        #    continue;
        #g_tweets[id] = 0;

        time = tweet['time'];
        time = tweetTimeToDatetime(time);

        user = tweet['user'];
        timelist = user_timelist.get(user);

        count = count + 1;
        print user, len(user_timelist), count;

        if timelist == None:
            timelist = [];
            user_timelist[user] = timelist;
        
        if len(timelist) == 0:
            timelist.append(time);
        else:
            if len(timelist) == 1:
                #repeative tweets
                if time == timelist[0]:
                    continue;

                if time < timelist[0]:
                    stop_time = timelist[0];
                    timelist.append(stop_time);
                    timelist[0] = time;
                else:
                    timelist.append(time);
            else:
                if len(timelist) == 2:
                    if time < timelist[0]:
                        timelist[0] = time;
                    if time > timelist[1]:
                        timelist[1] = time;
                
#the begin and end time the users are involved in an event
def getUserTweetsTime(words, tweets, user_timelist):
    #count = 0;
    for tweet in tweets:
        id = tweet['id'];
        if id in g_tweets.keys():
            continue;
        g_tweets[id] = 0;

        #count = count + 1;
        #if count > 10000:
        #    break;

        for word in words:
            sim = similarity4(word, tweet['text']);
            if sim  > 0:
                time = tweet['time'];
                time = tweetTimeToDatetime(time);

                user = tweet['user'];
                timelist = user_timelist.get(user);
                
                if timelist == None:
                    timelist = [];
                    user_timelist[user] = timelist;
                
                if len(timelist) == 0:
                    timelist.append(time);
                else:
                    if len(timelist) == 1:
                        #repeative tweets
                        if time == timelist[0]:
                            break;

                        if time < timelist[0]:
                            stop_time = timelist[0];
                            timelist.append(stop_time);
                            timelist[0] = time;
                        else:
                            timelist.append(time);
                    else:
                        if len(timelist) == 2:
                            if time < timelist[0]:
                                timelist[0] = time;
                            if time > timelist[1]:
                                timelist[1] = time;
                
                break;

#get the user's first time which is not evovled in an event
def getUserNextTime(user_duraTimelist, tweets, user_nextTime, user_freq):
    for tweet in tweets:
        user = tweet['user'];

        timelist = user_timelist[user];
        if timelist != None:
            time = tweetTimeToDatetime(tweet['time']);
            if len(timelist) == 0:
                continue;
            if len(timelist) == 1:
                if time <= timelist[0]:
                    continue;
            if len(timelist) == 2:
                if time <= timelist[1]:
                    continue;

            next_time = user_nextTime[user];
            if next_time == None:
                user_nextTime[user] = time;

            freq = user_freq.get(user);
            if freq == None:
                user_freq[user] = 0;

            user_freq[user] = user_freq[user] + 1;

#cal the duration users stay in an event
def getUserDura(user_duraTimelist, isFilter=0):
    user_dura = {};
    for user, timelist in user_duraTimelist.iteritems():
        #if len(timelist) == 1:
            #print 'only one checkin';
        
        #choose the 80% data as the training data
        if isFilter > 0:
            if user % 5 == 0:
                continue;

        if len(timelist) == 2:
            interval = timelist[1] - timelist[0];
            user_dura[user] = interval.days*24*3600 + interval.seconds;

    return user_dura;

def getEventDuraMain():
    #load the words for an event
    term_file = './data/japan_earthquake_words.txt';
    words = loadTerms(term_file);

    #load the tweets
    year = 2011;
    month = 3;
    day_from = 11;
    day_to = 26;
    user_timelist = {};
    for day in range(day_from, day_to):
        tweet_file = '/mnt/chevron/yuan/tweet/' + str(year) + '_' + str(month) + '_' + str(day) + '.txt';
        tweets = loadSimpleTweetsFromFile(tweet_file);
        getUserTweetsTime(words, tweets, user_timelist);
        #break;

    user_dura = getUserDura(user_timelist, 1);

    outfile = file('./output/user_dura.txt', 'w');
    json.dump(user_dura, outfile);
    outfile.close();

#choose 9/10 as the training data
def chooseTweets(tweets):
    count = 0;
    sel_tweets = [];
    for tweet in tweets:
        if count % 10 != 0:
            sel_tweets.append(tweet);
        
        count = count + 1;
    return sel_tweets;

def getEventDuraFunc(event, periods):
    #load the tweets
    period = periods[0];
    year = period[0];
    month = period[1];
    day_from = period[2];
    day_to = period[3];
    user_timelist = {};
    number = 0;
    for day in range(day_from, day_to):
        tweet_file = './data/' + event + '/weiTTL/' + str(year) + '_' + str(month) + '_' + str(day) + '.txt';
        tweets = loadSimpleTweetsFromFile(tweet_file);
        number = number + len(tweets);
        print tweet_file, len(tweets), number;

        getUserTweetsTime2(tweets, user_timelist);

    user_dura = getUserDura(user_timelist, 1);

    outfile = file('./data/' + event + '/user_dura_TTL_8outof10.txt', 'w');
    json.dump(user_dura, outfile);
    outfile.close();

def getEventDuraMain2():
    event = 'NBA';
    period = getNBAPeriod();
    getEventDuraFunc(event, period);
    
    event = 'election';
    period = getElectionPeriod();
    getEventDuraFunc(event, period);
    
    event = 'royal';
    period = getRoyalPeriod();
    getEventDuraFunc(event, period);
    
    event = 'jobs';
    period = getJobsPeriod();
    getEventDuraFunc(event, period);
    
    event = 'irene';
    period = getIrenePeriod();
    getEventDuraFunc(event, period);
    
    event = 'jpeq_us';
    period = getJPEQPeriod();
    getEventDuraFunc(event, period);

#getEventDuraMain2();
