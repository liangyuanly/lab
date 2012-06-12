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
import ast
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.api import *
from tinysegmenter import *
from settings import Settings
from operator import itemgetter
from Utility import *
import random
from utility.dijkstra import *
from utility.MST import *

def loadCluster(filename):
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
                cluster[label].append(term);
                term_label[term] = label;
            i = i + 1;
        i = i + 1;
        label = label + 1;

    return cluster, term_label;

def purity(cluster_truth, cluster):
    purity_num = 0;
    for key, a_cluster in cluster.iteritems():
        mixed_item = {};
        for term in a_cluster:
            label = cluster_truth[term];
            if mixed_item.get(label) == None:
                mixed_item[label] = 0;
            mixed_item[label] = mixed_item[label] + 1;
        max_purity = 0;
        for label, freq in mixed_item.iteritems():
            if freq > max_purity:
                max_purity = freq;

        purity_num = purity_num + max_purity;

    return purity_num / float(len(cluster_truth));

def purityFunc(truth_file, cluster_file):
    cluster, truth_label = loadCluster(truth_file);
    cluster, label = loadCluster(cluster_file);

    purity_ratio = purity(truth_label, cluster);
    return purity_ratio;
    
def purityMain():
    truth_file = './data/cluster_truth.txt';
    cluster, truth_label = loadCluster(truth_file);
    
    #cluster_file = './output/Map/cluster_of_tmpdis_US.txt';
    #cluster_file = './output/Map/cluster_of_ococur8_24.txt';
    #cluster_file = './output/Map/cluster_of_geodis_US_kernel.txt';
    
    #cluster_file = './output/Map/cluster_of_tmpdis.txt';
    #cluster_file = './output/Map/cluster_of_ococur.txt';
    #cluster_file = './output/Map/cluster_of_geodis.txt';
    #cluster_file = './output/Map/cluster_of_geodis_kernel.txt';
    #cluster_file = './output/Map/cluster_of_geotmpdis_JP.txt';
    cluster_file = './output/Map/cluster_of_user_JPEQ.txt';
    cluster, label = loadCluster(cluster_file);

    purity_ratio = purity(truth_label, cluster);
    print purity_ratio;

#purityMain();
