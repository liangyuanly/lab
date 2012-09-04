#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
simplejson = json
import ast
import random
import sys
sys.path.append('../utility/')
from tokenExtract import *
from boundingBox import *

#according to one hour
def getIndexForBinHour(begin, end, time):
    index = -1;
    if time >= begin and time <= end:
        values = time - begin;
        values = values.days*3600*24 + values.seconds;
        index = math.floor(values/3600); 
    else:
        print time;

    return index;

#stat the user's frequency
def userFrequencyBins(g_userlist):
    bins = {};
    for user, count in g_userlist.iteritems():
        if count in bins.keys():
            bins[count] = bins[count] + 1;
        else:
            bins[count] = 1;
    return bins;

#put the new added user into bins
def putNewUserInBins(g_userlist, tweets, user_bins, periods, isFilter=0):
    #get the begin and end time
    period = periods[0];
    year = period[0];
    month = period[1];
    day = period[2];
    begin_time = datetime.datetime(year, month, day, 0, 0, 0);
    period = periods[len(periods)-1];
    year = period[0];
    month = period[1];
    day = period[3];
    end_time = datetime.datetime(year, month, day-1, 23, 59, 0);
    
    for tweet in tweets:
        user = tweet['user'];
        
        if isFilter > 0:
            #chosse 20% users as the test data, !=0 means choosing the test data, == 0 means choose the trainig data
            if user % 5 != 0:
                continue;

        #existing users
        if user in g_userlist.keys():
            g_userlist[user] = g_userlist[user] + 1;
            continue;
        g_userlist[user] = 1;

        time = tweet['time'];
        time = tweetTimeToDatetime(time);
        index = getIndexForBinHour(begin_time, end_time, time);

        user_list = user_bins.get(index);
        if user_list == None:
            user_list = {};
            user_bins[index] = user_list;

        count = user_list.get(user);
        if count == None:
            user_list[user] = 1;
        else:
            user_list[user] = user_list[user] + 1;        

#calculate the unique user numbers per hour
def putUserInBins(tweets, user_bins, periods, isFilter=0):
    #get the begin and end time
    period = periods[0];
    year = period[0];
    month = period[1];
    day = period[2];
    begin_time = datetime.datetime(year, month, day, 0, 0, 0);
    period = periods[len(periods)-1];
    year = period[0];
    month = period[1];
    day = period[3];
    end_time = datetime.datetime(year, month, day-1, 23, 59, 59);
    
    for tweet in tweets:
        time = tweet['time'];
        time = tweetTimeToDatetime(time);
        index = getIndexForBinHour(begin_time, end_time, time);

        user = tweet['user'];

        if isFilter == 1:
            #choose 20% users as the test users
            if user % 5 != 0:
                continue;

        user_list = user_bins.get(index);
        if user_list == None:
            user_list = {};
            user_bins[index] = user_list;

        count = user_list.get(user);
        if count == None:
            user_list[user] = 1;
        else:
            user_list[user] = user_list[user] + 1;        

#filter the user who appears later
#then remaining users are checkouts
def filterUsers(user_bins):
    for hour1, user_list1 in user_bins.items():
        for hour2, user_list2 in user_bins.items():
            if hour2 <= hour1:
                continue;
            for user in user_list1.keys():
                if user in user_list2.keys():
                    del user_list1[user];


def statUserCount(user_bins):
    time_usercount = {};
    time_tweetcount = {};
    for hour, user_list in user_bins.iteritems():
        time_usercount[hour] = len(user_list);
        tweetscount = 0;
        for user, count in user_list.iteritems():
            tweetscount = tweetscount + count;
        time_tweetcount[hour] = tweetscount;

    return [time_usercount, time_tweetcount];

#choose 1/10 as the test data
#choose 9/10 as the trainig data
def chooseTweets(tweets):
    count = 0;
    sel_tweets = [];
    for tweet in tweets:
        if count % 10 != 0: #!= as the training data, == as the test data
            sel_tweets.append(tweet);
        
        count = count + 1;
    return sel_tweets;

def getEventUserBins(event, periods):
    #load the words for an event
    #term_file = './data/japan_earthquake_words.txt';
    #load the tweets
    user_bins = {};
    new_user_bins = {};
    g_userlist = {};
    for i in range(0, len(periods)):
        period = periods[i];
        year = period[0];
        month = period[1];
        day_from = period[2];
        day_to = period[3];
        user_timelist = {};
        for day in range(day_from, day_to):
            tweet_file = './data/' + event + '/weiTTL/' + str(year) + '_' + str(month) + '_' + str(day) + '.txt';
            tweets = loadSimpleTweetsFromFile(tweet_file);
            print tweet_file, len(tweets);
            
            #sel_tweets = chooseTweets(tweets);
            putUserInBins(tweets, user_bins, periods, 1);
            putNewUserInBins(g_userlist, tweets, new_user_bins, periods, 1);
    
   
    count_bins = userFrequencyBins(g_userlist); 
    #record the user's frequency
    outfile = file('./data/' + event + '/user_freq_8outof10.txt', 'w');
    json.dump(count_bins, outfile);
    outfile.close();

    [time_newuser_count, time_newtweets_count] = statUserCount(new_user_bins); 
    #record the new user and the tweets of new users
    outfile = file('./data/' + event + '/new_user_count_2outof10.txt', 'w');
    json.dump(time_newtweets_count, outfile);
    outfile.write('\n');
    json.dump(time_newuser_count, outfile);
    outfile.close();

 
    [time_usercount, time_tweetscount] = statUserCount(user_bins);
    
    outfile = file('./data/' + event + '/user_count_2outof10.txt', 'w');
    json.dump(time_tweetscount, outfile);
    outfile.write('\n');
    
    #filter users, get the real checkouts
    filterUsers(user_bins);
    [time_usercount, time_tweetscount] = statUserCount(user_bins);
    json.dump(time_usercount, outfile);
    outfile.close();
    
def getEventUserStatMain():
    event = 'NBA';
    periods = getNBAPeriod();
    getEventUserBins(event, periods);
    
    event = 'election';
    periods = getElectionPeriod();
    getEventUserBins(event, periods);
    
    event = 'royal';
    periods = getRoyalPeriod();
    getEventUserBins(event, periods);

    event = 'jobs';
    periods = getJobsPeriod();
    getEventUserBins(event, periods);

    event = 'irene';
    periods = getIrenePeriod();
    getEventUserBins(event, periods);

    event = 'jpeq_us';
    periods = getJPEQPeriod();
    getEventUserBins(event, periods);

getEventUserStatMain();
