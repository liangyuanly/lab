#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
#from matplotlib.dates import epoch2num, date2num
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
from boundingBox import *
from getTweets import GetTweets
from tokenization import *
from loadFile import *
from settings import Settings


def calTweetNum(year, month, day_from, day_to):
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
                count = count + 1;
        print count;

calTweetNum(2011, 8, 20, 21);

