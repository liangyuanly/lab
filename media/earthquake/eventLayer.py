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
import nltk
from Utility import *

def loadTags(filename):
    infile = file(filename);
    lines = infile.readlines();
    tag_bins = {};
    i = 0;
    while i < len(lines) - 1:
    #for i in range(0, len(lines)-1):
        tag = lines[i];
        tag = tag[0:len(tag)-1];
        bins = cjson.decode(lines[i+1]);
        tag_bins[tag] = bins;
        i = i + 2;
    
    return tag_bins;

def norBins(tag_bins):
    for tag, bins in tag_bins.iteritems():
        sum = 0;
        for index, freq in bins.iteritems():
            sum = sum + freq;
        
        if sum <= 0:
            continue;

        for index, freq in bins.iteritems():
            if freq > 0:
                bins[index] = freq/float(sum);

def entropy(tag_bins):
    tag_entro = {};
    for tag, bins in tag_bins.iteritems():
        sum = 0;
        for index, freq in bins.iteritems():
            sum = sum + freq;
        
        if sum <= 0:
            continue;

        entro = 0;
        for index, freq in bins.iteritems():
            if freq > 0:
                entro = entro - math.log(freq/float(sum));
        
        tag_entro[tag] = [sum, entro];

    return tag_entro;

def selectTagByDay(day, tag_bins, tag_entro):
    select = [];
    for tag, bins in tag_bins.iteritems():
        sum = 0;
        for idex, freq in bins.iteritems():
            sum = sum + freq;

        aver = sum / float(len(bins));
        array = tag_entro[tag];
        count = array[0];
        entro = array[1];
        if count > 200 and bins[str(day)] > aver * 5:
            print tag, bins[str(day)];
            select.append(tag);
    return select;
        
def selectTagByEntro(tag_entro):
    sum_entro = 0;
    for tag, array in tag_entro.iteritems():
        count = array[0];
        entro = array[1];
        sum_entro = sum_entro + entro;
        #print tag, count, entro;

    threshold = sum_entro / float(len(tag_entro));

    for tag, array in tag_entro.iteritems():
        count = array[0];
        entro = array[1];

        if count > 100 and entro < threshold * 2:
            print tag, count, entro;

def findClosest(sel_tag, tag_bins):
    dis_dic = {};
    sel_bins = tag_bins[sel_tag];
    for tag, bins in tag_bins.iteritems():
        if sel_tag == tag:
            continue;

        dis = 0;
        for index, freq in sel_bins.iteritems():
            dis = dis + abs(freq - bins[index]);

        dis_dic[tag] = dis;

    
    for tag, dis in sorted(dis_dic.iteritems(), key=lambda (k,v):(v,k)):
        print tag, dis;

def findClosestMain():
    filename = './output/Event/world_tag_bin_2011_3.txt';
    tag_bins = loadTags(filename);
    norBins(tag_bins);

    tag = '"apple"';
    findClosest(tag, tag_bins);

def tempDist(tag_bins, select):
    num = len(select);
    dis_matrix = allocMatrix(num, num);
    for i in range(0, num):
        tag1 = select[i];
        for j in range(0, num):
            tag2 = select[j]
            if tag1 == tag2:
                continue;
            
            dis = 0;
            for key in tag_bins[tag1].keys():
                dis = dis + abs(tag_bins[tag1][key] - tag_bins[tag2][key]);
            dis_matrix[i][j] = dis;
    return dis_matrix;

def selectTagMain():
    filename = './output/Event/world_tag_bin_2011_3.txt';
    tag_bins = loadTags(filename);
    tag_entro = entropy(tag_bins);
    #selectTagByEntro(tag_entro);
    norBins(tag_bins);
    select = selectTagByDay(10, tag_bins, tag_entro);
    
    matrix = tempDist(tag_bins, select);
    cluster = kmeansTokens(matrix, 8);

    outfile = file('./output/Event/cluster_of_2011_3.txt', 'w');
    for key, tokens in cluster.iteritems():
        #outfile.write(key.encode('utf-8') + '\n');
        for token in tokens:
            outfile.write(select[token] + '\t');
        outfile.write('\n\n');
    outfile.close();

selectTagMain();
#findClosestMain();
