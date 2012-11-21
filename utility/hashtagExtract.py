#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import numpy as np
import operator
import string
import math
simplejson = json
from common import *
from boundingBox import * 
from getTweets import GetTweets
from tokenization import *
from loadFile import *
from settings import Settings

global hashtag_set;

#according to oneday
def getIndexForBinDay(begin, end, time):
    index = -1;
    if time >= begin and time <= end:
        values = time - begin;
        values = values.days*3600*24 + values.seconds;
        index = math.floor(values/86400); 
    return index;

#per hour
def getIndexForBinHour(begin, end, time):
    index = -1;
    if time >= begin and time <= end:
        values = time - begin;
        values = values.days*3600*24 + values.seconds;
        index = math.floor(values/3600); 
    return index;

def getIndexForBin(begin, end, time, bin_num):
    interval = end - begin;
    interval = (interval.days*3600*24 + interval.seconds)/float(bin_num);
    index = -1;
    if time >= begin and time <= end:
        values = time - begin;
        values = values.days*3600*24 + values.seconds;
        index = math.floor(values/interval) 
    return index;

#according to global map
def getIndexForBoxGlobal(lati, longi):
    lati_index = math.floor((lati + 90)/1.8);
    longi_index = math.floor((longi + 180)/3.6);
    
    return lati_index, longi_index;

def getIndexForBox(bb, lati, longi, bin_num):
    lati_up = bb[0];
    lati_down = bb[1];
    longi_left = bb[2];
    longi_right = bb[3]; 
 
    lati_step = (lati_up - lati_down)/float(bin_num);
    longi_step = (longi_right - longi_left)/float(bin_num);
          
    lati_index = -1;
    longi_index = -1;
    if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
        lati_index = math.floor((lati - lati_down)/lati_step);
        longi_index = math.floor((longi - longi_left)/longi_step);
    
    return lati_index, longi_index;

def tagTimeBinHour(tweet_info, begin, end, bin_num, tag_timebin):
    tags = tweet_info['hashtag'];
    if tags == [] or tags == None:
        return;

    time = datetime.datetime.strptime(tweet_info['time'],'%a %b %d %H:%M:%S +0000 %Y')
    index = getIndexForBinHour(begin, end, time);
    if index < 0 or index >= bin_num:
        return;

    for tag in tags:
        tag = string.lower(tag);
        bins = tag_timebin.get(tag);
        if bins == None:
            bins = allocMatrix(1, bin_num);
            tag_timebin[tag] = bins;
        
        bins[index] = bins[index] + 1;


def tagTimeBin(tweet_info, begin, end, bin_num, tag_timebin):
    tags = tweet_info['hashtag'];
    if tags == [] or tags == None:
        return;

    time = datetime.datetime.strptime(tweet_info['time'],'%a %b %d %H:%M:%S +0000 %Y')
    index = getIndexForBinDay(begin, end, time);
    if index < 0 or index >= bin_num:
        return;

    for tag in tags:
        tag = string.lower(tag);
        bins = tag_timebin.get(tag);
        if bins == None:
            bins = allocMatrix(1, bin_num);
            tag_timebin[tag] = bins;
        
        bins[index] = bins[index] + 1;

def tagLocGrids(tweet_info, bb, bin_num, tag_locgrids):
    tags = tweet_info['hashtag'];
    if tags == [] or tags == None:
        return;

    geo = tweet_info['geo'];
    lati_index, longi_index = getIndexForBox(bb, lati, longi, bin_num);
    if lati_index < 0 or lati_index >= bin_num:
        return;
    if longi_index < 0 or longi_index >= bin_num:
        return;

    for tag in tags:
        tag = string.lower(tag);
        grid = tag_locgrids.get(tag);
        if bins == None:
            grid = allocMatrix(bin_num, bin_num);
            tag_timebin[tag] = grid;
        
        grid[lati_index][longi_index] = grid[lati_index][longi_index] + 1;

def tagUsers(tweet_info, bb, tag_users):
    tags = tweet_info['user'];
    if tags == [] or tags == None:
        return;

    user = tweet_info['user'];
    if user == [] or user == None:
        return;

    for tag in tags:
        tag = string.lower(tag);
        user_list = tag_users.get(tag);
        if user_list == None:
            user_list = allocMatrix(1, bin_num);
            tag_users[tag] = user_list;
        
        user_list.append(user);

#for global map
def tagMapMatrix(tweet_info, bb, array_num, tag_matrix):
    geo = tweet_info['geo'];
    index = -1;
    if geo != None and geo != []:
        index1, index2 = getIndexForBoxGlobal(geo[0], geo[1]);
    else:
        return;
    if index1 < 0 or index1 >= array_num or index2 < 0 or index2 >= array_num:
        return;

    tags = tweet_info['hashtag'];
    for tag in tags:
        tag = string.lower(tag);
        matrix = tag_matrix.get(tag);
        if matrix == None:
            matrix = allocMatrix(array_num, array_num);
            tag_matrix[tag] = matrix;
        
        matrix[index1][index2] = matrix[index1][index2] + 1;
        
def tagFreqCount(bb, tweet_info, tag_dic):
    if isTweetInbb(bb, tweet_info) == 1:
        # add all the hashtags related to earthquake
        tags = tweet_info['hashtag'];

        for tag in tags:
            tag = string.lower(tag);
            value = tag_dic.get(tag);
            if value == None:
                tag_dic[tag] = 1;
            else:
                tag_dic[tag] = tag_dic[tag] + 1;

        return 1;
    return 0;

def tagFreqCountFromSeeds(bb, tweet_info, tag_dic, seeds):
    is_related = 0;
    if isTweetInbb(bb, tweet_info) == 1:
        text = tweet_info['text'];
        
        # add all the hashtags related to earthquake
        tags = tweet_info['hashtag'];
        temp_text = string.lower(text);
        for seed in seeds:
            if text.find(seed) >= 0:
                #print text;
                is_related = 1;
                break;
      
        if is_related == 1:
            for tag in tags:
                tag = string.lower(tag);
                value = tag_dic.get(tag);
                if value == None:
                    tag_dic[tag] = 1;
                else:
                    tag_dic[tag] = tag_dic[tag] + 1;
      
    return is_related; 

#interface to the outside
#extract tags from seeds, time. location
def tagExtractFromSeeds(year, month, from_day, to_day, bb, seeds, time_binfile, count_file):
    getter = GetTweets();
    main_path = Settings.tweets_folder + str(year) + '/';
    tag_count = {};
    tag_bins = {};
    tag_matrix = {};
    begin = datetime.datetime(year, month, from_day, 0, 0, 0);
    end = datetime.datetime(year, month, to_day, 0, 0, 0);

    for days in range(from_day, to_day):
        path = main_path + str(month) + '/' + str(days) + '/';
        if not os.path.isdir(path):
            continue;

        dirList=os.listdir(path);
    
        for tweet_file in dirList:
            file_name = path+tweet_file;
            print file_name;
            for tweet in getter.iterateTweetsFromGzip(file_name):
                [rel, tweet_info] = getter.parseTweet(tweet); 
                ret = tagFreqCountFromSeeds(bb, tweet_info, tag_count, seeds);
                if ret > 0:
                    tagTimeBin(tweet_info, begin, end, to_day - from_day + 2, tag_bins);

    outfile_bin = file(time_binfile, 'w')
    outfile_count = file(count_file, 'w') 
  
    sort_tag = {};
    for tag, freq in sorted(tag_count.iteritems(), key=lambda (k,v):(v,k), reverse = True):
        json.dump(tag, outfile_count);
        outfile_count.write('\t' + str (freq) + '\n');

        print tag, freq;
        sort_tag[tag] = freq;
        if tag in tag_bins.keys():
            json.dump(tag, outfile_bin);
            outfile_bin.write('\n');
            json.dump(tag_bins[tag], outfile_bin);
            outfile_bin.write('\n');
    outfile_bin.close();
    outfile_count.close();

    return sort_tag;

#interface to the outside
#extract tags from time. location
def tagExtract(year, month, from_day, to_day, bb, time_binfile, count_file):
    getter = GetTweets();
    main_path = Settings.tweets_folder + str(year) + '/';
    tag_count = {};
    tag_bins = {};
    tag_matrix = {};
    begin = datetime.datetime(year, month, from_day, 0, 0, 0);
    end = datetime.datetime(year, month, to_day, 0, 0, 0);

    for days in range(from_day, to_day):
        path = main_path + str(month) + '/' + str(days) + '/';
        if not os.path.isdir(path):
            continue;

        dirList=os.listdir(path);
    
        for tweet_file in dirList:
            file_name = path+tweet_file;
            print file_name;
            for tweet in getter.iterateTweetsFromGzip(file_name):
                [rel, tweet_info] = getter.parseTweet(tweet); 
                tagFreqCount(bb, tweet_info, tag_count);
                tagTimeBin(tweet_info, begin, end, to_day - from_day + 2, tag_bins);

    outfile_bin = file(time_binfile, 'w')
    outfile_count = file(count_file, 'w') 
  
    sort_tag = {};
    for tag, freq in sorted(tag_count.iteritems(), key=lambda (k,v):(v,k), reverse = True):
        json.dump(tag, outfile_count);
        outfile_count.write('\t' + str (freq) + '\n');

        print tag, freq;
        sort_tag[tag] = freq;
        if tag in tag_bins.keys():
            json.dump(tag, outfile_bin);
            outfile_bin.write('\n');
            json.dump(tag_bins[tag], outfile_bin);
            outfile_bin.write('\n');
    outfile_bin.close();
    outfile_count.close();

    return sort_tag;

#extract tags from time. location
#output the tag_count, time_bins, users, location grids
def tagExtract(year, month, from_day, to_day, bb, count_file, time_file, loc_file, user_file):
    getter = GetTweets();
    main_path = Settings.tweets_folder + str(year) + '/';
    tag_count = {};
    tag_bins = {};
    tag_matrix = {};
    tag_locs = {};
    tag_users = {};
    begin = datetime.datetime(year, month, from_day, 0, 0, 0);
    end = datetime.datetime(year, month, to_day, 0, 0, 0);

    for days in range(from_day, to_day):
        path = main_path + str(month) + '/' + str(days) + '/';
        if not os.path.isdir(path):
            continue;

        dirList=os.listdir(path);
    
        for tweet_file in dirList:
            file_name = path+tweet_file;
            print file_name;
            for tweet in getter.iterateTweetsFromGzip(file_name):
                [rel, tweet_info] = getter.parseTweet(tweet); 
                tagFreqCount(bb, tweet_info, tag_count);
                tagTimeBin(tweet_info, begin, end, to_day - from_day + 2, tag_bins);
                #divide the bb into 100*100
                tagLocGrids(tweet_info, bb, 100, tag_locs);
                tagUsers(tweet_info, tag_users);

    outfile_bin = file(time_binfile, 'w')
    outfile_count = file(count_file, 'w') 
    outfile_loc = file(loc_file, 'w')
    outfile_user = file(loc_file, 'w')

    #write the period and the bouding box
    json.dump(tag_bins, outfile_bin);
    outfile_bin.write('\n');

    json.dump(tag_locs, outfile_loc);
    outfile_loc.write('\n');

    sort_tag = {};
    for tag, freq in sorted(tag_count.iteritems(), key=lambda (k,v):(v,k), reverse = True):
        json.dump(tag, outfile_count);
        #write the count
        outfile_count.write('\t' + str (freq) + '\n');

        print tag, freq;
        #write the time bins
        sort_tag[tag] = freq;
        if tag in tag_bins.keys():
            json.dump(tag, outfile_bin);
            outfile_bin.write('\n');
            json.dump(tag_bins[tag], outfile_bin);
            outfile_bin.write('\n');
        
        #write the locs grids
        if tag in tag_locs.keys():
            json.dump(tag_locs[tag], outfile_loc);
            outfile_loc.write('\n');

        #write the users
        if tag in tag_users.keys():
            json.dump(tag_users[tag], outfile_user);
            outfile_user.write('\n');

    outfile_bin.close();
    outfile_count.close();
    outfile_loc.close();
    outfile_user.close();

    return sort_tag;
