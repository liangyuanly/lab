#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
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

def filterTweetsByTTL(bb, year, month, day_from, day_to, tokens, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
        path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
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
                
                text = tweet_info['text'];
                is_related = 0;
                for token in tokens:
                    if similarityCal(token, text) > 0:
                        is_related = 1;
                        break;
                if is_related == 0:
                    continue;

                json.dump(tweet_info, out);
                out.write('\n');
        out.close();

def filterTweetsByTL(bb, year, month, day_from, day_to, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
        path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
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
                
                json.dump(tweet_info, out);
                out.write('\n');
        out.close();

def filterTweetsByTT(year, month, day_from, day_to, tokens, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    out = file(outfile, 'w');
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
        path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
        files = os.listdir(path);
        getter = GetTweets();
        count = 0;
        for afile in files:
            filename = path + afile;
            print filename;
            tweet_list = [];
            for tweet in getter.iterateTweetsFromGzip(filename):
                tweet_info = getter.parseTweet(tweet);
                
                text = tweet_info['text'];
                is_related = 0;
                for token in tokens:
                    if similarityCal(token, text) > 0:
                        is_related = 1;
                        break;
                if is_related == 0:
                    continue;

                json.dump(tweet_info, out);
                out.write('\n');
    
        out.close();

#filter the tweets by weighted token and time
def filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
        path = Settings.tweet_folder + str(year) + '/' + str(month) + '/' + str(day) + '/';
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
                    
                text = tweet_info['text'];
                weight = 0;
                for token, wei in tokens.iteritems():
                    if similarityCal(token, text) > 0:
                        weight = weight + wei;
                        break;
                if weight < 1:
                    continue;

                json.dump(tweet_info, out);
                out.write('\n');
    
        out.close();

def fileterTweetsByTag(tt, tags, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    begin = tt[0];
    end = tt[1];
    
    year = begin.date().year;
    month_from = begin.date().month;
    month_to = end.date().month;

    for month in range(month_from, month_to+1):
        for day in range(1, 31):
            time = datetime.datetime(year, month, day, 0, 0, 0);
            if time < begin or time > end:
                continue;

            out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
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
                
                    tweet_tag = tweet_info['hashtag'];
                    weight = 0;
                    for atag in tweet_tag:
                        if not atag in tags:
                            continue;

                    json.dump(tweet_info, out);
                    out.write('\n');
        
            out.close();

#filter the tweets by weighted token and time
def filterTweetsByWeiTT(year, month, day_from, day_to, tokens, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
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
            
                text = tweet_info['text'];
                weight = 0;
                for token, wei in tokens.iteritems():
                    if similarityCal(token, text) > 0:
                        weight = weight + wei;
                        break;
                if weight < 1:
                    continue;

                json.dump(tweet_info, out);
                out.write('\n');
    
        out.close();

def filterTweetsByTTag(bb, year, month, day_from, day_to, tags, out_folder):
    token_dic = {};
    related_tweets_num = 0;
    for day in range(day_from, day_to):
        out = file(out_folder + str(year) + '_' + str(month) + '_' + str(day) + '.txt', 'w');
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
            
                tweet_tags = tweet_info['hashtag'];
                weight = 0;
                for tag in tweet_tags:
                    if tag in tags:
                        json.dump(tweet_info, out);
                        out.write('\n');
                        break;
        out.close();
