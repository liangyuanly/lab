#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
#from matplotlib.patches import Polygon 
#from mpl_toolkits.basemap import Basemap
#import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.mlab import griddata 
from matplotlib import cm
from filterType import *

import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
from scipy import *

sys.path.append('../../cluster_tag/')
sys.path.append('./tag/')
sys.path.append('../../utility/')
from common import *
from boundingBox import *
from loadFile import *
from kmeans import *
from evaluate import *
from graphOfTokens import disOfTerm, disOfTimeGeo, transPoints, disOfTemp2, transTimePoints, transPoints2 
from termEventCommon import *
#from cluster import ClusterUsingLocFilter
from disMeasure import DisCalculator
from featureExtractor import FeatureExt

g_selected_words = []

def purityWrap(clusters, truth_file, format, dis_matrix):
    outfilename = 'output//cluster_temp.txt'
    outfile = file(outfilename, 'w');
    for key, tokens in clusters.iteritems():
        for token in tokens:
            outfile.write(token.encode('utf-8')+'\t');
        outfile.write('\n\n');
    outfile.close();

    puri = purityFunc(truth_file, outfilename, format);
    acc = K_NN(dis_matrix, truth_file, 1, format)
    
    return puri, acc;


def filterTerms(term_dic, term_list):
    for term in term_dic.keys():
        if term not in term_list:
            del term_dic[term];

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

def averageNetwork(dis_matrix, term_prob, ne_count):
    new_matrix = {}
    for node, neighbors in dis_matrix.iteritems():
        new_time_prob = deepcopy(term_prob[node])
        for ne, dis in neighbors.iteritems():
            if node == ne:
                continue
            if dis == 0:
                continue;

            prob = term_prob[ne]
            for time, fre in prob.iteritems():
                if time not in new_time_prob:
                    new_time_prob[time]  = fre * 1/dis
                else:
                    new_time_prob[time] += fre * 1/dis

        normalizeDic(new_time_prob)
        new_matrix[node] = new_time_prob

    return new_matrix

def iterNetwork(coocc_dis, temp_prob, truth_file, cluster_num, ne_count):
    iter = 0;
    metrics = {}
    accu_metrics = {}

    #temp_dis = disOfTemp2(temp_prob, 'manhattan', 'hour')
    #clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
    #puri = purityWrap(clusters, truth_file, 'utf-8')
    #metrics['temp'] = puri;
    #accu_metrics['temp'] = K_NN(temp_dis, truth_file, 1, 'utf-8')
    
    net_dis = coocc_dis
    while iter < 5:
        new_term_prob = averageNetwork(net_dis, temp_prob, ne_count)
        temp_dis = disOfTemp2(new_term_prob, 'manhattan', 'hour')
        clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
        #print clusters
        puri, acc = purityWrap(clusters, truth_file, 'utf-8', temp_dis)
        metrics['temp_net'] = puri;
        accu_metrics['temp_net'] = acc
        
        net_dis = disMixer(coocc_dis, temp_dis)

        print iter, metrics, accu_metrics

        iter += 1
    
    return metrics['temp_net'], accu_metrics['temp_net']

def iterThetaWordLoc(event, cluster_num, format, use_kernel, map, bydegree, ne_count):
    #first use the co-occur as the metric to cluster tokens
    global g_selected_words
    prob_theta_time = {};
    prob_word_theta = {};
    out_puri = {};
    
    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
    g_selected_words = label.keys()

    #filename = 'data/event/' + event + '/term_time_geo.txt';
    #infile = file(filename);
    #term_locs = json.load(infile);
    #infile.close();
    #filterTerms(term_locs, label);
    #term_time_locs = transTimePoints(term_locs, use_kernel, map, bydegree, 100);
    #indexKey(term_time_locs);

    filename = 'data/event/' + event + '/term_location.txt';
    infile = file(filename);
    term_locs = json.load(infile);
    infile.close();
    filterTerms(term_locs, label);
    #term_locs = transPoints(term_locs, use_kernel, map, bydegree, 100);
    term_locs = transPoints2(term_locs, 0, map, bydegree, 100); 
 
    #use co-occur init the cluster
    coocc_dis = initNetwork(event, term_locs, format, 'cooccur', 'manhattan');
    new_term_locs = averageNetwork(coocc_dis, term_locs, ne_count)
    dis_matrix = DisCalculator.disOfGeo(new_term_locs);
    clusters_temp, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    puri, accu = purityWrap(clusters_temp, truth_file, format, dis_matrix)
    out_puri['spa_net'] = puri;
    out_puri['spa_net_accuracy'] = accu;

    if use_kernel:
        term_locs = meanLocFilter(term_locs)

    out_puri['spa_net_iter'], out_puri['spa_net_iter'] = iterNetwork(coocc_dis, term_locs, truth_file, cluster_num, ne_count)
    print out_puri;
    return out_puri;
  
    #use the geo-spatial distance to cluster, for comparison
    #dis_matrix = disOfTerm(term_locs, 'abs')
    dis_matrix = DisCalculator.disOfGeo(term_locs);
    clusters_temp, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    puri, accu = purityWrap(clusters_temp, truth_file, format, dis_matrix)
    out_puri['spa'] = puri;
    out_puri['spa_accuracy'] = accu;

    print out_puri;
    return out_puri;


def termThetaCluterMain(event, cluster_num, bb, use_kernel, byDegree, ne_count):
    final_puri = {};
    iter_num = 2;
    for i in range(0, iter_num):
        puri = iterThetaWordLoc(event, cluster_num, format, use_kernel, bb, byDegree, ne_count)
    
        for key, f in puri.iteritems():
            if key not in final_puri:
                final_puri[key] = 0;
            final_puri[key] += f;
    for key in final_puri:
        final_puri[key] /= iter_num;
    
    filename = 'data/event/' + event + '/result_loc.txt';
    outfile = file(filename, 'a');
    outfile.write(str(ne_count) + '\n')
    json.dump(final_puri, outfile);
    outfile.write('\n');
    outfile.close();

def cooccurDis(dis_matrix):
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
            new_matrix[w1][w2] = (word_sum[w1]*word_sum[w2]) /  fre

    for w1, arr in new_matrix.iteritems():
        normalizeDic(arr)

    return new_matrix

def loadTruth(filename):
    infile = file(filename)
    lines = infile.readlines();
    clusters = {};
    count = 1;
    for line in lines:
        if len(line) < 2:
            continue
        clusters[str(count)] = []

        line = line[:-1]
        terms = line.split(',')
        for term in terms:
            clusters[str(count)].append(term)

        count += 1

    return clusters

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

def iterNetworkCluster(coocc_dis, temp_prob, truth_cluster, cluster_num):
    iter = 0;
    metrics = {}
    accu_metrics = {}

    #temp_dis = disOfTemp2(temp_prob, 'manhattan', 'hour')
    #clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
    #puri = purityWrap(clusters, truth_file, 'utf-8')
    #metrics['temp'] = puri;
    #accu_metrics['temp'] = K_NN(temp_dis, truth_file, 1, 'utf-8')
    
    net_dis = coocc_dis
    while iter < 5:
        new_term_prob = averageNetwork(net_dis, temp_prob, ne_count)
        temp_dis = disOfTemp2(new_term_prob, 'manhattan', 'hour')
        clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
        #print clusters
        puri = purityOfCluster(clusters, truth_cluster)

        metrics['temp_net'] = puri;
        accu_metrics['temp_net'] = K_NN_cluster(temp_dis, truth_cluster, 1)
        
        net_dis = disMixer(coocc_dis, temp_dis)

        print iter, metrics, accu_metrics

        iter += 1
    
    return metrics['temp_net'], accu_metrics['temp_net']

def newEventMain():
    metrics = {};
    accu_metrics = {}
    cluster_num = 7
    ne_count = 1000;

    filename = 'data/event/period_event/term_features_for_diff_noises_events.txt';
    term_timebin, term_locbin, term_occur = FeatureExt.getFeatures(filename);
   
    truth_file = 'data/event/period_event/diff_noise_terms';
    true_clusters = loadTruth(truth_file);
    
    #based on co-occurrence
    coocc_dis = cooccurDis(term_occur)
    clusters, center_temp = kmeansTokensWrap(coocc_dis, cluster_num, [])
    #print clusters

    puri = purityOfCluster(clusters, true_clusters)
    metrics['cooccur'] = puri;
    accu_metrics['cooccur'] = K_NN_cluster(coocc_dis, true_clusters, 1)

    #iterative network update
    #metrics['temp_net_iter'], accu_metrics['temp_net_iter'] = iterNetworkCluster(coocc_dis, term_locbin, true_clusters, cluster_num)
    
    new_term_prob = averageNetwork(coocc_dis, term_locbin, ne_count)
    dis_matrix = disOfTemp2(new_term_prob, 'manhattan', 'hour')
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityOfCluster(clusters, true_clusters)
    metrics['temp_net'] = puri;
    accu_metrics['temp_net'] = K_NN_cluster(dis_matrix, true_clusters, 1)
  
    #use the temporal-location
    dis_matrix = disOfTemp2(term_locbin, 'manhattan', 'hour')
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityOfCluster(clusters, true_clusters)
    metrics['temp'] = puri;
    accu_metrics['temp'] = K_NN_cluster(dis_matrix, true_clusters, 1)

    print metrics
    print accu_metrics
    
    filename = 'data/event/period_event/result_loc.txt';
    outfile = file(filename, 'a');
    #outfile.write(str(ne_count) + '\n')
    json.dump(metrics, outfile);
    outfile.write('\n');
    json.dump(accu_metrics, outfile);
    outfile.write('\n')
    outfile.close();


def eventMain():
    format = 'utf-8'
    use_kernel = 1;
    byDegree = 0;
    #all_counts = [1,2,3,4,5,6,7,8,9,10,1000]
    all_counts = [1000]

    for ne_count in all_counts:
        event = 'irene_overall'
        cluster_num = 3;
        bb = getUSbb()
        termThetaCluterMain(event, cluster_num, bb, use_kernel, byDegree, ne_count);

        event = '3_2011_events'
        cluster_num = 5;
        bb = getUSbb()
        termThetaCluterMain(event, cluster_num, bb, use_kernel, byDegree, ne_count);
    
        event = '8_2011_events'
        cluster_num = 5;
        bb = getUSbb()
        termThetaCluterMain(event, cluster_num, bb, use_kernel, byDegree, ne_count);
    
        event = 'jpeq_jp'
        cluster_num = 5;
        bb = getJPbb()
        termThetaCluterMain(event, cluster_num, bb, use_kernel, byDegree, ne_count);
    
eventMain();
#newEventMain()
