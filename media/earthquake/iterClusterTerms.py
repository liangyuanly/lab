#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
from scipy import *

sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *

def probThetaWordTime(term_prob, clusters):
    prob_theta_time = {};
    prob_word_theta = {};

    #statiscs on the cluster of the terms
    prob_theta_time = {};
    cluster_fre = {};
    token_fre = {};
    max_time = 0;
    cluster_sum_fre = {};
    event_num = len(clusters) + 1;
    for cluster_index, cluster in clusters.iteritems():
        cluster_index = int(cluster_index);
        cluster_fre[cluster_index] = {};
        cluster_sum_fre[cluster_index] = 0.0;
        for token in cluster:
            if token not in term_prob.keys():
                continue;
            token_fre[token] = 0.0;

            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                if time not in cluster_fre[cluster_index].keys():
                    cluster_fre[cluster_index][time] = 0.0;

                if time > max_time:
                    max_time = time;
                cluster_fre[cluster_index][time] += freq;
                token_fre[token] += freq;
                cluster_sum_fre[cluster_index] += freq;

    #p(theta|t)
    for time in range(0, max_time):
        sum_fre = 0.0;
        prob_theta_time[time] = {};
        for j in range(1, event_num):
            if time in cluster_fre[j].keys():
                sum_fre += cluster_fre[j][time];

        for j in range(1, event_num):
            if time in cluster_fre[j].keys():
