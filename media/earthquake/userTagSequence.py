#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
from parser import HTMLParsers
from parser import Utilities

def isTweetInJapan(tweet_info):
    lati_down = 30.4;
    lati_up = 45.4;
    longi_left = 129.5;
    longi_right = 147.0; 
       
    corrdi = tweet_info['corrdinate'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            
            url = tweet_info['url'];
            if url != None and url != []:
                return 1;

    return 0;

def loadTags(filename):
    in_file = file(filename);
    lines = in_file.readlines();
    select_tags = [];
    for line in lines:
        items = line.split('\t');
        if int(items[1]) > 20:
            select_tags.append(items[0]);

    return select_tags;

def collectUserTags(hashtag_set):
    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/2011/';
    dic = {};
    getter = GetTweets();
    global g_user_taglist;
    g_user_taglist = {};
    count = 0;
    
    for month in range(3, 4):
        day_begin = 1;
        day_end = 10;

        for days in range(day_begin, day_end): # Japan earthquake
            path = main_path+str(month)+'/'+str(days)+'/';
            dirList=os.listdir(path);
        
            for tweet_file in dirList:
                file_name = path+tweet_file;
                print file_name;
                for tweet in getter.iterateTweetsFromGzip(file_name):
                    #print tweet;
                    [rel, tweet_info] = getter.parseTweet(tweet); 
                    
                    tags = tweet_info['hashtag'];
                    if tags == None or tags == []:
                        continue;

                    if not isTweetInJapan(tweet_info):
                        continue;

                    for tag in tags:
                        if tag not in hashtag_set:
                            continue;

                        user = tweet_info['user'];
                        tag_seq = g_user_taglist.get(user);
                        if tag_seq == None:
                            tag_seq = [];

                        simple_tweetinfo = {};
                        simple_tweetinfo['hashtag'] = tag;
                        simple_tweetinfo['time'] = tweet_info['time'];
                        simple_tweetinfo['corrdinate'] = tweet_info['corrdinate'];
                        #simple_tweetinfo['text'] = tweet_info['text'].encode('utf-8');
                        print simple_tweetinfo;
                        tag_seq.append(simple_tweetinfo);
                        g_user_taglist[user] = tag_seq;
                        count = count + 1;
                        #if count == 20:
                        #    return;

global g_user_taglist;

def writeUserTags():
    global g_user_tag_list;
    outfile = file('./output/US_NBA_user_tag_seq.txt', 'w');
    for user, tweet_info_list in g_user_taglist.iteritems():
        outfile.write(str(user)+'\n');
        for tweet_info in tweet_info_list:
            outfile.write(tweet_info['hashtag'] + '|' + tweet_info['time'] + '\t');
        outfile.write('\n');

    outfile.close();

def getUserTagSeqMain():
    hashtag_set = loadTags('./output/NBA_tag_freq.txt');
    collectUserTags(hashtag_set);
    writeUserTags();

getUserTagSeqMain();

