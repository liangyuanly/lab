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
#from parser import HTMLParsers
#from parser import Utilities
import ast
import nltk
#from nltk.tokenize import RegexpTokenizer
#from nltk.tokenize.api import *
from tinysegmenter import *
from settings import Settings
from operator import itemgetter
import random

g_stop_symbol = [' ', '\t', '\n', '.', ',', ':', ';', '?', '"', '-', '!', '(', ')', '。', '，', '\\', '/', '！', '；', '‘', '“','［', '］', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '？', '_', '@'];

g_segmenter = TinySegmenter();

def tokenize(text, language, stop_words):
    # tokenize
    if language == 'Japanese':
        tokens = g_segmenter.tokenize(text);
    else:
        text = string.lower(text);
        tokens = text.split(' ');
    
    sel_tokens = {};
    sel_tokens['TotalTokenNum'] = 0;
    for token in tokens:
        token = string.lower(token);
        token = token.strip();

        #token = token.encode('utf-8');        
        if token == '' or token == ' ' or token == '\t' or token == '\n':
            continue;

        end = len(token) - 1;
        while end >= 0 and (token[end] in g_stop_symbol):
            token = token[0:end];
            end = end - 1;
                
        if token == '':
            continue;

        begin = 0;
        while begin >= 0 and begin < len(token) and (token[begin] in g_stop_symbol):
            begin = begin + 1;
            if begin < len(token) - 1:
                token = token[begin:len(token)];
            else:
                if begin == len(token) - 1:
                    token = '';
                break;

        if token in stop_words:
            continue;
                
        if token.find('http') >= 0:
            continue;
                
        if token == '' or token == ' ' or token == '\t' or token == '\n':
            continue;

        #if len(token) < 2:
        #    continue;
            
        freq = sel_tokens.get(token);
        if freq == None:
            sel_tokens[token] = 1;
        else:
            sel_tokens[token] = sel_tokens[token] + 1;

        sel_tokens['TotalTokenNum'] = sel_tokens['TotalTokenNum'] + 1;

    return sel_tokens;

# token and text
def similarity4(token, text):
    text = string.lower(text);
    if text.find(token) >= 0:
        #print token, text;
        return 1;

    return 0;
 
def similarity3(sel_tokens, text):
    text = string.lower(text);
    for token in sel_tokens:
        if text.find(token) >= 0:
            #print token, text;
            return 1;

    return 0;
  
#list of token comparison
def similarity2(sel_tokens, tokens):
    score = 0;
    num = tokens['TotalTokenNum'];
    for token, freq in tokens.iteritems():
        if token == "TotalTokenNum":
            continue;
        #print token.encode('utf-8');
        if token in sel_tokens:
            score = score + freq;
    return score;


def similarity(sel_tokens, tokens):
    score = 0;
    num = tokens['TotalTokenNum'];
    for token, freq in tokens.iteritems():
        if token == "TotalTokenNum":
            continue;
        #print token.encode('utf-8');
        if token in sel_tokens.keys():
            score = score + freq;
    
    return score;

def isTweetInNZ(tweet_info):
    lati_up  = -34.3;
    lati_down = down = -47.4;
    longi_left = 166.2;
    longi_right = 178.9;

    corrdi = tweet_info['corrdinate'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            
            url = tweet_info['url'];
            if url != None and url != []:
                return 1;

    return 0;

def isTweetInUS(tweet_info):
    lati_down = 29.6;
    lati_up = 49.1;
    longi_left = -125.5;
    longi_right = -69.3; 
       
    corrdi = tweet_info['corrdinate'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            
            url = tweet_info['url'];
            if url != None and url != []:
                return 1;

    return 0;

def isTweetInUK(tweet_info):
    lati_down = 49.5;
    lati_up = 59.0;
    longi_left = -11.3;
    longi_right = 2.8; 
       
    corrdi = tweet_info['corrdinate'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            
            url = tweet_info['url'];
            if url != None and url != []:
                return 1;

    return 0;


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

def loadStopwords(filename):
    in_file = file(filename);
    lines = in_file.readlines();
    stop_words = [];
    mark = 0;
    for line in lines:
        line = line.strip();
   
        if line == "unicode":
            mark = 1;
            continue;
        
        if mark > 0:
            line = unicode(line, 'utf-8');
        if line == '' or line == ' ' or line == '\n' or line == '\t':
            continue;
    
        if line[len(line)-1] == '\n' or line[len(line)-1] == '\t':
            line = line[0:len(line)-1];
 
        stop_words.append(line);

    return stop_words;

def tweetTimeToDatetime(time):
    d = datetime.datetime.strptime(time,'%a %b %d %H:%M:%S +0000 %Y');
    return d;

def datetimeToStr2(time):
    f = "%Y-%m-%d_%H_%M_%S";
    time_str = datetime.datetime.strftime(time, f);
    return time_str;

def datetimeToStr(time):
    f = "%Y-%m-%d_%H:%M:%S";
    time_str = datetime.datetime.strftime(time, f);
    return time_str;

def genFileName2(id, time): 
    datetime = tweetTimeToDatetime(time);
    time_str = datetimeToStr2(datetime);
    filename = time_str + '_' + str(id);
    
    return filename;

def genFileName(id, time): 
    datetime = tweetTimeToDatetime(time);
    time_str = datetimeToStr(datetime);
    filename = time_str + '_' + str(id);
    
    return filename;

#load the tweets from a file
def loadTweetsFromGZ(filename):
    getter = GetTweets();
    tweet_list = [];
    for tweet in getter.iterateTweetsFromGzip(filename):
        [rel, tweet_info] = getter.parseTweet(tweet);
        #tweet_list.append(tweet_info);
        yield tweet;

    #return tweet_list;

#load the tweets from a file
def loadTweetsFromGZ(filename, location):
    getter = GetTweets();
    tweet_list = [];
    for tweet in getter.iterateTweetsFromGzip(filename):
        [rel, tweet_info] = getter.parseTweet(tweet);
        if location == 'JP':
            if not isTweetInJapan(tweet_info):
                continue;
        if location == 'NZ':
            if not isTweetInNZ(tweet_info):
                continue;
        if location == 'US':
            if not isTweetInUS(tweet_info):
                continue;
        if location == 'UK':
            if not isTweetInUK(tweet_info):
                continue;

        tweet_list.append(tweet_info);

    return tweet_list;


#load the tweets from a file
def loadTweetsFromFile(filename):
    getter = GetTweets();
    tweet_list = [];
    infile = file(filename);
    lines = infile.readlines();
    for line in lines:
        tweet = cjson.decode(line);
        [rel, tweet_info] = getter.parseTweet(tweet);
        tweet_list.append(tweet_info);

    return tweet_list;

#load the simple tweets from a file
def loadSimpleTweetsFromFile(filename):
    tweet_list = [];
    infile = file(filename);
    lines = infile.readlines();
    for line in lines:
        tweet = cjson.decode(line);
        tweet_list.append(tweet);

    return tweet_list;

def loadTweetsForImage(image_list, tweet_list):
    getter = GetTweets();
    image_tweet = [];
    ids = [];
    for image in image_list:
        if len(image) < 1:
            continue;

        index1 = string.find(image, '_');
        hour = int(image[0:index1])
        hour = hour - 6;
        if hour < 0:
            hour = hour + 24;
        index2 = string.rfind(image, '_');
        print image;
        if index2 >= 0:
            id = np.uint64(image[index2+1:len(image)]);
        else:
            continue;
        
        ids.append(id);

    for tweet in tweet_list:
        id = tweet['id'];
        if id in ids:
            image_tweet.append(tweet);

    return image_tweet;

def loadPhotos(dirname):
    dir_list = os.listdir(dirname);
    id_list = [];
    for fname in dir_list:
        index = string.find(fname, '_');
        id = fname[index+1:len(fname)-5];
        id_list.append(id);

    return id_list;

def loadPhotoPath(dirname):
    dir_list = os.listdir(dirname);
    id_list = [];
    for fname in dir_list:
        id_list.append(id);

    return id_list;

def loadPhotos2(dirname):
    dir_list = os.listdir(dirname);
    id_list = [];
    for dir in dir_list:
        sub_dir = dirname + dir + '/';
        files = os.listdir(sub_dir);
        for fname in files:
            if fname[len(fname)-1:len(fname)] == 'txt':
                continue;
            id_list.append(sub_dir + fname);

    return id_list;

def loadPhotoInfo(filename):
    infile = file(filename);
    lines = infile.readlines();
    tweet_list = [];
    for line in lines:
        index = line.find("id");
        index2 = line.find("time");
        if index > 0 and index2 > 0:
            tweet = cjson.decode(line);
            tweet_list.append(tweet);
    return tweet_list;

#find the tweets for the images
def loadImageTweets(image_list, tweet_list):
    image_set = {};
    for image in image_list:
        index2 = string.rfind(image, '_');
        if index2 >= 0:
            id = np.uint64(image[index2+1:len(image)]);
            image_set[id] = image;

    image_tweet_list = [];
    for tweet_info in tweet_list:
        id = tweet_info['id'];
        if id in image_set.keys():
            image_set.remove(id);
            tweet_info['path'] = image_set[id];
            image_tweet_list.append(tweet_info);

    return image_tweet_list;

def loadTerms(filename, format='utf-8'):
    infile = file(filename, 'rb');
    lines = infile.readlines();
    list = [];
    for line in lines:
        terms = line.split('\t');
        for term in terms:
            if term == '\n':
                continue;
            if term[len(term)-1] == '\n':
                term = term[0:len(term)-1]
            if format == 'utf-8':
                list.append(unicode(term, 'utf-8'));
            else:
                list.append(term);

    infile.close();
    return list;

#according to oneday
def getIndexForBinDay(begin, end, time):
    index = -1;
    if time >= begin and time <= end:
        values = time - begin;
        values = values.days*3600*24 + values.seconds;
        index = math.floor(values/86400); 
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
    # US
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

def allocMatrix(n, m):
    matrix = {};
    #array
    if n == 1:
        for j in range(0, m):
            matrix[j] = 0;
    else:
        for i in range(0, n):
            matrix[i] = {};
            for j in range(0, m):
                matrix[i][j] = 0;
    return matrix;

def norMatrix(matrix):
    sum = 0;
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            sum = sum + matrix[i][j];
    
    print sum;
    if sum == 0:
        return;

    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            matrix[i][j] = matrix[i][j]/float(sum);

def centerTokens(dist_matrix, cluster_label):
    new_centroid = [];
    for center, tokens in cluster_label.iteritems():
        min_dist = 1111111;
        new_center = center;
        for token in tokens:
            total_dist = 0;
            for token2 in tokens:
                total_dist = total_dist + dist_matrix[token][token2];
            if total_dist < min_dist:
                min_dist = total_dist;
                new_center = token;
        new_centroid.append(new_center);

    return new_centroid;

def kmeansTokens(matrix, K):
    list = matrix.keys();
    centroid = random.sample(list, K);
    label = {};
    dist = {};

    iter = 0;
    isChange = True;
    while iter < 100 and isChange:
        iter = iter + 1;
        # label the tokens
        cluster = {};
        for center in centroid:
            cluster[center] = [];

        for token in list:
            min_dis = 11111111;
            for center in centroid:
                if matrix[center][token] < min_dis:
                    min_dis = matrix[center][token];
                    sel_label = center;
            cluster[sel_label].append(token);

        # re-cal the centriod
        new_centroid = centerTokens(matrix, cluster);
        for center in new_centroid:
            if center not in centroid:
                isChange = True;
                break;
            isChange = False;
        centroid = new_centroid;

    return cluster;

