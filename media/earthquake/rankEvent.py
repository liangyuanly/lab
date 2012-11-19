#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import math
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
#from scipy import *
import scipy
import random

sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *
from kmeans import *
from evaluate import *
from termEventCommon import getThetaTimeProb

def CalCount(cluster, term_value):
    event_num = len(cluster);
    
    theta_count = {};
    for theta, acluster in cluster.iteritems():
        theta_count[theta] = 0;
        for term in acluster:
            if term in term_value.keys():
                count = term_value[term];
                theta_count[theta] += count;
            else:
                print 'weired, term=', term;
    return theta_count;

def CalMoment(cluster, term_time):
    event_num = len(cluster);
    no_use, theta_time = getThetaTimeProb(cluster, term_time, event_num);
    
    moment = 0;
    theta_moment = {};
    for theta, time_bin in theta_time.iteritems():
        theta_moment[theta] = 0;
        for time, fre in time_bin.iteritems():
            moment += fre**2;
            theta_moment[theta] += fre**2

    return moment, theta_moment;

def CalEntropy(cluster, term_time):
    event_num = len(cluster);
    no_use, theta_time = getThetaTimeProb(cluster, term_time, event_num);
    
    entropy = 0;
    theta_entropy = {};
    for theta, time_bin in theta_time.iteritems():
        theta_entropy[theta] = 0;
        for time, fre in time_bin.iteritems():
            if fre > 0:
                entropy -= fre*math.log(fre);
                theta_entropy[theta] -= fre*math.log(fre);

    return entropy, theta_entropy;

def combineFeatures(multi_theta_value, weights):
    new_theta_value = {};
    for index, theta_value in multi_theta_value.iteritems():
        w = weights[index];
        for theta, value in theta_value.iteritems():
            if theta not in new_theta_value.keys():
                new_theta_value[theta] = 0;
            
            new_theta_value[theta] += w*value;
    
    print new_theta_value
    return new_theta_value;

def getTopEvents(cluster, theta_value, K, bigFirst):
    count = 0;
    sort_cluster = {};
    for theta, value in sorted(theta_value.iteritems(), key = lambda (k,v):(v,k), reverse = bigFirst):
        cluster_term = cluster[theta]
        if len(cluster_term) <= 0:
            continue;

        count += 1;
        sort_cluster[count] = cluster_term;
        if count >= K:
            break;
    
    return sort_cluster;

def evalEvent(cluster, term_time, all_tags, outfile):
    moment, theta_moment = CalMoment(cluster, term_time);
    entropy, theta_entropy = CalEntropy(cluster, term_time);
    theta_count = CalCount(cluster, all_tags)

    mixedFeature = {};
    mixedFeature[1] = theta_moment;
    mixedFeature[2] = theta_count;

    weight = {};
    weight[1] = 0.99999;
    weight[2] = 0.00001;
    new_features = combineFeatures(mixedFeature, weight);

    top_cluster = getTopEvents(cluster, theta_moment, 10, True);
    top_cluster2 = getTopEvents(cluster, theta_entropy, 10, False);
    top_cluster3 = getTopEvents(cluster, new_features, 10, True);

    outfile.write(str(moment) + '\t' + str(entropy) + '\n')
    json.dump(top_cluster, outfile); 
    outfile.write('\n')
    json.dump(top_cluster2, outfile);
    outfile.write('\n')
    json.dump(top_cluster3, outfile);
 
    outfile.write('\n\n')

def loadTagFre(filename):
    infile = file(filename);
    lines = infile.readlines();
    all_tags = {};
    for line in lines:
        data = cjson.decode(line);
        all_tags[data[0]] = int(data[1]);
    infile.close();
    return all_tags;

def evalEventMain():
    dir = 'data/event/3_2011_tags/'
    term_timefile = dir + 'term_time.txt'
    infile = file(term_timefile);
    term_time = json.load(infile);
    infile.close();

    cluster1, label = loadCluster(dir + 'cluster_cooccur', 'unicode');
    cluster2, label = loadCluster(dir + 'cluster_temp', 'unicode');
    cluster3, label = loadCluster(dir + 'cluster_temp_day', 'unicode');
    cluster4, label = loadCluster(dir + 'cluster_post_day', 'unicode');
    cluster5, label = loadCluster(dir + 'cluster_post_hour', 'unicode');
   
    tag_file = dir + 'tag_count.txt';
    all_tags = loadTagFre(tag_file);

    outfilename = dir + 'event_rank.txt';
    outfile = file(outfilename, 'w');
    evalEvent(cluster1, term_time, all_tags, outfile);
    evalEvent(cluster2, term_time, all_tags, outfile)
    evalEvent(cluster3, term_time, all_tags, outfile);
    evalEvent(cluster4, term_time, all_tags, outfile)
    evalEvent(cluster5, term_time, all_tags, outfile)
    outfile.close();

evalEventMain();
