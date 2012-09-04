#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
import ast
import nltk
from tinysegmenter import *
from settings import Settings
from operator import itemgetter
from Utility import *
import random
from utility.dijkstra import *
from utility.MST import *
import sys
sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *

def loadGeoForTerms(list, tweets, term_locs, outputfile=None):
    for tweet in tweets:
        geo_term = 'corrdinate';
        if not geo_term in tweet.keys():
            geo_term = 'geo';

        if tweet[geo_term] == None or tweet[geo_term] == []:
            continue;

        text = tweet['text'];
        flag = 0;
        for term in list:
            if similarity4(term, text) >= 1:
                locs = term_locs.get(term);
                if locs == None:
                    locs = [];
                    term_locs[term] = locs;

                flag = 1;
                locs.append(tweet[geo_term]);
            
        if flag == 1:
            if outputfile != None:
                json.dump(tweet, outputfile);
                outputfile.write('\n')
                
#def loadGeoForImage(image_tweets)
def writeTermGeos(term_locs, outfilename):
    outfile = file(outfilename, 'w');
    for term, locs in term_locs.iteritems():
        outfile.write(term + '\n');
        for loc in locs:
            outfile.write(str(loc) + '\t');
        outfile.write('\n');

    outfile.close();

def termTimeLocBin(term_list, tweets, time_loc_bin, base_time, end_time, bbs):
    for conti, box in bbs.iteritems():
        if conti not in time_loc_bin.keys():
            time_loc_bin[conti] = {};

    for tweet in tweets:
        time = tweet['time'];
        text = tweet['text'];
        flag = 0;
            
        if time == None or time == []:
            continue;
        flag = 0;
        for conti, box in bbs.iteritems():
            if isTweetInbb(box, tweet):
                time_bin = time_loc_bin[conti]
                print conti, time
                flag = 1
                break;
        if flag == 0:
            print 'not hit!'
            continue;

        date_time = tweetTimeToDatetime(time);
        if date_time < base_time or date_time > end_time:
            continue

        for term in term_list:
            if similarity4(term, text) >= 1:
                bins = time_bin.get(term);
                if bins == None:
                    bins = {};
                    time_bin[term] = bins;
                
                unit = date_time - base_time;
                day_time = unit.days * 24;
                unit = unit.seconds / 3600 + day_time;

                bin = bins.get(unit);
                if bin == None:
                    bin = 0;
                    bins[unit] = bin;

                bins[unit] = bins[unit] + 1;

def termTimeBin(term_list, tweets, time_bin, base_time, end_time):
    for tweet in tweets:
        time = tweet['time'];
        text = tweet['text'];
        flag = 0;
        
        if time == None or time == []:
            continue;
        
        date_time = tweetTimeToDatetime(time);
        if date_time < base_time or date_time > end_time:
            continue

        for term in term_list:
            if similarity4(term, text) >= 1:
                bins = time_bin.get(term);
                if bins == None:
                    bins = {};
                    time_bin[term] = bins;
                
                unit = date_time - base_time;
                day_time = unit.days * 24;
                unit = unit.seconds / 3600 + day_time;

                bin = bins.get(unit);
                if bin == None:
                    bin = 0;
                    bins[unit] = bin;

                bins[unit] = bins[unit] + 1;

#def writeTimeBin(time_bin, outfilename):
#    outfile = file(outfilename);
#    for term, bins in time_bin.iteritems():
#        outfile.write(term + '/n');
#        for unit, freq in bins.iteritems():
#            outfile.write(str(freq) + '\t');
#        outfile.write('\n');
#    outfile.close();

def userGraph(term_list, tweets, term_users):
    for tweet in tweets:
        text = tweet['text'];
        for term in term_list:
            if similarity4(term, text) > 0:
                user = tweet['user'];
                user_list = term_users.get(term);
                if user_list == None:
                    user_list = {};    
                    term_users[term] = user_list;
                count = user_list.get(user);
                if count == None:
                    user_list[user] = 1;
                else:
                    user_list[user] = user_list[user] + 1;

def userFeature(term_list, tweet_fold):
    #term_file = './data/cluster_truth.txt';
    #term_list = loadTerms(term_file);

    #year = 2011;
    #month = 8;
    #day_from = 20;
    #day_to = 30;
    #month = 3;
    #day_from = 11;
    #day_to = 20;

    term_users = {};
    files = os.listdir(tweet_fold);
    #for day in range(day_from, day_to):
    #    path = '/mnt/chevron/yuan/tweet/2011_' + str(month) + '_' + str(day) + '.txt';
    for afile in files:
        path = tweet_fold + afile;
        tweets = loadSimpleTweetsFromFile(path);   
    
        print path;
        userGraph(term_list, tweets, term_users);

    return term_users;
    #outfile = file('.txt', 'w');
    #json.dump(term_users, outfile);
    #outfile.close();

def termTimeBinMain():
    term_file = './data/US_cluster_truth.txt';
    term_list = loadTerms(term_file);

    month = 8;
    day_from = 20;
    day_to = 30;

    term_locs = {};
    time_bin = {};
    base_time = datetime.datetime(2011, 8, 20, 0, 0, 0);
    for day in range(day_from, day_to):
        path = '/mnt/chevron/yuan/tweet/2011_8_' + str(day) + '.txt';
        tweets = loadSimpleTweetsFromFile(path);   
    
        print day;
        termTimeBin(term_list, tweets, time_bin, base_time);

    outfile = file('./output/Map/time_unit_2011_8.txt', 'w');
    json.dump(time_bin, outfile);
    outfile.close();
        
def mapPhotoMain():
    subpath = ['congest', 'crack', 'fire', 'food', 'crowds', 'refuge'];
    image_path = '/mnt/chevron/yuan/pic/03-11-cluster/'
    image_locs = {};
    for sub in subpath:
        path = image_path + sub + '/';
        image_locs[sub] = [];
        image_file = path + 'ImageInfo.txt';
        tweets = loadPhotoInfo(image_file);
        for tweet in tweets:
            image_locs[sub].append(tweet['corrdinate']);
    
    outfile = file('./output/Map/image_locs.txt', 'w');
    json.dump(image_locs, outfile);
    outfile.close();

def mapPhotoMain2():
    date = '2011_3_11';
    image_path = Settings.japan_pic_tweets_w + date;

    tweets = loadTweetsFromFile(image_path);

    image_locs = {};
    image_locs[date] = [];
    for tweet in tweets:    
        image_locs[date].append(tweet['corrdinate']);
    
    outfile = file('./output/Map/image_locs_' + date + '.txt', 'w');
    json.dump(image_locs, outfile);
    outfile.close();

def loadTagTokens(filename, date, top_count):
    infile = file(filename);
    lines = infile.readlines();
    tokens = [];
    for line in lines:
        dic = cjson.decode(line);
        for key, token_dic in dic.items():
            if key != date:
                continue;

            count = 0;
            for token, freq in sorted(token_dic.iteritems(), key=lambda (k,v):(v,k), reverse = True):
                count = count + 1;
                tokens.append(token);
                if count > top_count:
                    break;
                print token.encode('utf-8'); #str(freq);
    return tokens;

def mapTermsUSMain():
    #term_file = './data/US_hurricane_daily_token_filter.txt';
    #term_list = loadTagTokens(term_file, '2011-8-24', 100);
    term_file = './data/US_cluster_truth.txt';
    term_list = loadTerms(term_file);
    
    month = 8;
    day_from = 20;
    day_to = 30;

    term_locs = {};
    #from the file
    for day in range(day_from, day_to):
        tweet_file = '/mnt/chevron/yuan/tweet/2011_' + str(month) + '_' + str(day) + '.txt';
        tweet_list = loadSimpleTweetsFromFile(tweet_file);
        loadGeoForTerms(term_list, tweet_list, term_locs);

    #from gz file
    #for day in range(day_from, day_to):
    #    path = Settings.tweet_folder + '/2011/' + str(month) + '/' + str(day) + '/';
    #    files = os.listdir(path);
    
    #    out_tweet_file = file('/mnt/chevron/yuan/tweet/2011_' + str(month) + '_' + str(day) + '.txt', 'w');

    #    for afile in files:
    #        tweet_list = loadTweetsFromGZ(path + afile, 'US');
    #        loadGeoForTerms(term_list, tweet_list, term_locs, out_tweet_file);

    #    out_tweet_file.close();

    writeTermGeos(term_locs, './output/Map/term_location_2011_' + str(month) + '_' + str(day_from) + '-' + str(day_to) + '.txt');
     

#map the terms to the geo-map
def mapTermsMain():
    term_file = './data/cluster.txt';
    term_list = loadTerms(term_file);

    month = 3;
    day_from = 16;
    day_to = 30;

    term_locs = {};
    for day in range(day_from, day_to):
        path = Settings.tweet_folder + '/2011/3/' + str(day) + '/';
        files = os.listdir(path);
    
        out_tweet_file = file('/mnt/chevron/yuan/tweet/2011_3_' + str(day) + '.txt', 'w');

        for afile in files:
            tweet_list = loadTweetsFromGZ(path + afile, 'JP');
            loadGeoForTerms(term_list, tweet_list, term_locs, out_tweet_file);

        out_tweet_file.close();

    writeTermGeos(term_locs, './output/Map/term_location_2011_3.txt');

def calRelevance(sel_tokens, rel_matrix, tweets):
    #count = 0;
    for tweet in tweets:
        #count = count + 1;
        #if count > 100:
        #    break;
        text = string.lower(tweet['text']);
        for token in sel_tokens:
            if text.find(token) < 0:
                continue;

            for token2 in sel_tokens:
                if token == token2:
                    continue;

                if text.find(token2) < 0:
                    continue;

                rel_matrix[token][token2] = rel_matrix[token][token2] + 1;
                rel_matrix[token2][token] = rel_matrix[token2][token] + 1;

def reverse(dis_matrix):
    for key in dis_matrix.keys():
        max_freq = 0;
        for key2 in dis_matrix[key]:
            if dis_matrix[key][key2] > max_freq:
                max_freq = dis_matrix[key][key2];

        for key2 in dis_matrix[key].keys():
            if dis_matrix[key][key2] != 0:
                dis_matrix[key][key2] = max_freq/float(dis_matrix[key][key2]);

#extract the coocurence 
def relevanceOfToken(tokens, tweet_fold):
    matrix = {};
    for token in tokens:
        if token == 'totaltokennum':
            continue;
        matrix[token] = {};
        for token2 in tokens:
            if token2 == 'totaltokennum':
                continue;
            matrix[token][token2] = 0; 

    files = os.listdir(tweet_fold);
    for fname in files:
        tweet_list = loadSimpleTweetsFromFile(tweet_fold + fname);
        calRelevance(tokens, matrix, tweet_list);

    reverse(matrix);
    
    for term1 in matrix.keys():
        for term2 in matrix[term1].keys():
            if term1 == term2:
                continue;

            if matrix[term1][term2] == 0:
                matrix[term1][term2] = 1000; # give it a big number

    return matrix;

#make the mutiple dimension into one
def assemTimeLocBin(time_loc_bin):
    assem_time_bin = {};
    begin_idx = 0;
    for conti, time_bin in time_loc_bin.iteritems():
        for term, bin in time_bin.iteritems():
            if term not in assem_time_bin.keys():
                assem_time_bin[term] = {};

            for time, fre in bin.iteritems():
                assem_time_bin[term][begin_idx + time] = fre;

        begin_idx += 1000

    return assem_time_bin

#every hour is a bin
def timeLocationFeature(term_list, tt, bbs, tweet_fold):
    time_loc_bin = {};
    begin = tt[0];
    end = tt[1];
    
    files = os.listdir(tweet_fold);
    for fname in files:
        path = tweet_fold + '/' + fname;
        tweets = loadSimpleTweetsFromFile(path);   
    
        termTimeLocBin(term_list, tweets, time_loc_bin, begin, end, bbs);

    time_bin = assemTimeLocBin(time_loc_bin)
    return time_bin;

#every hour is a bin
def timeFeature(term_list, tt, tweet_fold):
    term_locs = {};
    time_bin = {};
    begin = tt[0];
    end = tt[1];
    
    files = os.listdir(tweet_fold);
    for fname in files:
        path = tweet_fold + '/' + fname;
        tweets = loadSimpleTweetsFromFile(path);   
    
        termTimeBin(term_list, tweets, time_bin, begin, end);

    return time_bin;

def locationFeature(term_list, tweet_fold):
    term_locs = {};
    #from the file
    files = os.listdir(tweet_fold);
    for filename in files:
        tweet_file = tweet_fold + filename;
        tweet_list = loadSimpleTweetsFromFile(tweet_file);
        loadGeoForTerms(term_list, tweet_list, term_locs);
    
    return term_locs;

def getAllbbs():
    bb = {};
    bb['Asia'] = getAsiabb();
    bb['Euro'] = getEuropebb();
    bb['SouA'] = getSouthAmericabb();
    bb['NorA'] = getNorthAmericabb();
    bb['Austra'] = getAustraliabb();
    bb['Africa'] = getAfricabb();
    return bb;

#extract the (t,l) features, the modified version of Func2
def extractFeatureFunc3(tokens, tt, bbs, tweet_fold, fold):
    #extract the time bin feature
    time_bin = timeLocationFeature(tokens, tt, bbs, tweet_fold);
    
    outfilename = fold + 'term_time_location.txt';
    outfile = file(outfilename, 'w');
    json.dump(time_bin, outfile);
    outfile.close();

#extract the (t,l) features
def extractFeatureFunc2(event):
    fold = './data/event/' + event + '/';
    tweet_fold = fold + 'tweet/';
    truthfile = fold + 'truth_cluster.txt';
    bb, tt = getbbtt(event); 
    bbs = getAllbbs();
    tt = transTime(tt);
    tokens = loadTerms(truthfile);

    #extract the time bin feature
    time_bin = timeLocationFeature(tokens, tt, bbs, tweet_fold);
    
    outfilename = fold + 'term_time_location.txt';
    outfile = file(outfilename, 'w');
    json.dump(time_bin, outfile);
    outfile.close();

#extract the time, location, user features, etc
def extractFeatureFunc1(event):
    fold = './data/event/' + event + '/';
    tweet_fold = fold + 'tweet/';
    truthfile = fold + 'truth_cluster.txt';
    bb, tt = getbbtt(event); 
    tt = transTime(tt);
    tokens = loadTerms(truthfile);
    
    #extract the co-ocureence feature
    outfilename = fold + 'term_coocurence.txt';
    matrix = relevanceOfToken(tokens, tweet_fold);
    
    outfile = file(outfilename, 'w');
    json.dump(matrix, outfile);
    outfile.close();

    #extract the time bin feature
    time_bin = timeFeature(tokens, tt, tweet_fold);
    
    outfilename = fold + 'term_time.txt';
    outfile = file(outfilename, 'w');
    json.dump(time_bin, outfile);
    outfile.close();

    #extract the geo feature
    term_locs = locationFeature(tokens, tweet_fold);
    outfilename = fold + 'term_location.txt';
    outfile = file(outfilename, 'w');
    json.dump(term_locs, outfile);
    outfile.close();
    #writeTermGeos(term_locs, outfilename);

    #extract the user intersetion
    term_user = userFeature(tokens, tweet_fold);
    outfilename = fold + 'term_user.txt';
    outfile = file(outfilename, 'w');
    json.dump(term_user, outfile);
    outfile.close();

def extractFeatureFunc(tokens, bb, tt, tweet_fold, fold):
    #extract the co-ocureence feature
    outfilename = fold + 'term_coocurence.txt';
    matrix = relevanceOfToken(tokens, tweet_fold);
    
    outfile = file(outfilename, 'w');
    json.dump(matrix, outfile);
    outfile.close();

    #extract the time bin feature
    time_bin = timeFeature(tokens, tt, tweet_fold);
    
    outfilename = fold + 'term_time.txt';
    outfile = file(outfilename, 'w');
    json.dump(time_bin, outfile);
    outfile.close();

    #extract the geo feature
    term_locs = locationFeature(tokens, tweet_fold);
    outfilename = fold + 'term_location.txt';
    outfile = file(outfilename, 'w');
    json.dump(term_locs, outfile);
    outfile.close();
    #writeTermGeos(term_locs, outfilename);

    #extract the user intersetion
    term_user = userFeature(tokens, tweet_fold);
    outfilename = fold + 'term_user.txt';
    outfile = file(outfilename, 'w');
    json.dump(term_user, outfile);
    outfile.close();

def extractTLFeatureMain():
    #event = 'jpeq_jp';
    event = 'irene_overall'
    #event = '3_2011_events'
    #event = '8_2011_events'
    extractFeatureFunc2(event);
    return
    
    #extract multiple events
    tweet_fold = '/home/yuan/lab/duration/data/8_2011_tweets/';
    bbs = getAllbbs();
    tt = getAugust();
    #tt = getMarch();
    tt = transTime(tt);
    out_fold = './data/event/8_2011_events/'
    #events = ['earthquake_JP', 'arab_spring', 'earthquake_NZ', 'gov_shutdown', 'background'];
    events = ['irene', 'jobs_resign', 'earthquake_US', 'arab_spring_late', 'background']
    all_tokens = [];
    for event in events:
        filename_15 = '/home/yuan/lab/duration/data/' + event + '/top15.txt';
        tokens = loadToken(filename_15);
        all_tokens = all_tokens + tokens;

    extractFeatureFunc3(all_tokens, tt, bbs, tweet_fold, out_fold);

def extractFeatureMain():
    event = 'jpeq_jp';
    extractFeatureFunc1(event);
    return;

    event = 'irene_overall';
    extractFeatureFunc1(event);
    return;

#    event = 'NBA';
#    extractFeatureFunc1(event);
    
    tweet_fold = '/home/yuan/lab/duration/data/3_2011_tweets/';
    bb = getWorldbb();
    tt = getMarch();
    tt = transTime(tt);
    out_fold = './data/event/3_2011_events/'
    events = ['earthquake_JP', 'arab_spring', 'earthquake_NZ', 'gov_shutdown', 'background'];
    #events = ['irene', 'jobs_resign', 'earthquake_US', 'arab_spring_late', 'background']
    all_tokens = [];
    for event in events:
        filename_15 = '/home/yuan/lab/duration/data/' + event + '/top15.txt';
        tokens = loadToken(filename_15);
        all_tokens = all_tokens + tokens;

    extractFeatureFunc(all_tokens, bb, tt, tweet_fold, out_fold);

#mapTermsMain();
#mapPhotoMain2();
#termTimeBinMain();
#mapTermsUSMain();
#termUserMain();

#extract the time, co-occur, spatial, user features
#extractFeatureMain();

#extract the time-location features
extractTLFeatureMain();
