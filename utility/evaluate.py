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
#from parser import HTMLParsers
#from parser import Utilities
import ast
import nltk
#from nltk.tokenize import RegexpTokenizer
#from nltk.tokenize.api import *
#from tinysegmenter import *
from settings import Settings
from operator import itemgetter
#from Utility import *
import random
#from utility.dijkstra import *
#from utility.MST import *
import sys
#sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *

def compareList(list1, list2):
    co = 0;
    for it in list1:
        if it in list2:
            co +=1

    return co

def recallPrecision(rank_list, true_list):
    new_rank_list = {}

    k = 11    
    #select the coorsponding cluster for the rank list
    for center, list in rank_list.iteritems():
        sel_center = center
        max_com = 0
        for theta, arr in true_list.iteritems():
            ret = compareList(list[:k], arr[:k]) 
            if ret > max_com:
                sel_center = theta
                max_com =  ret

        new_rank_list[sel_center] = list

    recall = {}
    prec = {}
    max_len = 0
    for theta, list in new_rank_list.iteritems():
        recall[theta] = []
        prec[theta] = []
        true_terms = true_list[theta]
        rel = 0.0
        count = 0.0
        if len(list) > max_len:
            max_len = len(list)

        for item in list:
            if item in true_terms:
                rel += 1
            count += 1
            
            pr = rel/count
            re = rel/len(true_terms)
            
            recall[theta].append(re)
            prec[theta].append(pr)

    aver_recall = [0 for i in range(max_len)]
    aver_prec = [0 for i in range(max_len)]
    for theta in recall:
        num = 0.0
        for k in range(max_len):
            if k < len(recall[theta]):
                aver_recall[k] += recall[theta][k]
                aver_prec[k] += prec[theta][k]
    
    theta_num  = float(len(prec))
    aver_prec = [i/theta_num for i in aver_prec]
    aver_recall = [i/theta_num for i in aver_recall]

    return aver_prec, aver_recall

def precisionRank(rank_list, true_cluster):
    new_rank_list = {}

    k = 11    
    #select the coorsponding cluster for the rank list
    for center, list in rank_list.iteritems():
        sel_center = center
        max_com = 0
        for theta, arr in true_cluster.iteritems():
            ret = compareList(list[:k], arr[:k]) 
            if ret > max_com:
                sel_center = theta
                max_com =  ret

        new_rank_list[sel_center] = list

    #cumulative precision
    print new_rank_list
    accu = []
    for count in range(1, k+1):
        s = 0
        for theta, list in new_rank_list.iteritems():
            if count >= len(list):
                continue

            arr = true_cluster[theta]
            if list[count] in arr:
                s += 1
        accu.append(s)

    prec = []
    rec = []
    for count in range(1, k+1): 
        ac = sum(accu[:count])/float(count*len(true_cluster))
        prec.append(ac)

    print prec
    return prec

def purityOfCluster(cluster1, cluster2):
    cluster_lable= {};
    label = 1;
    for key, a_cluster in cluster1.items():
        for term in a_cluster:
            cluster_lable[term] = label;
        label += 1;

    purity_num = 0;
    for key, a_cluster in cluster2.items():
        mixed_item = {};
        for term in a_cluster:
            if not term in cluster_lable:
                continue;

            label = cluster_lable[term];
            if mixed_item.get(label) == None:
                mixed_item[label] = 0;
            mixed_item[label] = mixed_item[label] + 1;

        max_purity = 0;
        for label, freq in mixed_item.iteritems():
            if freq > max_purity:
                max_purity = freq;

        purity_num = purity_num + max_purity;

    return purity_num / float(len(cluster_lable));


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
