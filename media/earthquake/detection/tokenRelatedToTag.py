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
import ast
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.api import *
from tinysegmenter import *
from settings import Settings
from operator import itemgetter
from Utility import *


g_pic_sites = ['twitpic', 'twitrpix', 'plixi', 'yfrog', 'ow.ly']; 

def calSimilarity(sel_tokens, tweets, stop_words):
    for tweet in tweets:
        tokens = tokenize(tweet['text'], 'Japanese', stop_words);
        score = similarity(sel_tokens, tokens);
        #print tweet['text'].encode('utf-8'), score;
        #if score <= 0:
        #    del tweet;
        #    continue;
        tweet['score'] = score;

def selectTopSentence(token_filename, year, month, day, stop_words, isImage):
    #load the selected tokens
    infile = file(token_filename);
    lines = infile.readlines();
    for line in lines:
        line = string.lower(line);
        dic = cjson.decode(line);
        key = str(year) + '-' + str(month) + '-' + str(day);
        if isImage:
            key = 'image-' + key;
        tokens = dic.get(key);
        if tokens != None:
            break;

    if tokens == None:
        return;
    
    for token, freq in sorted(tokens.iteritems(), key=lambda (k,v):(v,k), reverse = True):
        print token.encode('utf-8') + freq;

    path = Settings.tweet_folder;
    sub_path = '/' + str(year) + '/' + str(month) + '/' + str(day) + '/';
    path = path + sub_path;
    files = os.listdir(path);
    getter = GetTweets();
    similar_tweets = [];
    for afile in files:
        filename = path + afile;
        #print filename;
        tweet_list = [];
        for tweet in getter.iterateTweetsFromGzip(filename):
            [rel, tweet_info] = getter.parseTweet(tweet);
            if not isTweetInJapan(tweet_info):
                continue;
    
            if isImage:
                if tweet_info['url'] == None or tweet_info['url'] == []:
                    continue;

            tweet_list.append(tweet_info);

        calSimilarity(tokens, tweet_list, stop_words);
        similar_tweets = similar_tweets + tweet_list;

    #record the tweets with similar scores in a certain day
    if isImage:
        outfile = file('output/TopImage/' + str(year)+'-'+str(month) + '-' + str(day) + '.txt', 'w');
    else:
        outfile = file('output/TopSentence/' + str(year)+'-'+str(month) + '-' + str(day) + '.txt', 'w');
    for tweet in sorted(similar_tweets, key=itemgetter('score'), reverse = True):
        if tweet['score'] > 0:
            json.dump(tweet, outfile, encoding='utf-8');
            outfile.write(tweet['text'].encode('utf-8')+'\n');
    outfile.close();

def selectTopSentenceMain(isImage = False):
    filename = './data/stop_words.txt';
    token_file = './output/JP_earthquake_daily_token_filter.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
    year = 2011;
    month = 3;
    for day in range(11, 14):
        selectTopSentence(token_file, year, month, day, stop_words, isImage);

def loadTweets(filename, tweets, format='json'):
    in_file = file(filename);
    lines = in_file.readlines();
    for line in lines:
        if format == 'json':
            tweet_info = cjson.decode(line);
            #print tweet_info["hashtag"];
        else:
            tweet_info = ast.literal_eval(line);
        tweets.append(tweet_info);

def addTag(tweet, tokens):
    for token in tokens:
        if similarity4(token, tweet['text']) > 0:
            if token not in tweet['hashtag']:
                tweet['hashtag'].append(token);

def tokensForTag(tweets, tag_tokens, stopwords, select_tags, language='English', tags=None, isAddTag=False):
    for tweet_info in tweets:
        if tags != [] and tags != None:
            tweet_info['hashtag'] = tags;
        
        if isAddTag:
            addTag(tweet_info, select_tags);
        #print tweet_info["hashtag"];

        tags = tweet_info['hashtag'];
        if tags == None or tags == []:
            continue;
        text = tweet_info['text'];
        #print text.encode('utf-8');
     
        tokens = tokenize(text, language, stopwords);
        print tokens;

        for tag in tags:
            tag = string.lower(tag);

            if tag not in select_tags:
                continue;

            token_dics = tag_tokens.get(tag);
            if token_dics == None:
                token_dics = {};
                tag_tokens[tag] = token_dics;
                token_dics['TotalTokenNum'] = 0;

            for token, freq in tokens.iteritems():
                ac_freq = token_dics.get(token);
                if ac_freq == None:
                    token_dics[token] = 0;

                token_dics[token] = token_dics[token] + freq;
                #token_dics['TagTokenNum'] = token_dics['TagTokenNum'] + 1;

def normalizeToken(tag_tokens):
    for tag, token_dics in tag_tokens.iteritems():
        total_token_num = float(token_dics['TotalTokenNum']);
        for token, fre in token_dics.iteritems():
            if token == 'TotalTokenNum':
                continue;
            token_dics[token] = token_dics[token]/total_token_num;

def loadTags(filename):
    in_file = file(filename);
    lines = in_file.readlines();
    select_tags = [];
    for line in lines:
        items = line.split('\t');
        if int(items[1]) > 5:
            tag = string.lower(items[0]);
            select_tags.append(tag);

    return select_tags;

def writeTagsToken(tag_tokens):
    outfile = file('./output/tag_token.txt', 'w');
    for tag, tweet_info_list in tag_tokens.iteritems():
        outfile.write(str(tag)+'\n');
        for token, freq in sorted(tweet_info_list.iteritems(), key=lambda (k,v):(v,k), reverse = True):
            outfile.write(token.encode('utf-8') +':' + str(freq) + '\t');
        outfile.write('\n' + '\n');

    outfile.close();

def tokenADayTweetsUS(stop_words, year, month, day):
    path='/mnt/chevron/bde/Data/TweetData/GeoTweets/' + str(year) + '/' + str(month) + '/' + str(day) + '/';
    files = os.listdir(path);
    tag_token = {};
    key = str(year)+'-'+str(month)+'-'+str(day);
    select_tags = [key, 'image-'+key];
    getter = GetTweets();
    count = 0;
    for afile in files:
        filename = path + afile;
        print filename;
        tweet_list = [];
        for tweet in getter.iterateTweetsFromGzip(filename):
            [rel, tweet_info] = getter.parseTweet(tweet);
            if not isTweetInUS(tweet_info):
                continue;
            tweet_info['hashtag'] = [key];
            if tweet_info['url'] != None and tweet_info['url'] != []:
                for website in g_pic_sites:
                    if tweet_info['url'][0].find(website) >= 0:
                        tweet_info['hashtag'] = [key, 'image-'+key];
                        break;
            tweet_list.append(tweet_info);
        tokensForTag(tweet_list, tag_token, stop_words, select_tags, 'english');
    return tag_token;

def tokenADayTweets(stop_words, year, month, day):
    path='/mnt/chevron/bde/Data/TweetData/GeoTweets/' + str(year) + '/' + str(month) + '/' + str(day) + '/';
    #outfile = file('TweetsIn15Minutes.txt', 'wb')
    files = os.listdir(path);
    tag_token = {};
    key = str(year)+'-'+str(month)+'-'+str(day);
    select_tags = [key, 'image-'+key];
    getter = GetTweets();
    count = 0;
    for afile in files:
        filename = path + afile;
        print filename;
        tweet_list = [];
        for tweet in getter.iterateTweetsFromGzip(filename):
            [rel, tweet_info] = getter.parseTweet(tweet);
            if not isTweetInJapan(tweet_info):
                continue;
            tweet_info['hashtag'] = [key];
            if tweet_info['url'] != None and tweet_info['url'] != []:
                for website in g_pic_sites:
                    if tweet_info['url'][0].find(website) >= 0:
                        tweet_info['hashtag'] = [key, 'image-'+key];
                        break;
            tweet_list.append(tweet_info);
        tokensForTag(tweet_list, tag_token, stop_words, select_tags, 'Japanese');
    return tag_token;

#for the hurricane
def tokenDaysUSMain():
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
   
    year = 2011;
    month = 8;
    
    outfile = file('output/US_hurricane_daily_token_10_17.txt', 'w');
    for day in range(10, 17):
        tag_token = tokenADayTweetsUS(stop_words, year, month, day);
        normalizeToken(tag_token);
        json.dump(tag_token, outfile);
        outfile.write('\n');
    outfile.close();
 
def tokenDaysMain():
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
   
    year = 2011;
    month = 3;
    
    outfile = file('output/JP_earthquake_daily_token.txt', 'w');
    for day in range(10, 21):
        tag_token = tokenADayTweets(stop_words, year, month, day);
        normalizeToken(tag_token);
        json.dump(tag_token, outfile, encoding="utf-8");
        outfile.write('\n');
    outfile.close();
 

def tokenForNoTagMain():
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
    
    tweets_filename = './output/JP_earthquake_tweets.txt';
    #tweets_filename = './output/US_election_tweets.txt';
    #tweets_filename = './output/UK_wedding_tweets.txt';
    #tweets_filename = './output/US_kony_tweets.txt';
    loadTweets(tweets_filename, tweets, 'json');
    
    select_tags = ['image'];
    
    tag_token = {};
    tokensForTag(tweets, tag_token, stop_words, select_tags, 'Japanese', ['image']);
    normalizeToken(tag_token);
    outfile = file('output/JP_earthquake_image_tag_token.txt', 'w');
    json.dump(tag_token,outfile, encoding="utf-8");
    #writeTagsToken(tag_token);

def tokenForTagUSMain():
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
   
    select_tag = [];
    tag_filename = file('./data/select_tag.txt');
    lines = tag_filename.readlines();
    for line in lines:
        if line[len(line)-1] == '\n':
            select_tag.append(line[0:len(line)-1]);
        else:
            select_tag.append(line);

    year = 2011;
    month = 8;
    day_from = 20;
    day_to = 30;

    tag_token = {};
    for day in range(day_from, day_to):
        tweets_filename = '/mnt/chevron/yuan/tweet/' + str(year) + '_' + str(month) + '_' + str(day) + '.txt';
        loadTweets(tweets_filename, tweets);
        tokensForTag(tweets, tag_token, stop_words, select_tag, 'English', None, True);
    
    normalizeToken(tag_token);
    outfile = file('output/US_Irene_tag_token.txt', 'w');
    json.dump(tag_token,outfile);
    #writeTagsToken(tag_token);

def tokenForTagMain():
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);
    tweets = [];
    
    tweets_filename = './output/JP_earthquake_tweets.txt';
    #tweets_filename = './output/US_election_tweets.txt';
    #tweets_filename = './output/UK_wedding_tweets.txt';
    #tweets_filename = './output/US_kony_tweets.txt';
    loadTweets(tweets_filename, tweets, 'json');
    
    tag_filename = './output/JP_earthquake_tag_freq.txt';
    #tag_filename = './output/UK_wedding_tag_freq.txt';
    #tag_filename = './output/US_kony_tag_freq.txt';
    select_tags = loadTags(tag_filename);
    
    tag_token = {};
    tokensForTag(tweets, tag_token, stop_words, select_tags, 'Japanese');
    normalizeToken(tag_token);
    outfile = file('output/JP_earthquake_tag_token.txt', 'w');
    json.dump(tag_token,outfile, encoding="utf-8");
    #writeTagsToken(tag_token);

def tokenFilterByIDF(filename, filename_common):
    infile = file(filename_common);
    dic_common = {};
    dic_common_fre = {};
    lines = infile.readlines();
    for line in lines:
        dic = cjson.decode(line);
        for key, token_dic in dic.iteritems():
            for token, freq in token_dic.iteritems():
                if dic_common.get(token) == None:
                    dic_common[token] = freq;
                    dic_common_fre[token] = 1;
                else:
                    dic_common[token] = dic_common[token] + freq;
                    dic_common_fre[token] = dic_common_fre[token] + 1;
    for token, freq in dic_common.iteritems():
        dic_common[token] = dic_common[token]/float(dic_common_fre[token]);

    outfile = file('./data/US_hurricane_tag_token_filter.txt', 'w');
    infile = file(filename);
    lines = infile.readlines();
    top100_token_file = file('./output/top100_tokens.txt', 'w');
    for line in lines:
        dic = cjson.decode(line);
        for key, token_dic in dic.items():
            sorted_dic = {};
            for token, freq in token_dic.items():
                if dic_common.get(token) == None:
                    continue;
                if freq > dic_common[token]*3:
                    continue;
                del token_dic[token];
            
            print '\n'+key+'\n';
            top100_token_file.write(key + '\n');
        
        #for tag in tag_list:
        #    if string.find(tweet_info['text'].encode('utf-8'), tag) > 0:
        #        value = tag_dic.get(tag);
        #        if value == None:
        #            value = [1, time];
        #            tag_dic[tag] = value;
        #        else:
        #            value[0] = value[0] + 1;
        #            value.append(time);
      
            count = 0;
            dic_tmp = {};
            for token, freq in sorted(token_dic.iteritems(), key=lambda (k,v):(v,k), reverse = True):
                count = count + 1;
                dic_tmp[token] = freq;
                if count > 100:
                    break;
                top100_token_file.write(token + '\t');
                print token.encode('utf-8'), str(freq);
       
            top100_token_file.write('\n');
            sorted_dic[key] = dic_tmp;
            json.dump(sorted_dic, outfile, encoding = 'utf-8');
            outfile.write('\n');
    
    top100_token_file.close();
    outfile.close();

#tokenForTagMain();
#tokenForNoTagMain();
#tokenDaysMain();
#tokenDaysUSMain();
tokenFilterByIDF('./output/US_Irene_tag_token.txt', './output/US_hurricane_daily_token_10_17.txt');
#selectTopSentenceMain(False);
#tokenForTagUSMain()
