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

def centerTokens(dist_matrix, cluster_label):
    new_centroid = [];
    for center, tokens in cluster_label.iteritems():
        min_dist = 1111111;
        new_center = center;
        for token in tokens:
            total_dist = 0;
            for token2 in tokens:
                total_dist = total_dist + dist_matrix[token][token2];
            if total_dist < min_dist:
                min_dist = total_dist;
                new_center = token;
        new_centroid.append(new_center);

    return new_centroid;

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
    
    list = matrix;
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
            for center in centroid:
                if center not in matrix:      
                    print 'error happened, center is not in dis_matrix.keys()'
                    print center, matrix
                    #the error is proably brought by the init_centers
                    center = random.sample(list, 1);
                    center = center[0]
                    while center in centroid:
                        center = random.sample(list, 1);
                        center = center[0]

                if center not in cluster:
                    cluster[center] = [];

                if matrix[center][token] < min_dis:
                    min_dis = matrix[center][token];
                    sel_label = center;
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
