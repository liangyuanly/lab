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


