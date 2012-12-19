#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
#from scipy import *
import scipy
import random
import fnmatch

sys.path.append('../utility/')
from boundingBox import *
from loadFile import *
from common import *

def getAllTweet(tweet, all_tweets):
    id = tweet['id'];
    all_tweets[id] = {};
    all_tweets[id]['time'] = tweet['time'];
    all_tweets[id]['geo'] = tweet['geo'];
    all_tweets[id]['url'] = tweet['url'];

def replyCollect(tweet, all_tweets, tweet_time, tweet_dis, replied_tweets, begin_time, geo_center):
    time = tweet['time']
    date_time = tweetTimeToDatetime(time);
    #every half hour
    unit = date_time - begin_time;
    day_time = unit.days * 24 * 60;
    time_index = int(unit.seconds / 60 + day_time);
    if time_index < 0:
        return;

    if time_index not in tweet_time.keys():
        tweet_time[time_index] = {};
        tweet_time[time_index]['replying_count'] = 0;
        tweet_time[time_index]['tweet_count'] = 0
    tweet_time[time_index]['tweet_count'] += 1;

    geo = tweet['geo']; 
    radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
    radiu = radiu**0.5*100
    dis_index = int(radiu);
    if dis_index > 1000:
        return;

    if dis_index not in tweet_dis.keys():
        tweet_dis[dis_index] = {};
        tweet_dis[dis_index]['replying_count'] = 0;
        tweet_dis[dis_index]['tweet_count'] = 0
    tweet_dis[dis_index]['tweet_count'] += 1;

    replyid = tweet['reply_to'] 
    if replyid != None and replyid != []:
        tweet_time[time_index]['replying_count'] += 1;
        tweet_dis[dis_index]['replying_count'] += 1;
        if replyid in all_tweets.keys():
            replied_info = all_tweets[replyid];
            if replyid not in replied_tweets:
                replied_tweets[replyid] = replied_info;
                replied_tweets[replyid]['count'] = 0;
            
            replied_tweets[replyid]['count'] += 1;

def replyTimeDis(replied_tweets, begin_time, geo_center):
    reply_time = {};
    reply_dis = {};
    for id, tweet in replied_tweets.iteritems():
        time = tweet['time']
        date_time = tweetTimeToDatetime(time);
        #every half hour
        unit = date_time - begin_time;
        day_time = unit.days * 24 * 60;
        time_index = int(unit.seconds / 60 + day_time);
        if time_index < 0:
            return;

        if time_index not in reply_time.keys():
            reply_time[time_index] = {};
            reply_time[time_index]['replied_count'] = 0
        reply_time[time_index]['replied_count'] += tweet['count'];

        geo = tweet['geo']; 
        radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
        radiu = radiu**0.5*100
        dis_index = int(radiu);
        if dis_index > 1000:
            return;

        if dis_index not in reply_dis.keys():
            reply_dis[dis_index] = {};
            reply_dis[dis_index]['replied_count'] = 0
        reply_dis[dis_index]['replied_count'] += tweet['count'];

    return reply_time, reply_dis;

def replyStat(tweet_fold, begin_time, geo_center): 
    files = os.listdir(tweet_fold);
    tweet_time = {};
    tweet_dis = {};
    all_tweets = {};
    replied_tweets = {};

    for afile in files:
        if not fnmatch.fnmatch(afile, '*_1?.txt'):
            continue
        path = tweet_fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);   
        for tweet in tweets:
            getAllTweet(tweet, all_tweets)

    for afile in files:
        if not fnmatch.fnmatch(afile, '*_1?.txt'):
            continue
        path = tweet_fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);   
        for tweet in tweets:
            replyCollect(tweet, all_tweets, tweet_time, tweet_dis, replied_tweets, begin_time, geo_center);
    
    reply_time, reply_dis =  replyTimeDis(replied_tweets, begin_time, geo_center);
    
    return tweet_time, tweet_dis, reply_time, reply_dis

def replyMain():
    begin_time = datetime.datetime(2011, 3, 11, 5, 46, 24);
    geo_center = [38.297, 142.372]
    
    spread_list = {};
    spread_dis_list = {};

    fold = '../duration/data/jpeq_jp/tweet2/';
    tweet_time, tweet_dis, reply_time, reply_dis = replyStat(fold, begin_time, geo_center);

    outfilename = 'data/event/jpeq_world/reply_stat.txt';
    outfile = file(outfilename, 'w');
    json.dump(tweet_time, outfile);
    outfile.write('\n');
    json.dump(tweet_dis, outfile);
    outfile.write('\n');
    json.dump(reply_time, outfile);
    outfile.write('\n');
    json.dump(reply_dis, outfile);
    outfile.write('\n');
    outfile.close();

replyMain();
