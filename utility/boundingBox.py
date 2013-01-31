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

def transTime(str_bb):
    time = str_bb[0];
    year = time[0];
    month = time[1];
    day_from = time[2];
    day_to = time[3];
    begin = datetime.datetime(year, month, day_from, 0, 0, 0);
    end = datetime.datetime(year, month, day_to-1, 23, 59, 59);

    if len(str_bb) > 1:
        time = str_bb[len(str_bb)-1];
        year = time[0];
        month = time[1];
        day_from = time[2];
        day_to = time[3];
        end = datetime.datetime(year, month, day_to-1, 23, 59, 59);

    return [begin, end];

def getIndexForTime(date_time, base_time):
    #date_time = tweetTimeToDatetime(time);
    if date_time < base_time:
        return -1

    unit = date_time - base_time;
    day_time = unit.days * 24;
    unit = unit.seconds / 3600 + day_time;
    return unit;

def getIndexForbb(lati, longi, bb, lat_num, lon_num):
    # Japan
    lati_up = bb[1];
    lati_down = bb[0];
    longi_left = bb[2];
    longi_right = bb[3]; 
    #step = 100;
    lati_step = (lati_up - lati_down)/lat_num;
    longi_step = (longi_right - longi_left)/lon_num;
          
    lati_index = -1;
    longi_index = -1;
    if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
        lati_index = math.floor((lati - lati_down)/lati_step);
        longi_index = math.floor((longi - longi_left)/longi_step);
    
    return int(lati_index), int(longi_index);

def getbbtt(event):
    if event == 'NBA':
        return [getUSbb(), getNBAPeriod()];
    if event == 'jpeq_us':
        return [getUSbb(), getJPEQPeriod()];
    if event == 'jpeq_jp':
        return [getWorldbb(), getMarch()]; 
        #return [getJPbb(), getJPEQPeriod()];
    if event == 'jobs':
        return [getUSbb(), getJobsPeriod()];
    if event == 'irene_overall':
        return [getUSbb(), getIrenePeriod()];
    if event == 'irene':
        return [getUSbb(), getIrenePeriod()];
    if event == 'royal':
        return [getUKbb(), getRoyalPeriod()];
    if event == 'election':
        return [getUSbb(), getElectionPeriod()];
    if event == '3_2011_events':
        return [getWorldbb(), getMarch()];
    if event == '8_2011_events':
        return [getWorldbb(), getAugust()];
    if event == '3_2011_tags':
        return [getWorldbb(), getMarch()];
    return [[], []];

def getEuropebb():
    return [35.7, 72.5, -13.4, 35.5]

def getAfricabb():
    return [-33.2, 35.5, -17.2, 45.7]

def getAsiabb():
    return [-7.4, 74.0, 51.3, 153.3]

def getNorthAmericabb():
    return [12.81, 73.6, -173.3, -51.3]

def getSouthAmericabb():
    return [-56.2, 12.8, -95.3, -30.5]

def getAustraliabb():
    return [-48.5, -9.4, 109.3, 178.6]

def getJPbb():
    return [30.4, 45.4, 129.5, 147.0]

def getWorldbb():
    return [-35.0, 60.0, -180.0, 180.0]

def getNZbb():
    return [-47.4, -34.3, 166.2, 178.9];

def getUSbb():
    return [29.6, 49.1, -125.5, -69.3];

def getUKbb():
    return [49.5, 59.0, -11.3, 2.8];

def getMarch():
    return [[2011, 3, 1, 30]];

def getAugust():
    return [[2011, 8, 1, 30]];

#not include the day_to
def getJPEQPeriod():
    return [[2011, 3, 11, 16]];

def getIrenePeriod():
    return [[2011, 8, 20, 30]];

def getJobsPeriod():
    return [[2011, 10, 5, 10]];

def getRoyalPeriod():
    return [[2011, 4, 29, 31], [2011, 5, 1, 4]];

def getElectionPeriod():
    return [[2012, 4, 1, 31]];

def getNBAPeriod():
    return [[2012, 2, 4, 29]];    

def isTweetInbb2(boundingbox, leftOrRight, upOrDown, tweet_info):
    lati_down  = boundingbox[0];
    lati_up = boundingbox[1];
    longi_left = boundingbox[2];
    longi_right = boundingbox[3];
    long = (longi_right - longi_left)/2.0;
    width = (lati_up - lati_down)/2.0;

    corrdi = tweet_info['geo'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
        
        isInbb = 0;
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            isInbb =  1;
       
        if leftOrRight == 0 and upOrDown == 0:
            return isInbb;

        if isInbb == 0:
            return 0;

        side_tag = 0;
        if leftOrRight == -1:
            if longi <= longi_left + long:
                side_tag = 1;
        else:
            if leftOrRight == 1:
                if longi >= longi_left + long:
                    side_tag = 1;
            else:
                side_tag = 1;

        if side_tag == 0:
            return 0;

        head_tag = 0;
        if upOrDown == -1:
            if lati <= lati_down + width:
                head_tag = 1;
        else:
            if upOrDown == 1:
                if lati >= lati_down + width:
                    head_tag = 1;
            else:
                head_tag = 1;

        return isInbb and side_tag and head_tag;

    return 0;
                
def isTweetInbb(boundingbox, tweet_info):
    lati_down  = boundingbox[0];
    lati_up = boundingbox[1];
    longi_left = boundingbox[2];
    longi_right = boundingbox[3];

    if 'geo' in tweet_info.keys():
        corrdi = tweet_info['geo'];
    else:
        corrdi = tweet_info['corrdinate'];

    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            return 1;

    return 0;

def isTweetInNZ(tweet_info):
    lati_up  = -34.3;
    lati_down = down = -47.4;
    longi_left = 166.2;
    longi_right = 178.9;

    corrdi = tweet_info['geo'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            return 1;

    return 0;

def isTweetInUS(tweet_info):
    lati_down = 29.6;
    lati_up = 49.1;
    longi_left = -125.5;
    longi_right = -69.3; 
       
    corrdi = tweet_info['geo'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            return 1;

    return 0;

def isTweetInUK(tweet_info):
    lati_down = 49.5;
    lati_up = 59.0;
    longi_left = -11.3;
    longi_right = 2.8; 
       
    corrdi = tweet_info['geo'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            return 1;

    return 0;


def isTweetInJapan(tweet_info):
    lati_down = 30.4;
    lati_up = 45.4;
    longi_left = 129.5;
    longi_right = 147.0; 
       
    corrdi = tweet_info['geo'];
    if corrdi != None and corrdi != []:
        lati = corrdi[0];
        longi = corrdi[1];
   
        if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
            return 1;

    return 0;

