#!/usr/bin/pythoni
# -*- coding: utf-8 -*-

#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
import os, datetime, gzip, cjson, json
from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json


def isTweetInUS(tweet_info):
    lati_down = 26.2;
    lati_up = 49.3;
    longi_left = -125.2;
    longi_right = -66.2; 
       
    corrdi = tweet_info['corrdinate'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            
            url = tweet_info['url'];
            if url != None and url != []:
                return 1;

    return 0;

global hashtag_set;

def tagFreqCount(tweet_info, tag_dic):
    global hashtag_set;
    #if 1:
    if isTweetInUS(tweet_info) == 1:
        text = tweet_info['text'];
        is_related = 0;
        
        # add all the hashtags related to earthquake
        tags = tweet_info['hashtag'];
        if text.find('NBA') > 0 or string.lower(text).find('basketball') > 0:
            is_related = 1;
            for tag in tags:
                hashtag_set[tag] = 0;

        #add all the hashtags related to earthquake related hashtag
        for tag in tags:
            if hashtag_set.get(tag) != None:
                is_related = 1;
                break;
       
        if is_related == 1:
            for tag in tags:
                hashtag_set[tag] = 0;
        else:
            return;

        time = datetime.datetime.strptime(tweet_info['time'],'%a %b %d %H:%M:%S +0000 %Y')
        for tag in tags:
            value = tag_dic.get(tag);
            if value == None:
                value = [1, time];
                tag_dic[tag] = value;
            else:
                value[0] = value[0] + 1;
                value.append(time);
        #for tag in tag_list:
        #    if string.find(tweet_info['text'].encode('utf-8'), tag) > 0:
        #        value = tag_dic.get(tag);
        #        if value == None:
        #            value = [1, time];
        #            tag_dic[tag] = value;
        #        else:
        #            value[0] = value[0] + 1;
        #            value.append(time);
       

def putTagInbins(dic, time_from, time_to):
    bin_num = 100;
    dic_bin = {};
    for key in dic.keys():
        item = dic[key];
        hist, bin_edges = np.histogram(date2num(item[1:len(item)]), bins = np.linspace(date2num(time_from), date2num(time_to), num=100));       
        dic_bin[key] = [item[0], hist];
    return dic_bin;

def main():
    global hashtag_set;
    hashtag_set = {};
    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/2012/';
    dic = {};
    getter = GetTweets();
    from_day = 1
    to_day = 15

    count = 0;
    month_from = 2;
    month_to = 3; # < month_to 

    for month in range(month_from, month_to):
        day_begin = from_day;
        day_end = to_day;
        if month_from < month_to - 1:
            if month == month_from:
                day_end = 30;
            if month > month_from and month < month_to -1:
                day_end = 30;
                day_begin = 1;
            if month == month_to -1:
                day_begin = 1;

        for days in range(day_begin, day_end): # NBA
            path = main_path+str(month)+'/'+str(days)+'/';
            dirList=os.listdir(path);
        
            for tweet_file in dirList:
                file_name = path+tweet_file;
                print file_name;
                for tweet in getter.iterateTweetsFromGzip(file_name):
                    #print tweet;
                    [rel, tweet_info] = getter.parseTweet(tweet); 
                    tagFreqCount(tweet_info, dic);
                    #count = count + 1;
                    #if count > 1000:
                   #break;

    date_from = datetime.datetime(2012, month_from, from_day, 0, 0);
    date_to = datetime.datetime(2012, month_to-1, to_day, 0, 0);
    dic = putTagInbins(dic, date_from, date_to);

    file_out = file('./output/NBA_tag_freq.txt', 'w');

    for key in dic.keys():
        if dic[key][0] < 10:
            continue;
        file_out.write(key.encode('utf-8')+'\t'+str(dic[key][0])+'\t');
        for i in range(0, len(dic[key][1])):
            file_out.write(str(dic[key][1][i]) + '\t')
        file_out.write('\n');
    file_out.close();

main();
