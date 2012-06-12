
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
simplejson = json
import ast
import random
import sys
sys.path.append('../utility/')
from tokenExtract import *
from loadFile import *
from boundingBox import *
from getTweets import GetTweets;
from tweetFilter import *

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


def ireneEventExtract():
    filename = './data/irene/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2011;
    month = 8;
    day_from = 20;
    day_to = 30;
    language = 'English';
    outfilename = './data/irene/select_tokens.txt';
    #tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    day_from = 10;
    day_to = 15;
    outfilename_com = './data/irene/common_tokens.txt'
    #tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/irene/top10_tokens.txt'
    #tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');

    day_from = 20;
    day_to = 30;
    #use the selected tokens, bb, time to filter the tweets
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/irene/weiTT/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
  
    filterTweetsByWeiTT(year, month, day_from, day_to, tokens, out_fold);
    return 0;

def jpeqUSEventExtract():
    filename = './data/jpeq_us/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2011;
    month = 3;
    day_from = 11;
    day_to = 20;
    language = 'English';
    outfilename = './data/jpeq_us/select_tokens.txt';
    #tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    day_from = 1;
    day_to = 5;
    outfilename_com = './data/jpeq_us/common_tokens.txt'
    #tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/jpeq_us/top10_tokens.txt'
    #tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');
 
    day_from = 11;
    day_to = 16;
    #use the selected tokens, bb, time to filter the tweets
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/jpeq_us/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
  
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
 
def konyEventExtract():
    filename = './data/kony/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2012;
    month = 3;
    day_from = 10;
    day_to = 18;
    language = 'English';
    outfilename = './data/kony/select_tokens.txt';
    tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    day_from = 1;
    day_to = 3;
    outfilename_com = './data/kony/common_tokens.txt'
    tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/kony/top100_tokens.txt'
    tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');
 
    day_from = 6;
    day_to = 30;
    #use the selected tokens, bb, time to filter the tweets
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/kony/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
  
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
 
def NBAEventExtract():
    return 0;

def superBowlEventExtract():
    return 0;

def jobsEventExtract():
    filename = './data/jobs/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2011;
    month = 10;
    day_from = 5;
    day_to = 7;
    language = 'English';
    outfilename = './data/jobs/select_tokens.txt';
    #tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    day_from = 1;
    day_to = 4;
    outfilename_com = './data/jobs/common_tokens.txt'
    #tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/jobs/top10_tokens.txt'
    #tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');
 
    day_from = 5;
    day_to = 10;
    #use the selected tokens, bb, time to filter the tweets
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/jobs/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
 
def NZEQEventExtract():
    return 0;

def royalWedEventExtract():
    filename = './data/royal/query.txt';
    query = loadTerms(filename);
    bb = getUKbb();
    year = 2011;
    month = 4;
    day_from = 29;
    day_to = 31;
    language = 'English';
    outfilename = './data/royal/select_tokens.txt';
    #tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    day_from = 1;
    day_to = 2;
    outfilename_com = './data/royal/common_tokens.txt'
    #tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/royal/top10_tokens.txt'
    #tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');

    #use the selected tokens, bb, time to filter the tweets
    day_from = 29;
    day_to = 31;
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/royal/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
 
    month = 5;
    day_from = 1;
    day_to = 4;
    filterTweetsByTTL(bb, year, month, day_from, day_to, tokens, out_fold);

def linsanityEventExtract():
    filename = './data/NBA/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2012;
    month = 2;
    day_from = 10;
    day_to = 20;
    language = 'English';
    outfilename = './data/NBA/select_tokens.txt';
    #tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    month = 1;
    day_from = 25;
    day_to = 28;
    outfilename_com = './data/NBA/common_tokens.txt'
    #tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/NBA/top10_tokens.txt'
    #tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');

    #use the selected tokens, bb, time to filter the tweets
    month = 2;
    day_from = 4;
    day_to = 29;
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/NBA/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);

def electionEventExtract():
    filename = './data/election/query.txt';
    query = loadTerms(filename);
    bb = getUSbb();
    year = 2012;
    month = 4;
    day_from = 20;
    day_to = 30;
    language = 'English';
    outfilename = './data/election/select_tokens.txt';
    tokenOfAQueryExtract(bb, year, month, day_from, day_to, query, outfilename, language);
    
    #extract the common tokens to filter the ones 
    month = 1;
    day_from = 25;
    day_to = 28;
    outfilename_com = './data/election/common_tokens.txt'
    tokenDailyExtract(bb, year, month, day_from, day_to, outfilename_com, language);
    
    #filter the selected tokens by the common tokens
    outfilename_100 = './data/election/top100_tokens.txt'
    tokenFilterByIDF(outfilename, outfilename_com, outfilename_100, 100, format='single');

    #use the selected tokens, bb, time to filter the tweets
    month = 4;
    day_from = 1;
    day_to = 31;
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/election/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
    #use the selected tokens, bb, time to filter the tweets
    month = 5;
    day_from = 1;
    day_to = 11;
    tokens = loadTokenWei(outfilename_100);
    out_fold = './data/election/weiTTL/';
    if not os.path.exists(out_fold):
        os.makedirs(out_fold);
    filterTweetsByWeiTTL(bb, year, month, day_from, day_to, tokens, out_fold);
 
ireneEventExtract();
#jpeqUSEventExtract();
#konyEventExtract();
#royalWedEventExtract();
#jobsEventExtract();
#linsanityEventExtract();
#electionEventExtract();
