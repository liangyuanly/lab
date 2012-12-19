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
from bin import *
from tokenization import similarityCal

def DicDivide(loc_bin, user_bin):
    new_bin = {};
    for key, value in loc_bin.iteritems():
        if key in user_bin:
            new_bin[key] = value / float(user_bin[key]);
            print value, user_bin[key], new_bin[key];
        else:
            print value, 0
            new_bin[key] = value;
         
    return new_bin;

def normalizeArray(dic):
    sum = 0.0;
    for ele in dic:
        sum = sum + ele;
    
    if sum > 0:
        for i in range(0, len(dic)):
            dic[i] /= sum;

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

    if time_index not in tweet_time:
        tweet_time[time_index] = {};
        tweet_time[time_index]['tweet_count'] = 0
    tweet_time[time_index]['tweet_count'] += 1;

    geo = tweet['geo']; 
    radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
    radiu = radiu**0.5
    dis_index = int(radiu);
    if dis_index not in tweet_dis:
        tweet_dis[dis_index] = {};
        tweet_dis[dis_index]['tweet_count'] = 0
    tweet_dis[dis_index]['tweet_count'] += 1;

    replyid = tweet['in_reply_to_status_id'] 
    if replyid != None and replyid != []:
        if replyid in all_tweets:
            replied_info = all_tweets[replyid];
            if replyid not in replied_tweets:
                replied_tweets[replyid] = replied_info;
                replied_tweets[replyid]['count'] = 0;
            else:
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

        if time_index not in reply_time:
            reply_time[time_index] = {};
            reply_time[time_index]['replied_count'] = 0
        reply_time[time_index]['replied_count'] += tweet['count'];

        geo = tweet['geo']; 
        radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
        radiu = radiu**0.5
        dis_index = int(radiu);
        if dis_index not in reply_dis:
            reply_dis[dis_index] = {};
            reply_dis[dis_index]['replied_count'] = 0
        reply_dis[dis_index]['replied_count'] += tweet['count'];

    return reply_time, reply_dis;

#only count the current retweet
def retweetTime(tweet, tweet_time, begin_time):
    text = tweet['text'];
    time = tweet['time']

    date_time = tweetTimeToDatetime(time);
    #every half hour
    unit = date_time - begin_time;
    day_time = unit.days * 24 * 60;
    time_index = int(unit.seconds / 60 + day_time);
    if time_index < 0:
        return;

    #test, only count the earthquake
    #if similarityCal('earthquake', text) <= 0:
    #    return;

    if time_index not in tweet_time:
        tweet_time[time_index] = {};
        tweet_time[time_index]['retweet_count'] = 0
        tweet_time[time_index]['tweet_count'] = 0
        tweet_time[time_index]['image_tweet_count'] = 0;

    tweet_time[time_index]['tweet_count'] += 1
    
    url = tweet['url'];
    if len(url) > 0:
        tweet_time[time_index]['image_tweet_count'] += 1;

    if text.find('RT @') >= 0:
        tweet_time[time_index]['retweet_count'] += 1    

def retweetDis(tweet, tweet_dis, geo_center, radiu_step):
    text = tweet['text'];
    geo = tweet['geo'];
    url = tweet['url'];
    user = tweet['user'];

    radiu = (geo[0] - geo_center[0][0])**2 + (geo[1] - geo_center[1][0])**2;
    radiu = radiu**0.5;
    radiu = int(radiu/float(radiu_step))
    dis_index = int(radiu);
    if dis_index > 100:
        return;

    if dis_index not in tweet_dis:
        tweet_dis[dis_index] = {};
        tweet_dis[dis_index]['tweet_count'] = 0
        tweet_dis[dis_index]['retweet_count'] = 0
        tweet_dis[dis_index]['image_retweet_count'] = 0;
        tweet_dis[dis_index]['image_tweet_count'] = 0;
        tweet_dis[dis_index]['user_count'] = 0;
        tweet_dis[dis_index]['image_user_count'] = 0;
        tweet_dis[dis_index]['user'] = {};
        tweet_dis[dis_index]['image_user'] = {};

    if len(url) != 0:
        tweet_dis[dis_index]['image_tweet_count'] += 1;
        if user not in tweet_dis[dis_index]['image_user']:
            tweet_dis[dis_index]['image_user'][user] = 0;
            tweet_dis[dis_index]['image_user_count'] += 1;
    else:
        tweet_dis[dis_index]['tweet_count'] += 1
        if user not in tweet_dis[dis_index]['user']:
            tweet_dis[dis_index]['user'][user] = 0;
            tweet_dis[dis_index]['user_count'] += 1;
 
    if text.find('RT @') >= 0:
        if len(url) != 0:
            tweet_dis[dis_index]['image_retweet_count'] += 1;
        else:
            tweet_dis[dis_index]['retweet_count'] += 1

def retweetFreq(tweet, retweet_list):
    text = tweet['text'];
    if text.find('RT @') < 0:
        return

    retweet_count = tweet['count'];
    time = tweet['time'];
    geo = tweet['geo'];
    url = tweet['url']
    
    if id in retweet_list:
        if retweet_count > retweet_list[id]['count']:
            retweet_list[id]['count'] = retweet_count;
    else:
        retweet_list[id] = {}
        retweet_list[id]['count'] = retweet_count;
        retweet_list[id]['time'] = time;
        retweet_list[id]['geo'] = geo;
        retweet_list[id]['url'] = url;


#    if 'retweeted_status' in tweet.keys():
#        retweet = tweet['retweeted_status'];
#        id = retweet['id'];
#        retweet_count = tweet['count'];
#        time = tweet['time'];
#        geo = tweet['geo'];
#        url = tweet['url']
#
#        if id in retweet_list.keys():
#            if retweet_count > retweet_list[id]['count']:
#                retweet_list[id]['count'] = retweet_count;
#        else:
#            retweet_list[id] = {}
#            retweet_list[id]['count'] = retweet_count;
#            retweet_list[id]['time'] = time;
#            retweet_list[id]['geo'] = geo;
#            retweet_list[id]['url'] = url;

def retweetTimeDis(retweet_list, begin_time, geo_center):
    retweet_time = {};
    retweet_dis = {};
    for id, tweet in retweet_list.iteritems():
        time = tweet['time'];
        geo = tweet['geo'];
        count = tweet['count'];

        date_time = tweetTimeToDatetime(time);
        #every half hour
        unit = date_time - begin_time;
        day_time = unit.days * 24 * 60;
        time_index = int(unit.seconds / 60 + day_time);
        if time_index < 0 or time_index > 96*60:
            continue;

        if time_index not in retweet_time:
            retweet_time[time_index] = {};
            retweet_time[time_index]['sum_freq'] = 0
            retweet_time[time_index]['tweet_count'] = 0
        
        retweet_time[time_index]['sum_freq'] += count 
        retweet_time[time_index]['tweet_count'] += 1
        
        radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
        radiu = radiu**0.5
        dis_index = int(radiu);
        
        if dis_index not in retweet_dis:
            retweet_dis[dis_index] = {};
            retweet_dis[dis_index]['sum_freq'] = 0
            retweet_dis[dis_index]['tweet_count'] = 0

        retweet_dis[dis_index]['sum_freq'] += count 
        retweet_dis[dis_index]['tweet_count'] += 1
    
    return retweet_time, retweet_dis;

def getGeoCenter(tweet_fold, bb, x_step, y_step):
    loc_bin = {};
    image_loc_bin = {};
    retweet_loc_bin = {};
    image_retweet_loc_bin = {};
    files = os.listdir(tweet_fold);
    tweet_time = {};
    tweet_dis = {};
    user_list = {};
    image_user_list = {};
    user_bin = {};
    image_user_bin = {};

    for afile in files:
        #if not fnmatch.fnmatch(afile, '*_1?.txt'):
        #    continue
        path = tweet_fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);   
        for tweet in tweets:
            if not isTweetInbb(bb, tweet):
                continue;
            text = tweet['text'];
            url = tweet['url'];
            user = tweet['user'];

            if len(url) > 0:
                key = getLocBin([tweet['geo']], bb, x_step, y_step, image_loc_bin);
                if key not in image_user_list:  #calculate the users' distribution
                    image_user_list[key] = {};
                    image_user_list[key][user] = 0;
                    getLocBin([tweet['geo']], bb, x_step, y_step, image_user_bin);
                else:
                    if user not in image_user_list[key]:
                        image_user_list[key][user] = 0;
                        getLocBin([tweet['geo']], bb, x_step, y_step, image_user_bin);
            else:
                key = getLocBin([tweet['geo']], bb, x_step, y_step, loc_bin);
                if key not in user_list:  #calculate the users' distribution
                    user_list[key] = {};
                    user_list[key][user] = 0;
                    getLocBin([tweet['geo']], bb, x_step, y_step, user_bin);
                else:
                    if user not in user_list[key]:
                        user_list[key][user] = 0;
                        getLocBin([tweet['geo']], bb, x_step, y_step, user_bin);

            if text.find('RT @') >= 0:
                if len(url) > 0:
                    getLocBin([tweet['geo']], bb, x_step, y_step, image_retweet_loc_bin);
                else:
                    getLocBin([tweet['geo']], bb, x_step, y_step, retweet_loc_bin);
    
    center_x = {};
    center_y = {};
    user_fre = DicDivide(loc_bin, user_bin);
    image_user_fre = DicDivide(image_loc_bin, image_user_bin);
    center_x[4], center_y[4] = getPeakLoc(user_fre, bb, x_step, y_step);
    center_x[5], center_y[5] = getPeakLoc(image_user_fre, bb, x_step, y_step);
    
    center_x[0], center_y[0] = getPeakLoc(loc_bin, bb, x_step, y_step);
    center_x[1], center_y[1] = getPeakLoc(image_loc_bin, bb, x_step, y_step);
    
    center_x[2], center_y[2] = getPeakLoc(retweet_loc_bin, bb, x_step, y_step);
    center_x[3], center_y[3] = getPeakLoc(image_retweet_loc_bin, bb, x_step, y_step);

    return center_x, center_y;

def retweetStat(tweet_fold, begin_time, geo_center, bb, radiu_step): 
    files = os.listdir(tweet_fold);
    tweet_time = {};
    tweet_dis = {};

    for afile in files:
        #if not fnmatch.fnmatch(afile, '*_1?.txt'):
        #    continue
        path = tweet_fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);   
        for tweet in tweets:
            #retweetFreq2(tweet, retweet_list);
            if not isTweetInbb(bb, tweet):
                continue;
     
            retweetTime(tweet, tweet_time, begin_time)
            #retweetDis(tweet, tweet_dis, geo_center, radiu_step)
    
    return tweet_time, tweet_dis
    #return retweetTime(retweet_list, begin_time, geo_center);

def retweetMain():
    begin_time = datetime.datetime(2011, 2, 21, 23, 0, 0)
    #begin_time = datetime.datetime(2011, 3, 11, 5, 0, 0);
    center_x, center_y = [38.297, 142.372]
    #center_x = [center_x];
    #center_y = [center_y];
    #bb = getWorldbb();
    bb = getNZbb();

    #this one contain all the earthquake from the world
    #fold = '../duration/data/jpeq_jp/tweet2/';
    fold = '../duration/data/earthquake_NZ/weiTTL/'
    
    #center_x, center_y = getGeoCenter(fold, bb, 0.01, 0.01);
    print 'geo_center =', center_x, center_y;
    radiu_step = 0.1;
    retweet_time, retweet_dis = retweetStat(fold, begin_time, [center_x, center_y], bb, radiu_step);

    outfilename = 'data/event/nzeq/retweet_stat.txt';
    outfile = file(outfilename, 'w');
    json.dump(retweet_time, outfile);
    outfile.write('\n');
    for index in retweet_dis:
        del retweet_dis[index]['user'];
        del retweet_dis[index]['image_user'];

    json.dump(retweet_dis, outfile);
    outfile.write('\n');
    json.dump(radiu_step, outfile);
    outfile.write('\n');
    outfile.close();

retweetMain()
