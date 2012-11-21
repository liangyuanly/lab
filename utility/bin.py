#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import numpy as np
import operator
import string
import math

def getTimeBin(time_list, start_time, format, time_step):
    bins = {};
    for time in time_list:
        index = int((time - start_time)/time_step);
        index = str(index);
        if index not in bins:
            bins[index] = 0;
        bins[index] += 1;
    
    return bins;

def getLocBin(loc_list, bb, x_step, y_step, loc_bin):
    #loc_bin = {};
    for loc in loc_list:
        lati = loc[0];
        longi = loc[1];
        x_index = int(float((lati - bb[0]) / x_step));
        y_index = int(float((longi - bb[2]) / y_step));
        key = str(x_index) + '_' + str(y_index);
        if key not in loc_bin:
            loc_bin[key] = 0;
        loc_bin[key] += 1;
    return key;

def getPeakTime(list, start_time, time_step):
    max_value = 0;
    max_index = '';
    for index, value in list.iteritems():
        if value > max_value:
            max_value = value;
            max_index = index;
    
    time = start_time + int(max_index) * time_step;
    return time;

def getPeakLoc(list, bb, x_step, y_step):
    max_value = 0;
    max_index = '';
    for index, value in list.iteritems():
        if value > max_value:
            max_value = value;
            max_index = index;

    print max_value, max_index;    
    x, y = max_index.split('_');
    lati = bb[0] + int(x) * x_step;
    longi = bb[2] + int(y) * y_step;

    return lati, longi;
