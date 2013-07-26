#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
#from scipy import *
import scipy
import random
import sys;
sys.path.append('../../../utility')
from tokenization import similarityCal
from common import *
import time

def filterAccordingTime():
    infile = file('tweet2/2011_3_10.txt');
    lines = infile.readlines();
    infile.close();

    outfile  = file('selected_tweets.txt', 'w');
    date_tweet = {};
    for line in lines:
        data = cjson.decode(line)
        stime = data['time'];
        text = data['text'];
        if  similarityCal('mar 11 05:', stime) > 0 and (similarityCal('\u5730\u9707', text) > 0 or similarityCal('earthquake', text) > 0 ):
            date_time = tweetTimeToDatetime(stime);
            date_time = time.mktime(date_time.timetuple());
            date_tweet[date_time] = data;

    for key, data in sorted(date_tweet.items()):
        json.dump(data, outfile);
        outfile.write('\n')
        outfile.write(data['text'].encode('utf-8'))
        outfile.write('\n')
    outfile.close();

filterAccordingTime();
