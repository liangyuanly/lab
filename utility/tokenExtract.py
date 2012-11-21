#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
#import numpy as np
import operator
import string
import math
simplejson = json
import ast
from tinysegmenter import *
from operator import itemgetter
from common import *
from boundingBox import * 
from getTweets import GetTweets
from tokenization import *
from loadFile import *
from settings import Settings
import tokenization

g_pic_sites = ['twitpic', 'twitrpix', 'plixi', 'yfrog', 'ow.ly']; 

def normalizeFreq(token_dics):
    total_token_num = float(token_dics['TotalTokenNum']);
    for token, fre in token_dics.iteritems():
        if token == 'TotalTokenNum':
            continue;
        token_dics[token] = token_dics[token]/total_token_num;

def normalizeToken(tag_tokens):
    for tag, token_dics in tag_tokens.iteritems():
        total_token_num = float(token_dics['TotalTokenNum']);
        for token, fre in token_dics.iteritems():
            if token == 'TotalTokenNum':
                continue;
            token_dics[token] = token_dics[token]/total_token_num;

def tokensForToken(tweets, token_dics, stopwords, tokens, language='English'):
    related_tweet_num = 0;
    for tweet_info in tweets:
        text = tweet_info['text'];

        is_related = 0;
        for token in tokens:
            if tokenization.similarityCal(token, text) > 0:
                is_related = 1;
                break;

        if is_related == 0:
            continue;

        related_tweet_num = related_tweet_num + 1;

        text_tokens = tokenize(text, language, stopwords);

        for token, freq in text_tokens.iteritems():
            ac_freq = token_dics.get(token);
            if ac_freq == None:
                token_dics[token] = 0;

            token_dics[token] = token_dics[token] + freq;
    
    return related_tweet_num;

def tokensForTag(tweets, tag_tokens, stopwords, select_tags, language='English', tags=None, isAddTag=False):
    for tweet_info in tweets:
        #in this case, which means use all the tweets:
        if tags != [] and tags != None:
            tweet_info['hashtag'] = tags;
        
        #if isAddTag:
        #    addTag(tweet_info, select_tags);
        #print tweet_info["hashtag"];

        tags = tweet_info['hashtag'];
        if tags == None or tags == []:
            continue;
        text = tweet_info['text'];
        #print text.encode('utf-8');
     
        tokens = tokenize(text, language, stopwords);
        #print tokens;

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

def tokenADayTweets(bb, stop_words, year, month, day, language = 'English'):
    path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
    if not os.path.exists(path):
        return {};
    
    #outfile = file('TweetsIn15Minutes.txt', 'wb')
    files = os.listdir(path);
    tag_token = {};
    key = str(year)+'-'+str(month)+'-'+str(day);
    select_tags = [key] # 'image-'+key];
    getter = GetTweets();
    count = 0;
    for afile in files:
        filename = path + afile;
        print filename;
        tweet_list = [];
        for tweet in getter.iterateTweetsFromGzip(filename):
            tweet_info = getter.parseTweet(tweet);
            if not isTweetInbb(bb, tweet_info):
                continue;
            tweet_info['hashtag'] = [key];
            #if tweet_info['url'] != None and tweet_info['url'] != []:
            #    for website in g_pic_sites:
            #        if tweet_info['url'][0].find(website) >= 0:
            #            tweet_info['hashtag'] = [key, 'image-'+key];
            #            break;
            tweet_list.append(tweet_info);
        tokensForTag(tweet_list, tag_token, stop_words, select_tags, language);
    return tag_token;

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

#interface to outside
#filter the tokens by IDF
def tokenFilterByIDF(infile_name, filename_common, outfile_name, token_count = 100, format='multiple'):
    infile = file(filename_common);
    dic_common = {};
    #dic_common_fre = {};
    lines = infile.readlines();
    days_num = len(lines);
    if days_num <= 0:
        print 'the common file is empty'
        return;

    for line in lines:
        dic = cjson.decode(line);
        for key, token_dic in dic.iteritems():
            for token, freq in token_dic.iteritems():
                if dic_common.get(token) == None:
                    dic_common[token] = freq;
                    #dic_common_fre[token] = 1;
                else:
                    dic_common[token] = dic_common[token] + freq;
                    #dic_common_fre[token] = dic_common_fre[token] + 1;
    for token, freq in dic_common.iteritems():
        dic_common[token] = dic_common[token]/float(days_num);

    outfile = file(outfile_name, 'w');
    #filter the tokens in the dictionary
    if format != 'multiple':
        infile = file(infile_name);
        token_dic = json.load(infile);
        infile.close();
        sorted_dic = {};
        for token, freq in token_dic.items():
            if dic_common.get(token) == None:
                continue;
            if freq > dic_common[token]*3:
                continue;
            del token_dic[token];
            
        count = 0;
        for token, freq in sorted(token_dic.iteritems(), key=lambda (k,v):(v,k), reverse = True):
            count = count + 1;
            if count > token_count:
                break;
            outfile.write(token.encode('utf-8') + '\t' + str(freq) + '\n');
            print token.encode('utf-8'), str(freq);
    else:
        #filter the tokens for multiple dictionaries
        infile = file(infile_name);
        lines = infile.readlines();
        infile.close();
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
                outfile.write(key + '\n');
            
                count = 0;
                for token, freq in sorted(token_dic.iteritems(), key=lambda (k,v):(v,k), reverse = True):
                    count = count + 1;
                    if count > token_count:
                        break;
                    outfile.write(token + '\t');
                    print token.encode('utf-8'), str(freq);
       
    outfile.close();

#interface to outside
#extract tokens for a certain period
def tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language):
    filename = Settings.stop_words_file;
    stop_words = loadStopwords(filename);
    tweets = [];
   
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
        if not os.path.exists(path):
            continue;
        files = os.listdir(path);
        getter = GetTweets();
        count = 0;
        for afile in files:
            filename = path + afile;
            print filename;
            tweet_list = [];
            for tweet in getter.iterateTweetsFromGzip(filename):
                tweet_info = getter.parseTweet(tweet);
                if isTweetInbb(bb, tweet_info) == 0:
                    continue;
                tweet_list.append(tweet_info);
            tokensForToken(tweet_list, token_dic, stop_words, query, language);
            #related_tweets_num = related_tweets_num + temp_num; 

    outfile = file(outfilename, 'w');
    normalizeFreq(token_dic);
    json.dump(token_dic, outfile);
    outfile.close();

#interface to outside
#extract tokens for a certain period
def tokenDailyExtract(bb, year, month, day_from, day_to, outfilename, language):
    filename = Settings.stop_words_file;
    stop_words = loadStopwords(filename);
    tweets = [];
   
    outfile = file(outfilename, 'w');
    for day in range(day_from, day_to):
        tag_token = tokenADayTweets(bb, stop_words, year, month, day, language);
        normalizeToken(tag_token);
        json.dump(tag_token, outfile);
        outfile.write('\n');
    outfile.close();

#interface to outside  doing.....
#extract tokens for a certain period
def tokenTagExtract(tweets_filename, tag_filename, outfilename, language):
    filename = Settings.stop_words_file;
    stop_words = loadStopwords(filename);
    tweets = [];
    
    #tweets_filename = './output/JP_earthquake_tweets.txt';
    loadTweets(tweets_filename, tweets, 'json');
    
    #tag_filename = './output/JP_earthquake_tag_freq.txt';
    select_tags = loadTags(tag_filename);
    
    tag_token = {};
    tokensForTag(tweets, tag_token, stop_words, select_tags, language);
    normalizeToken(tag_token);
    outfile = file(outfilename, 'w');
    json.dump(tag_token,outfile);
    outfile.close();

