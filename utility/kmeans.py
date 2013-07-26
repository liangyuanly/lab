#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
import ast
from tinysegmenter import *
from operator import itemgetter
import random
import scipy
import scipy.cluster.hierarchy as sch
from common import *
from loadFile import *

def centerTokens(dist_matrix, cluster_label):
    new_centroid = [];
    for center, tokens in cluster_label.iteritems():
        min_dist = 1111111;
        new_center = center;
        for token in tokens:
            total_dist = 0;
            for token2 in tokens:
                if token in dist_matrix and token2 in dist_matrix[token]:
                    total_dist = total_dist + dist_matrix[token][token2];
                else:
                    total_dist += 2;

            if total_dist < min_dist:
                min_dist = total_dist;
                new_center = token;
        new_centroid.append(new_center);

    return new_centroid;

def centerTokensDis(dist_matrix, cluster_label):
    new_centroid = {};
    aver_dis = {};
    for center, tokens in cluster_label.iteritems():
        min_dist = 1111111;
        new_center = center;
        for token in tokens:
            total_dist = 0;
            for token2 in tokens:
                if token in dist_matrix and token2 in dist_matrix[token]:
                    total_dist = total_dist + dist_matrix[token][token2];
                else:
                    total_dist += 2;

            if total_dist < min_dist:
                min_dist = total_dist;
                new_center = token;
                aver_dis[center] = total_dist/float(len(tokens));

        new_centroid[center] = new_center;

    return new_centroid, aver_dis;


def hierachyClusterTokens(term_matrix, K):
    tokens = term_matrix.keys();
    index_dic = {};
    index = 0;
    for token in tokens:
        index_dic[token] = index;
        index += 1;

    n = len(tokens);
    matrix = allocMatrix(n, n, 1000);

    for token, list in term_matrix.iteritems():
        index1 = index_dic[token];
        for token2, dis in list.iteritems():
            index2 = index_dic[token2];
            matrix[index1][index2] = dis;
    
    #test
    for i in range(0, n):
        for j in range(i, n):
            print matrix[i][j], matrix[j][i];

    y = [];
    for i in range(0, n):
        x = [];
        for j in range(0, n):
            if i == j:
                x.append(0);
            else:
                x.append(matrix[i][j]);
        y.append(x);

    print y;
    Y = np.array(y);
    Z = sch.centroid(Y);
    C = sch.fcluster(Z, criterion='maxclust', t=K);
    print C;
    clusters = {};
    for i in range(0, len(C)):
        token = tokens[i];
        index = C[i];
        if index not in clusters:
            clusters[index] = [];
        clusters[index].append(token);

    return clusters, [];

def kmeansTokens(matrix, K, init_centers=[]):

    #return hierachyClusterTokens(matrix, K)
    
    list = matrix.keys();

    if len(init_centers) <= 0:
        centroid = random.sample(list, K);
    else:
        centroid = init_centers;

    label = {};
    dist = {};

    iter = 0;
    isChange = True;
    while iter < 100 and isChange:
        iter = iter + 1;
        # label the tokens
        cluster = {};
        #for center in centroid:
        #    cluster[center] = [];

        for token in list:
            min_dis = 11111111;
            sel_label = ''
            for center in centroid:
                if center not in matrix:      
                    print 'error happened, center is not in dis_matrix.keys()'
                    #the error is proably brought by the init_centers
                    center = random.sample(list, 1);
                    center = center[0]
                    while center in centroid:
                        center = random.sample(list, 1);
                        center = center[0]

                if token in matrix[center] and matrix[center][token] < min_dis:
                    min_dis = matrix[center][token];
                    sel_label = center;
                
           
            if not sel_label == '':
                if sel_label not in cluster:
                    cluster[sel_label] = [];

                cluster[sel_label].append(token);

        # re-cal the centriod
        new_centroid = centerTokens(matrix, cluster);
        for center in new_centroid:
            if center not in centroid:
                isChange = True;
                break;
            isChange = False;
        centroid = new_centroid;
    
    return cluster, centroid

def kmeansTokensWrap(dis_matrix, cluster_num, centroid = []):
    clusters, centers = kmeansTokens(dis_matrix, cluster_num, centroid);
    
    #change the key of the cluster
    new_cluster = {};
    index = 1;
    for key, list in clusters.iteritems():
        new_cluster[index] = list;
        index += 1;
    
    return new_cluster, centers

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

def labelCluster(true_cluster):
    label = {}
    for cl, cluster in true_cluster.iteritems():
        for term in cluster:
            if term not in label:
                label[term] = []

            label[term].append(cl)

    return label

def accuracyCluster(cluster, true_cluster):
    cluster_label = labelCluster(cluster)
    truth_label = labelCluster(true_cluster);
    acc = 0
    print cluster_label
    print truth_label
    for term, label in cluster_label.iteritems():
        if term not in truth_label:
            continue

        print term, label, truth_label[term]

        for cl in label:
            if cl in truth_label[term]:
                acc += 1;
                break
            else:
                for t in truth_label[term]:
                    terms = true_cluster[t]
                    if cl in terms:
                        acc += 1
                        break

    return acc/float(len(truth_label))

def K_NN_cluster(dis_matrix, true_cluster, K):
    truth_label = labelCluster(true_cluster);
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
        
        if truth_cluster == chosen_cluster:
            accu = accu + 1;
    
    return accu/float(len(truth_label));

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

