#m/usr/bin/pythoni
#from matplotlib.patches import Polygon 
#from mpl_toolkits.basemap import Basemap
#import matplotlib.pyplot as plt
#import numpy as np
#import matplotlib as mpl

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
from graphOfTokens import disOfTemp, disOfTemp2
from termEventCommon import *
from filterType import meanFilter, averageFilter

g_selected_words = {}

def purityWrap(clusters, truth_file, format):
    outfilename = 'output//cluster_temp.txt'
    outfile = file(outfilename, 'w');
    for key, tokens in clusters.iteritems():
        for token in tokens:
            outfile.write(token.encode('utf-8')+'\t');
        outfile.write('\n\n');
    outfile.close();

    puri = purityFunc(truth_file, outfilename, format);
    return puri;

def getWords(truth_cluster):
    words = [];
    for index, cluster in truth_cluster.iteritems():
        for term in cluster:
            if term[0] == '"':
                term =  term[1:len(term)];
            if term[len(term)-1] == '"':
                term = term[0:len(term)-1];
            words.append(term)
    return words;

def initNetwork(event, term_time, format, init_method, dis_method):
    global g_selected_words

    dirname = 'data/event/' + event 

    #init_method = 'temp'
    if init_method == 'cooccur':
        print 'coocur initialization!'
        filename = dirname + '/term_coocurence2.txt'
        infile = file(filename);
        if format == 'utf-8':
            dis_matrix = json.load(infile, format);
        else:
            dis_matrix = json.load(infile);
    else: 
        print 'no other inition yet'
    
    dis_matrix = disMatrixFilter(dis_matrix, g_selected_words)
   
    word_sum = {}
    for word, arr in dis_matrix.iteritems():
        n = 0.0
        for w, num in arr.iteritems():
            n += num
        word_sum[word] = n

    new_matrix = {}
    for w1, arr in dis_matrix.iteritems():
        new_matrix[w1] = {}
        for w2, fre in arr.iteritems():
            new_matrix[w1][w2] = fre / (word_sum[w1]*word_sum[w2])

    for w1, arr in new_matrix.iteritems():
        normalizeDic(arr)

    return new_matrix

def averageNetwork(dis_matrix, term_prob):
    new_matrix = {}
    for node, neighbors in dis_matrix.iteritems():
        new_time_prob = deepcopy(term_prob[node])
        for ne, dis in neighbors.iteritems():
            if node == ne:
                continue
            prob = term_prob[ne]
            for time, fre in prob.iteritems():
                if time not in new_time_prob:
                    new_time_prob[time]  = fre * dis
                else:
                    new_time_prob[time] += fre * dis

        normalizeDic(new_time_prob)
        new_matrix[node] = new_time_prob

    return new_matrix

#integrate the co-occur and temporal distances
def disMixer(coocc_dis, temp_dis):
    new_dis = {};
    for w1, arr in coocc_dis.iteritems():
        new_dis[w1] = {}
        for w2, dis in arr.iteritems():
            new_dis[w1][w2] = dis * 0.5

    for w1, arr in temp_dis.iteritems():
        if w1 not in new_dis:
            new_dis[w1] = {}

        for w2, dis in arr.iteritems():
            if w2 not in new_dis:
                new_dis[w1][w2] = 1

            new_dis[w1][w2] += dis*0.5

        normalizeDic(new_dis[w1])

    return new_dis

def iterNetwork(coocc_dis, temp_prob, truth_file, cluster_num):
    iter = 0;
    metrics = {}
    accu_metrics = {}

    temp_dis = disOfTemp2(temp_prob, 'manhattan', 'hour')
    clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
    #print clusters
    puri = purityWrap(clusters, truth_file, 'utf-8')
    metrics['temp'] = puri;
    accu_metrics['temp'] = K_NN(temp_dis, truth_file, 1, 'utf-8')
    
    net_dis = coocc_dis
    while iter < 10:
        new_term_prob = averageNetwork(net_dis, temp_prob)
        temp_dis = disOfTemp2(new_term_prob, 'manhattan', 'hour')
        clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
        #print clusters
        puri = purityWrap(clusters, truth_file, 'utf-8')
        metrics['temp_net'] = puri;
        accu_metrics['temp_net'] = K_NN(temp_dis, truth_file, 1, 'utf-8')
        
        net_dis = disMixer(coocc_dis, temp_dis)

        print iter, metrics, accu_metrics

        iter += 1
        

def iterThetaWordTime(event, cluster_num, format, dis_method, filter_type):
    #first use the co-occur as the metric to cluster tokens
    prob_theta_time = {};
    prob_word_theta = {};
    metrics = {};
    accu_metrics = {};

    filename = 'data/event/' + event + '/term_time.txt'; #/term_time_location.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    for term, time_bin in term_prob.iteritems():
        normalizeDic(time_bin);
    if 'mean' in filter_type:
        print 'mean filter'
        term_prob = meanFilter(term_prob);
    print 'the term count of term_time loaded is', len(term_prob);

    #filename = 'data/event/' + event + '/term_time.txt';
    #infile = file(filename);
    #term_one_place_prob = json.load(infile);
    #infile.close();
    #for term, time_bin in term_one_place_prob.iteritems():
    #    normalizeDic(time_bin);

    theta_file = 'data/event/' + event + '/iter_theta_prob.txt';
    out_theta_file = file(theta_file, 'w');
    
    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
   
    #based on co-occurrence
    coocc_dis = initNetwork(event, term_prob, format, 'cooccur', 'manhattan')
    clusters, center_temp = kmeansTokensWrap(coocc_dis, cluster_num, [])
    #print clusters
    puri = purityWrap(clusters, truth_file, format)
    metrics['cooccur'] = puri;
    accu_metrics['cooccur'] = K_NN(coocc_dis, truth_file, 1, format)

    #iterative network update
    iterNetwork(coocc_dis, term_prob, truth_file, cluster_num)


    dis_matrix = initNetwork(event, term_prob, format, 'cooccur', 'manhattan')
    new_term_prob = averageNetwork(dis_matrix, term_prob)
    dis_matrix = disOfTemp2(new_term_prob, dis_method, 'hour')
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityWrap(clusters, truth_file, format)
    metrics['temp_net'] = puri;
    accu_metrics['temp_net'] = K_NN(dis_matrix, truth_file, 1, format)
  
    #use the temporal-location
    dis_matrix = disOfTemp2(term_prob, dis_method, 'hour')
    dis_matrix = disMatrixFilter(dis_matrix, g_selected_words) 
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityWrap(clusters, truth_file, format)
    metrics['temp'] = puri;
    accu_metrics['temp'] = K_NN(dis_matrix, truth_file, 1, format)

    
    print metrics, '\n'
    print accu_metrics
    ####test, return first
    return metrics, accu_metrics

def termIterEventMain(event, cluster_num, format, filter_type):
    global g_selected_words
    
    outfilename = 'data/event/' + event + '/results_temporal.txt';
    outfile = file(outfilename, 'w');

    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
    
    term_count = 0;
    for theta, acluster in true_clusters.iteritems():
        term_count += len(acluster);
    print 'load term from file, the number is', term_count;

    g_selected_words = getWords(true_clusters);

    metric_sum = {};
    accu_metric_sum = {};
    iter_count = 10;
    for i in range(0, iter_count):
        dis_method = 'abs'
        print 'hard cluster, Manhanttan distance!!!!!'
        metric, accu_metric = iterThetaWordTime(event, cluster_num, format, dis_method, filter_type);
        for key, value in metric.iteritems():
            if key not in metric_sum:
                metric_sum[key] = 0;
                accu_metric_sum[key] = 0;
            metric_sum[key] += metric[key];
            accu_metric_sum[key] += accu_metric[key];
    for key in metric_sum:
        metric_sum[key] /= iter_count;
        accu_metric_sum[key] /= iter_count;

    outfile.write('purity based on Manhattan distance\n')
    for key, value in metric_sum.iteritems():
        outfile.write(key + '\t' + str(value) + '\n');
    outfile.write('\nAccuracy based on Manhattan distance\n')
    for key, value in accu_metric_sum.iteritems():
        outfile.write(key + '\t' + str(value) + '\n');
    outfile.write('\n');

    ###test
    outfile.close();
    return;

def eventMain():
    #filter_type = [];
    filter_type = ['mean'];
    format = 'utf-8'
    
    event = 'irene_overall'
    cluster_num = 3;
    termIterEventMain(event, cluster_num, format, filter_type)
 
    event = 'jpeq_jp'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)
   
    event = '3_2011_events'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)
    
    event = '8_2011_events'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)

eventMain()
