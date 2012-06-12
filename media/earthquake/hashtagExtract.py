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
import nltk
from Utility import *

tag_list = ['残','緊急', '爆発','停電','混雑','震','裂','摇','崩', 'earthquake', '災', '死', '惨', 'damage', '燃', '難', '煙', '지진', '壊', 'pray', '祈','donate', 'nuclear'];

g_select_tags = {'jpquake':[], 'TEPCO':[], 'nuclear':[], 'azk48':[], 'cameraplus':[], 'odawara':[], 'rakuteneagles':[], 'tigers':[], 'hanshin':[], 'Prayforjapan':[], 'imakoko_niigata_jp':[], 's_tour':[], 'Eye':[]};

def downloadPhoto(tweet, tag):
    services = {'twitpic': HTMLParsers.parseTwitpic, 'yfrog': HTMLParsers.parseYfrog, 'twitrpix': HTMLParsers.parseTwitrpix}
    service, url = 'twitpic', ''
    url = tweet['url'][0];
    for service, parseMethod in services.iteritems():
        if service in tweet['text']:
            for term in tweet['text'].split():
                    if service in term: 
                        url = term
                        break
    url = url.replace('\\', '')
    d = datetime.datetime.strptime(tweet['time'],'%a %b %d %H:%M:%S +0000 %Y')
    if not url.startswith('http'): url = 'http://'+url
    for service, parseMethod in services.iteritems():
        if service in url:
            id = tweet['id']
            fileName = './JapanImage/tags/'+tag+'/'+Utilities.getDataFile(d)+'/%s_%s.jpeg'%(str(d).replace(' ', '_'), id)
            print url, fileName
            folder = '/'.join(fileName.split('/')[:-1])
            if not os.path.exists(folder): os.makedirs(folder, 0777)
            if not os.path.exists(fileName):
                retry, notParsed = 0, True
                while retry<3 and notParsed:
                    try:
                        parseMethod(url, fileName)
                        notParsed = False
                        time.sleep(3)
                    except: retry+=1

global hashtag_set;

def photoTagFreCount(tweet_info, tag_dic):
    global hashtag_set;
    tags = tweet_info['tags'];
    title = tweet_info['basic1']['title'];
    discription = tweet_info['discription'];
    is_related = 0;
    if title.find('earthquake') >= 0 or title.find('\\u5730\\u9707') >= 0 or discription.get('earthquake') != None or discription.get('\\u5730\\u9707') != None: 
        is_related = 1;
    
    if is_related == 0:
        try:
            if tags.index('earthquake') >= 0 or tags.index('\\u5730\\u9707') >= 0:
                is_related = 1;
        except:
            pass;

    if is_related == 1:
        time = datetime.datetime.strptime(tweet_info['dates']['taken'],'%Y-%m-%d %H:%M:%S')
        for tag in tags:
            hashtag_set[tag] = 0;
            
            value = tag_dic.get(tag);
            if value == None:
                value = [1, time];
                tag_dic[tag] = value;
            else:
                value[0] = value[0] + 1;
                value.append(time);

def selectedTagFreq(tweet_info):
    tags = tweet_info['hashtag'];
    url = tweet_info['url'];
    if url == None or url == []:
        return;

    for tag in tags:
        value = g_select_tags.get(tag);
        if value != None:
            value.append(url);
        downloadPhoto(tweet_info, tag);

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

def tagMapMatrix(tweet_info, bb, array_num, tag_matrix):
    geo = tweet_info['corrdinate'];
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
        
def tagFreqCountWorld(tweet_info, tag_dic):
    ret = 0;
    if 1:
    #if isTweetInJapan(tweet_info) == 1:
        # add all the hashtags related to earthquake
        tags = tweet_info['hashtag'];

        for tag in tags:
            tag = string.lower(tag);
            value = tag_dic.get(tag);
            if value == None:
                tag_dic[tag] = 1;
            else:
                tag_dic[tag] = tag_dic[tag] + 1;

def tagFreqCount(tweet_info, tag_dic):
    global hashtag_set;
    ret = 0;
    #if 1:
    if isTweetInUS(tweet_info) == 1:
    #if isTweetInJapan(tweet_info) == 1:
        text = tweet_info['text'];
        is_related = 0;
        
        # add all the hashtags related to earthquake
        tags = tweet_info['hashtag'];
        temp_text = string.lower(text);
        #if temp_text.find('earthquake') > 0 or temp_text.encode('utf-8').find('震') > 0:
        if text.find('tornado') > 0 or text.find('hurricane') > 0 or text.find('irene') > 0:
        #if text.find('wedding') > 0 or text.find('royal') > 0:
        #if text.find('romney') or text.find('santorum'):
        #if (text.find('president') > 0 or text.find('presidential') >0) and (text.find('election') or text.find('candidate') or text.find('campaign')) > 0:
        #if text.find('kony') > 0 or text.find('kony2012') > 0: 
            print text;
            is_related = 1;
            for tag in tags:
                hashtag_set[tag] = 0;

        #add all the hashtags related to earthquake related hashtag
        #for tag in tags:
        #    if hashtag_set.get(tag) != None:
        #        is_related = 1;
        #        break;
       
        if is_related == 1:
            for tag in tags:
                tag = string.lower(tag);
                hashtag_set[tag] = 0;
        else:
            return 0;

        print tweet_info['id'], tweet_info['time'];
        print tweet_info['text'].encode('utf-8');
        #if tags != [] and tags != None:
            #print tweet_info;

        time = datetime.datetime.strptime(tweet_info['time'],'%a %b %d %H:%M:%S +0000 %Y')
        for tag in tags:
            tag = string.lower(tag);
            value = tag_dic.get(tag);
            if value == None:
                value = [1, time];
                tag_dic[tag] = value;
            else:
                value[0] = value[0] + 1;
                value.append(time);
        
        return 1; 

def putTagInbins(dic, time_from, time_to, bin_num):
    dic_bin = {};
    for key in dic.keys():
        item = dic[key];
        hist, bin_edges = np.histogram(date2num(item[1:len(item)]), bins = np.linspace(date2num(time_from), date2num(time_to), num=bin_num));       
        dic_bin[key] = [item[0], hist];
    return dic_bin;

def binsOfTag(tag_dic, year, month, from_day, to_day, bin_num, outfilename):
    date_from = datetime.datetime(year, month, from_day, 0, 0);
    date_to = datetime.datetime(year, month, to_day, 0, 0);
    dic = putTagInbins(tag_dic, date_from, date_to, bin_num);

    file_out = file(outfilename, 'w');

    for key in dic.keys():
        if dic[key][0] < 10:
            continue;
        file_out.write(key.encode('utf-8') + '\t'+str(dic[key][0])+'\t');
        for i in range(0, len(dic[key][1])):
            file_out.write(str(dic[key][1][i]) + '\t')
        file_out.write('\n');
    file_out.close();

def tagWorldMain(is_selected):
    from_day = 1
    to_day = 31
    year = 2011;
    count = 0;
    month = 3;

    getter = GetTweets();
    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/' + str(year) + '/';
    tag_count = {};
    tag_bins = {};
    tag_matrix = {};
    bb = [90, -90, -180, 180];
    begin = datetime.datetime(year, month, from_day, 0, 0, 0);
    end = datetime.datetime(year, month, to_day, 0, 0, 0);
    bin_num = 100;

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
                tagFreqCountWorld(tweet_info, tag_count);
                tagTimeBin(tweet_info, begin, end, 31, tag_bins);
                #tagMapMatrix(tweet_info, bb, 100, tag_matrix); 

    outfile_bin = file('./output/Event/world_tag_bin_2011_3.txt', 'w')
    outfile_matrix = file('./output/Event/world_tag_matrix_2011_3.txt', 'w')
    outfile_count = file('./output/Event/world_tag_count_2011_3.txt', 'w') 
  
    for tag, freq in sorted(tag_count.iteritems(), key=lambda (k,v):(v,k), reverse = True):
        if freq < 50:
            continue;

        json.dump(tag, outfile_count);
        outfile_count.write('\t' + str (freq) + '\n');

        print tag, freq;
        if tag in tag_bins.keys():
            json.dump(tag, outfile_bin);
            outfile_bin.write('\n');
            json.dump(tag_bins[tag], outfile_bin);
            outfile_bin.write('\n');

        #if tag in tag_matrix.keys():
        #    json.dump(tag, outfile_matrix);
        #    outfile_matrix.write('\n');
        #    json.dump(tag_matrix[tag], outfile_matrix);
        #    outfile_matrix.write('\n');

    outfile_bin.close();
    outfile_matrix.close();
    outfile_count.close();

def tagJapanMain(is_selected):
    global hashtag_set;
    hashtag_set = {};
    dic = {};
    getter = GetTweets();
    from_day = 20
    to_day = 30
    year = 2011;
    count = 0;
    month_from = 8;
    month_to = 9; #<4

    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/' + str(year) + '/';
    outtweets_file = file('output/US_hurricane_tweets.txt', 'w');
    for month in range(month_from, month_to):
        day_begin = from_day;
        day_end = to_day;
        #if month == month_from:
        #    day_end = 30;
        #if month > month_from and month < month_to -1:
        #    day_end = 30;
        #    day_begin = 1;
        #if month == month_to -1 and month > month_from:
        #    day_begin = 1;

        for days in range(day_begin, day_end): # Japan earthquake
            path = main_path+str(month)+'/'+str(days)+'/';
            if not os.path.isdir(path):
                continue;

            dirList=os.listdir(path);
        
            for tweet_file in dirList:
                file_name = path+tweet_file;
                print file_name;
                for tweet in getter.iterateTweetsFromGzip(file_name):
                    #print tweet;
                    [rel, tweet_info] = getter.parseTweet(tweet); 
                    if is_selected == 0:
                        ret = tagFreqCount(tweet_info, dic);
                        if ret == 1:
                            json.dump(tweet_info, outtweets_file);
                            outtweets_file.write('\n');
                    else:
                        selectedTagFreq(tweet_info);
                    #count = count + 1;
                    #if count > 1000:
                   #break;
    #print g_select_tags;
    outtweets_file.close();
    file_out = file('./output/selected_tag_photos.txt', 'w');
    for key, urllist in g_select_tags.iteritems():
        file_out.write(key+'\n');
        for url in urllist:
            file_out.write(url[0] + '\n');
        file_out.write('\n');
    file_out.close();

    date_from = datetime.datetime(year, month_from, from_day, 0, 0);
    date_to = datetime.datetime(year, month_to-1, to_day, 0, 0);
    dic = putTagInbins(dic, date_from, date_to, 10);

    file_out = file('./output/US_hurricane_tag_freq.txt', 'w');

    for key in dic.keys():
        #if dic[key][0] < 10:
        #    continue;
        file_out.write(key.encode('utf-8') + '\t'+str(dic[key][0])+'\t');
        for i in range(0, len(dic[key][1])):
            file_out.write(str(dic[key][1][i]) + '\t')
        file_out.write('\n');
    file_out.close();

def extractTagFromPhotos():
    global hashtag_set;
    hashtag_set = {};
    main_path = '/mnt/chevron/kykamath/data/twitter/twitter_pics/japan/JapanPhoto2';
    dirs = os.listdir(main_path);

    dics = {};
    for dir in dirs:
        filename = main_path + '/' + dir + '/PhotoInfo.txt';
        file_in = file(filename);
        lines = file_in.readlines();
        for line in lines:
            tweet_info = cjson.decode(line);
            photoTagFreCount(tweet_info, dics);
        file_in.close();

    date_from = datetime.datetime(2011, 3, 11, 0, 0);
    date_to = datetime.datetime(2011, 3, 20, 0, 0);
    dic = putTagInbins(dics, date_from, date_to, 20);

    file_out = file('./output/photo_tag_freq.txt', 'w');

    for key in dic.keys():
        #if dic[key][0] < 2:
        #    continue;
        file_out.write(key.encode('utf-8')+'\t'+str(dic[key][0])+'\t');
        for i in range(0, len(dic[key][1])):
            file_out.write(str(dic[key][1][i]) + '\t')
        file_out.write('\n');
    file_out.close();

#extractTagFromPhotos();
def loadSelectedTags():
    in_file = file('selected_tags.txt');
    #in_file = file('select_tag_list.txt');
    lines = in_file.readlines();
    global g_select_tags;
    g_select_tags = {};
    for line in lines:
        g_select_tags[line[0:len(line)-1]] = [];

#extractTagFromPhotos();
#loadSelectedTags();
#tagJapanMain(0);
tagWorldMain(0);
