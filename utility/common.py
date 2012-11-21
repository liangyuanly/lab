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
import random

#what the fuck, what the hell is this....
#def normMatrix(dis_matrix):
#    for term1 in dis_matrix.keys():
#        max = 0;
#        for term2, count in dis_matrix[term1].iteritems():
#            #sum = sum + count;
#            if  count > max:
#                max = count;
#
#        if max <= 0:
#            continue;
#
#        for term2 in dis_matrix.keys():
#            if term1 == term2:
#                continue;
#            if dis_matrix[term1][term2] == 0:
#                dis_matrix[term1][term2] = 1000;
#            else:    
#                dis_matrix[term1][term2] = max/float(dis_matrix[term1][term2]);

def normMatrix(dis_matrix):
    sum = 0.0;
    for term1 in dis_matrix.keys():
        for term2, count in dis_matrix[term1].iteritems():
            sum = sum + count;
    
    if sum <= 0:
        return;

    for term1 in dis_matrix.keys():
        for term2, count in dis_matrix[term1].iteritems():
            dis_matrix[term1][term2] /=  sum;

def normalizeDic(dic):
    sum = 0.0;
    for key, ele in dic.iteritems():
        sum = sum + ele;
    
    if sum > 0:
        for key, freq in dic.iteritems():
            dic[key] = freq/sum;

def allocMatrix(n, m, value=0):
    matrix = {};
    #array
    if n == 1:
        for j in range(0, m):
            matrix[j] = value;
    else:
        for i in range(0, n):
            matrix[i] = {};
            for j in range(0, m):
                matrix[i][j] = value;
    return matrix;

def norMatrix(matrix):
    sum = 0;
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            sum = sum + matrix[i][j];
    
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            if sum != 0:
                matrix[i][j] = matrix[i][j]/float(sum);

def tweetTimeToDatetime(time):
    d = datetime.datetime.strptime(time,'%a %b %d %H:%M:%S +0000 %Y');
    return d;

def datetimeToStr2(time):
    f = "%Y-%m-%d_%H_%M_%S";
    time_str = datetime.datetime.strftime(time, f);
    return time_str;

def datetimeToStr(time):
    f = "%Y-%m-%d_%H:%M:%S";
    time_str = datetime.datetime.strftime(time, f);
    return time_str;

def datetimeDateToStr(time):
    f = "%Y-%m-%d";
    time_str = datetime.datetime.strftime(time, f);
    return time_str;

def strTimeToDatetime(time, format):
    d = datetime.datetime.strptime(time, format);
    return d;
