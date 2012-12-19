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

def spreadByDis(tweet, spread_list, geo_center):
    user = tweet['user'];
    geo = tweet['geo'];
    url = tweet['url'] ;

    radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
    radiu = radiu**0.5 * 100
    dis_index = int(radiu);

    if dis_index > 1000:
        return;

    if dis_index not in spread_list.keys():
        spread_list[dis_index] = {};
        spread_list[dis_index]['sum_freq'] = 0;
        spread_list[dis_index]['user_count'] = 0;
        spread_list[dis_index]['user'] = {};
        spread_list[dis_index]['sum_url_freq'] = 0;

    if user not in spread_list[dis_index]['user'].keys():
        spread_list[dis_index]['user'][user] = 0;
        spread_list[dis_index]['user_count'] += 1;

    spread_list[dis_index]['sum_freq'] += 1;
    if url is not None and not url == []:
        spread_list[dis_index]['sum_url_freq'] += 1;

#spread_list, the radio and rectangle for every half an hour
def spreadByTime(tweet, spread_list, begin_time, geo_center):
    time = tweet['time'];
    geo = tweet['geo'];
    url = tweet['url'];
    date_time = tweetTimeToDatetime(time);

    #every half hour
    unit = date_time - begin_time;
    day_time = unit.days * 24 * 60;
    time_index = int(unit.seconds / 60 + day_time);
    if time_index < 0 or time_index > 96*60:
        return;

    if time_index not in spread_list.keys():
        spread_list[time_index] = {};
        spread_list[time_index]['max_radiu'] = 0;
        spread_list[time_index]['min_radiu'] = 720;
        spread_list[time_index]['sum_radiu'] = 0;
        spread_list[time_index]['tweet_count'] = 0;
        spread_list[time_index]['url_max_radiu'] = 0;
        spread_list[time_index]['url_min_radiu'] = 720;
        spread_list[time_index]['url_sum_radiu'] = 0;
        spread_list[time_index]['url_tweet_count'] = 0;
        
        #up down left right
        #spread_list[time_index]['rect'] = [geo[], 0, 0, 0];

    #check the current spread radio 
    radiu = (geo[0] - geo_center[0])**2 + (geo[1] - geo_center[1])**2;
    radiu = radiu**0.5
    if radiu > spread_list[time_index]['max_radiu']:
        spread_list[time_index]['max_radiu'] = radiu;
    if radiu < spread_list[time_index]['min_radiu']:
        spread_list[time_index]['min_radiu'] = radiu;
    
    spread_list[time_index]['sum_radiu'] += radiu;
    spread_list[time_index]['tweet_count'] += 1;
    
    if url is not None and not url == []:
        print url
        if radiu > spread_list[time_index]['url_max_radiu']:
            spread_list[time_index]['url_max_radiu'] = radiu;
        if radiu < spread_list[time_index]['url_min_radiu']:
            spread_list[time_index]['url_min_radiu'] = radiu;
    
        spread_list[time_index]['url_sum_radiu'] += radiu;
        spread_list[time_index]['url_tweet_count'] += 1;

    #check the current spread rectangle
    #if geo[0] < spread_list[time_index]['rect'][0]:
    #    spread_list[time_index]['rect'][0] = geo[0]
    #if geo[0] > spread_list[time_index]['rect'][1]:
    #    spread_list[time_index]['rect'][1] = geo[0]
    #if geo[1] < spread_list[time_index]['rect'][2]:
    #    spread_list[time_index]['rect'][0] = geo[1]
    #if geo[1] > spread_list[time_index]['rect'][4]:
    #    spread_list[time_index]['rect'][1] = geo[1]
    
def spreadSpeed(tweet_fold, begin_time, geo_center, spread_list, spread_dis_list):
    term_users = {};
    files = os.listdir(tweet_fold);
    #spread_list = {};
    #spread_dis_list = {};

    count = [0,0]; #record the text and url tweet number
    for afile in files:
        if not fnmatch.fnmatch(afile, '*_2?.txt'):
            continue
        path = tweet_fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);   
        for tweet in tweets:
            count[0] += 1;
            if not tweet['url'] == []:
                count[1] += 1;

            spreadByTime(tweet, spread_list, begin_time, geo_center)
            spreadByDis(tweet, spread_dis_list, geo_center)

    print count
    #return spread_list, spread_dis_list;

def spreadSpeedMain():
    begin_time = datetime.datetime(2011, 3, 11, 5, 46, 24);
    #geo_center = [38.297, 142.372]
    #geo_center = [43.60, 172.55]
    geo_center = [35.68, 139.69]

    spread_list = {};
    spread_dis_list = {};
    #fold = '../duration/data/jpeq_world/weiTTL/';
    #spreadSpeed(fold, begin_time, geo_center, spread_list, spread_dis_list);
    fold = '../duration/data/earthquake_NZ/weiTTL/'
    #fold = '../media/earthquake/data/event/jpeq_jp/tweet/';
    spreadSpeed(fold, begin_time, geo_center, spread_list, spread_dis_list);

    return;

    outfilename = 'data/event/jpeq_world/spread_speed.txt';
    outfile = file(outfilename, 'w');
    json.dump(spread_list, outfile);
    outfile.write('\n');
    for dis_index in spread_dis_list.keys():
        del spread_dis_list[dis_index]['user'];
    json.dump(spread_dis_list, outfile);
    outfile.close();

spreadSpeedMain();
