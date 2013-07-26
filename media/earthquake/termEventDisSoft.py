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

sys.path.append('../../cluster_tag/')
sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *
from kmeans import *
from evaluate import *
#from graphOfTokens import disOfTemp, disOfTemp2
from termEventCommon import *
from filterType import meanFilter, averageFilter
from featureExtractor import FeatureExt
from disMeasure import DisCalculator

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
            new_matrix[w1][w2] = fre/(word_sum[w1]*word_sum[w2])

    for w1, arr in new_matrix.iteritems():
        normalizeDic(arr)

    return new_matrix

def averageNetwork(dis_matrix, term_prob, ne_count):
    new_matrix = {}
    for node, neighbors in dis_matrix.iteritems():
        if node not in term_prob:
            continue

        new_time_prob = deepcopy(term_prob[node])
        count = 0;
        for ne, dis in sorted(neighbors.iteritems(), key = lambda (k,v):(v,k)):
            if count >= ne_count:
                break;
            count += 1;

            if node == ne:
                continue
            if dis == 0:
                continue

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
        temp_dis = DisCalculator.disOfTemp2(new_term_prob, 'manhattan', 'hour')
        clusters, center_temp = kmeansTokensWrap(temp_dis, cluster_num, [])
        #print clusters
        puri = purityWrap(clusters, truth_file, 'utf-8')
        metrics['temp_net'] = puri;
        accu_metrics['temp_net'] = K_NN(temp_dis, truth_file, 1, 'utf-8')
        
        net_dis = disMixer(coocc_dis, temp_dis)

        print iter, metrics, accu_metrics

        iter += 1
    
    return metrics['temp_net'], accu_metrics['temp_net']

def iterThetaWordTime(event, cluster_num, format, dis_method, filter_type, ne_count):
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
    metrics['temp_net_iter'], accu_metrics['temp_net_iter'] = iterNetwork(coocc_dis, term_prob, truth_file, cluster_num, ne_count)

    dis_matrix = initNetwork(event, term_prob, format, 'cooccur', 'manhattan')
    new_term_prob = averageNetwork(dis_matrix, term_prob, ne_count)
    dis_matrix = DisCalculator.disOfTemp2(new_term_prob, dis_method, 'hour')
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityWrap(clusters, truth_file, format)
    metrics['temp_net'] = puri;
    accu_metrics['temp_net'] = K_NN(dis_matrix, truth_file, 1, format)
  
    #use the temporal-location
    dis_matrix = DisCalculator.disOfTemp2(term_prob, dis_method, 'hour')
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

def termIterEventMain(event, cluster_num, format, filter_type, ne_count):
    global g_selected_words
    
    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
    
    term_count = 0;
    for theta, acluster in true_clusters.iteritems():
        term_count += len(acluster);
    print 'load term from file, the number is', term_count;

    g_selected_words = getWords(true_clusters);

    metric_sum = {};
    accu_metric_sum = {};
    iter_count = 5;
    for i in range(0, iter_count):
        dis_method = 'abs'
        print 'hard cluster, Manhanttan distance!!!!!'
        metric, accu_metric = iterThetaWordTime(event, cluster_num, format, dis_method, filter_type, ne_count);
        for key, value in metric.iteritems():
            if key not in metric_sum:
                metric_sum[key] = 0;
                accu_metric_sum[key] = 0;
            metric_sum[key] += metric[key];
            accu_metric_sum[key] += accu_metric[key];
    for key in metric_sum:
        metric_sum[key] /= iter_count;
        accu_metric_sum[key] /= iter_count;

    outfilename = 'data/event/' + event + '/results_temporal.txt';
    outfile = file(outfilename, 'a');

    outfile.write(str(ne_count) + '\n')
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

def iterNetworkCluster(coocc_dis, temp_prob, truth_cluster, cluster_num, ne_count):
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
        temp_dis = DisCalculator.disOfTemp2(new_term_prob, 'manhattan', 'hour')
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
    ne_count = 1000

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
    metrics['temp_net_iter'], accu_metrics['temp_net_iter'] = iterNetworkCluster(coocc_dis, term_timebin, true_clusters, cluster_num, ne_count)
   
    for ne_count in [1000]:
        new_term_prob = averageNetwork(coocc_dis, term_timebin, ne_count)
        dis_matrix = DisCalculator.disOfTemp2(new_term_prob, 'manhattan', 'hour')
        clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
        #print clusters
        puri = purityOfCluster(clusters, true_clusters)
        metrics['temp_net_'+str(ne_count)] = puri;
        accu_metrics['temp_net_'+str(ne_count)] = K_NN_cluster(dis_matrix, true_clusters, 1)
  
    #use the temporal-location
    dis_matrix = DisCalculator.disOfTemp2(term_timebin, 'manhattan', 'hour')
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, [])
    #print clusters
    puri = purityOfCluster(clusters, true_clusters)
    metrics['temp'] = puri;
    accu_metrics['temp'] = K_NN_cluster(dis_matrix, true_clusters, 1)

    print metrics
    print accu_metrics

    filename = 'data/event/period_event/result_temporal.txt';
    outfile = file(filename, 'w');
    #outfile.write(str(ne_count) + '\n')
    json.dump(metrics, outfile);
    outfile.write('\n');
    json.dump(accu_metrics, outfile);
    outfile.write('\n')
    outfile.close();


def eventMain():
    #filter_type = [];
    filter_type = ['mean'];
    format = 'utf-8'
    all_counts = [1,2,3,4,5,6,7,8,9,10]
    #all_counts = [1000]

    for ne_count in all_counts:
        event = 'irene_overall'
        cluster_num = 3;
        termIterEventMain(event, cluster_num, format, filter_type, ne_count)
        
        continue
        
        event = '8_2011_events'
        cluster_num = 5;
        termIterEventMain(event, cluster_num, format, filter_type, ne_count)
    
   
        event = '3_2011_events'
        cluster_num = 5;
        termIterEventMain(event, cluster_num, format, filter_type, ne_count)
    
        event = 'jpeq_jp'
        cluster_num = 5;
        termIterEventMain(event, cluster_num, format, filter_type, ne_count)
    
#eventMain()
newEventMain()
