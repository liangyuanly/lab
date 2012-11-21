#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import fnmatch
#import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
import ast
from tinysegmenter import *
from operator import itemgetter
import random

def dumpCluster(cluster, outfilename):
    outfile = file(outfilename, 'w');
    #outfile = file('./output/Map/cluster_of_geodis_kernel.txt', 'w');
    for key, tokens in cluster.iteritems():
        #outfile.write(key.encode('utf-8')+'\n');
        for token in tokens:
            #outfile.write(token + '\t')
            outfile.write(token.encode('utf-8')+'\t');
        outfile.write('\n\n');

    outfile.close();


def loadCluster(filename, format='unicode'):
    infile = file(filename);
    lines = infile.readlines();
    infile.close();
    label = 1;

    cluster = {};
    i = 0;
    term_label = {};
    while i < len(lines):   
        cluster[label] = [];
        while(i < len(lines) and lines[i] != '\n'):
            items = lines[i].split('\t');
            for term in items:
                if term == '\n':
                    continue;
                if term[len(term)-1] == '\n':
                    term = term[0:len(term)-1];
                if format == 'utf-8':
                    term = unicode(term, 'utf-8');
                if format == 'unicode':
                    term = unicode(term, errors='replace')
                cluster[label].append(term);
                term_label[term] = label;
            i = i + 1;
        i = i + 1;
        label = label + 1;

    return cluster, term_label;


def loadTokenCluster(filename, format='unicode'):
    infile = file(filename, 'rb');
    lines = infile.readlines();
    list = [];
    count = 0;
    for line in lines:
        count = count + 1;
        terms = line.split('\t');
        for term in terms:
            if term == '\n':
                continue;
            if term[len(term)-1] == '\n':
                term = term[0:len(term)-1]
            if format == 'utf-8':
                term = unicode(term, 'utf-8');
            list.append(term);

    infile.close();
    return list;


def loadToken(filename, format='unicode'):
    infile = file(filename, 'rb');
    lines = infile.readlines();
    list = [];
    count = 0;
    for line in lines:
        count = count + 1;
        terms = line.split('\t');
        term = terms[0];
        if term == '\n':
            continue;
        if term[len(term)-1] == '\n':
            term = term[0:len(term)-1]
        if format == 'utf-8':
            term = unicode(term, 'utf-8');
        list.append(term);

    infile.close();
    return list;

def loadTokenWei(filename):
    infile = file(filename, 'rb');
    lines = infile.readlines();
    list = {};
    count = 0;
    for line in lines:
        count = count + 1;
        terms = line.split('\t');
        term = terms[0];
        if term == '\n':
            continue;
        if term[len(term)-1] == '\n':
            term = term[0:len(term)-1]
        list[term] = 1 - 0.1*(count/10);

    infile.close();
    return list;

#load the tweets from a file
def loadTweetsFromGZ(filename):
    getter = GetTweets();
    tweet_list = [];
    for tweet in getter.iterateTweetsFromGzip(filename):
        [rel, tweet_info] = getter.parseTweet(tweet);
        tweet_list.append(tweet_info);

    return tweet_list;

#load the tweets from a file
def loadTweetsFrombb(filename, bb):
    getter = GetTweets();
    tweet_list = [];
    for tweet in getter.iterateTweetsFromGzip(filename):
        [rel, tweet_info] = getter.parseTweet(tweet);
        if not isTweetInbb(bb):
            continue;
        tweet_list.append(tweet_info);

    return tweet_list;


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

    return set(stop_words);

def loadTopTags(filename):
    infile = file(filename);
    lines = infile.readlines();
    all_tags = [];
    for line in lines:
        data = cjson.decode(line);
        all_tags.append((data[0], int(data[1])));

    sort_tags = sorted(all_tags, key=itemgetter(1), reverse = True);
    sort_tags = sort_tags[0:1000];
    sel_tags = [];
    for tags in sort_tags:
        sel_tags.append(tags[0]);
    print sel_tags;
    return sel_tags;

