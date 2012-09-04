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
import sys
sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *

def purity(cluster_truth, cluster):
    purity_num = 0;
    for key, a_cluster in cluster.iteritems():
        mixed_item = {};
        for term in a_cluster:
            if not term in cluster_truth.keys():
                continue;

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

def closest(term, dis_matrix, sel_tokens):
    min_dis = 10000;
    chosen_term = '';
    for term2, dis in dis_matrix[term].iteritems():
        if term == term2:
            continue;
            
        if dis < min_dis and term2 in sel_tokens:
            min_dis = dis;
            chosen_term = term2;
    return chosen_term;

def K_NN(dis_matrix, truth_file, K, format='unicode'):
    cluster, truth_label = loadCluster(truth_file, format);
    #k-nn
    accu = 0;
    for term in dis_matrix.keys():
        if term not in truth_label.keys():
            continue;

        chosen_term = closest(term, dis_matrix, truth_label.keys());
        if chosen_term == '':
            continue;

        chosen_cluster = truth_label[chosen_term];
        truth_cluster = truth_label[term];
        
        if chosen_cluster == truth_cluster:
            accu = accu + 1;

    return accu/float(len(truth_label));

def purityFunc(truth_file, cluster_file, format='unicode'):
    cluster, truth_label = loadCluster(truth_file, format);
    cluster, label = loadCluster(cluster_file, format);

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
