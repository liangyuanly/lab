#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
from scipy import *
import random

sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *
from kmeans import *
from disMeasure import DisCalculator

def gaussProb(model, x):
    mu = model[0];
    sigma = model[1];
    return (1/(sqrt(2*pi)*sigma)) * exp(-(x-mu)**2/(2*sigma**2))


def normalizeDic(dic):
    sum = 0.0;
    for key, ele in dic.iteritems():
        sum = sum + ele;
    
    if sum > 0:
        for key, freq in dic.iteritems():
            dic[key] = freq/sum;

def meanFilter(term_prob):
    new_term_prob = copy.copydeep(term_prob);

    for term, time_bin in term_prob.iteritems():
        for time, fre in time_bin.iteritems():
            time = int(time);
    
def disMatrixFilter(dis_matrix, words):
    for key1 in dis_matrix.keys():
        if key1 not in words:
            del dis_matrix[key1];
            continue;
        
        for key2 in dis_matrix[key1].keys():
            if key2 not in words:
                del dis_matrix[key1][key2];

    return dis_matrix

def kmeansTokensWrap(dis_matrix, cluster_num, centroid):
    clusters, centers = kmeansTokens(dis_matrix, cluster_num, centroid);
    
    #change the key of the cluster
    new_cluster = {};
    index = 1;
    for key, list in clusters.iteritems():
        new_cluster[index] = list;
        index += 1;
    
    return new_cluster, centers

def getClusterProb(clusters, term_time, event_num):
    prob_theta_time = {}

    cluster_fre = {};
   
    #normalize term_time
    for term, time_bin in term_time.iteritems():
        normalizeDic(time_bin);

    #event_num = len(clusters)       
    for i in range(1, event_num+1):
        cluster_fre[i] = {};

    for cluster_idx, cluster in clusters.iteritems():
        for token, weight in cluster.iteritems():
            if token not in term_time:
                continue;
            time_bins = term_time[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                if time not in cluster_fre[cluster_idx]:
                    cluster_fre[cluster_idx][time] = 0.0;
                cluster_fre[cluster_idx][time] = cluster_fre[cluster_idx][time] + freq*weight;

    return cluster_fre;

def getTimeProbFromTimeLoc(term_time_locs):
    term_time = {};
    for term, time_locs in term_time_locs.iteritems():
        sum = 0.0;
        term_time[term] = {};
        for time, locs in time_locs.iteritems():
            term_time[term][time] = 0;
            for loc_index, fre in locs.iteritems():
                term_time[term][time] += fre;
                sum += fre;
        if sum == 0:
            print term, 'the term frequency is 0';
            continue;

        for time in term_time[term]:
            term_time[term][time] /= sum;

    return term_time;

#this function is used to calculate the filtering window p(t|theta)
#the windows can be gaussian, square, triangle, etc
#cluster_fre is theta_prob
def getThetaTimeWindow(cluster_fre):
    max_time = 0.0;
    for theta, time_bin in cluster_fre.iteritems():
        for time, fre in time_bin.iteritems():
            if time > max_time:
                max_time = time;
    max_time += 1;

    square_window = {};
    gauss_window = {};
    for theta, time_bin in cluster_fre.iteritems():
        max_fre = 0;
        temp_max_time = 0;
        square_window[theta] = {}; 
        gauss_window[theta] = {};
        for time, fre in time_bin.iteritems():
            if fre > max_fre:
                max_fre = fre;
                temp_max_time = time;

        if len(time_bin) <= 0:
            continue;

        cumu_prob_thred = 0.68;
        #find the windows which cover 80% probability 
        sub_prob = time_bin[temp_max_time];
        left = temp_max_time - 1;
        right = temp_max_time + 1;
        while sub_prob < cumu_prob_thred:
            if left in time_bin:
                sub_prob += time_bin[left];
            if right in time_bin:
                sub_prob += time_bin[right];

            left -= 1;
            right += 1;

        rev_left = left;
        rev_right = right;

        if left < 0:
            left = 0;
        if right > max_time - 1:
            right = max_time - 1;

        #gen the square window
        bin_count = right - left;
        for time in range(0, max_time):
            if time <= right and time >= left:
                square_window[theta][time] = cumu_prob_thred/bin_count;
            else:
                square_window[theta][time] = 0.1*(1 - cumu_prob_thred) / (max_time - bin_count);
       
        #gen the gauss window
        mu = temp_max_time;
        sigma = (rev_right - rev_left)/2; #cdf(mu, sigma) ~= 68%
        for time in range(0, max_time):
            gauss_window[theta][time] = gaussProb([mu, sigma], time);
    
    return square_window, gauss_window;

#this function is used to calculate the p(theta|t) p(t|theta)
def getThetaTimeProb2(clusters, term_one_place_time, event_num):
    prob_theta_time = {}
    cluster_fre = {};
    #event_num = len(clusters)       
    for i in range(1, event_num+1):
        cluster_fre[i] = {};

    for cluster_idx, cluster in clusters.iteritems():
        for token in cluster:
            if token not in term_one_place_time.keys():
                continue;
            time_bins = term_one_place_time[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
        
                if time not in cluster_fre[cluster_idx].keys():
                    cluster_fre[cluster_idx][time] = 0.0;

                cluster_fre[cluster_idx][time] = cluster_fre[cluster_idx][time] + freq;
   
    #cal p(t|theta)
    prob_time_theta = cluster_fre;
    for clustetr_idx, time_fre in prob_time_theta.iteritems():
        normalizeDic(time_fre);  #notice: the time_fre is changed in the normalizeDic function

    return prob_time_theta;


#this function is used to calculate the p(theta|t) p(t|theta)
def getWeightThetaTimeProb(clusters, centers, term_one_place_time, event_num):
    
    return getThetaTimeProb(clusters, term_one_place_time, event_num);

    prob_theta_time = {}

    cluster_fre = {};
    max_time = 0;
   
    #event_num = len(clusters)       
    for i in range(1, event_num+1):
        cluster_fre[i] = {};

    for cluster_idx, cluster in clusters.iteritems():
        for token in cluster:
            if token not in term_one_place_time:
                continue;
            time_bins = term_one_place_time[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                if time > max_time:
                    max_time = time;

    max_time += 1;

    for cluster_idx, cluster in clusters.iteritems():
        for i in range(0, max_time):
            cluster_fre[cluster_idx][i] = 0;
        
        center = centers[cluster_idx-1];
        if center in term_one_place_time:
            center_timebin = term_one_place_time[center];
        else:
            center_timebin = {};
        
        for token in cluster:
            if token not in term_one_place_time:
                continue;
            time_bins = term_one_place_time[token];
            
            dis = DisCalculator.disOfDic(center_timebin, time_bins);
            print center, token, dis;
            if dis == 0:
                weight = 100;
            else:
                weight = 1/dis;

            for time, freq in time_bins.iteritems():
                time = int(time)
                cluster_fre[cluster_idx][time] = cluster_fre[cluster_idx][time] + freq;
    
    #cal p(t|theta)
    prob_time_theta = cluster_fre;
    for clustetr_idx, time_fre in prob_time_theta.iteritems():
        normalizeDic(time_fre);  #notice: the time_fre is changed in the normalizeDic function

    return prob_theta_time, prob_time_theta;

#this function is used to calculate the p(theta|t) p(t|theta)
def getThetaTimeProb(clusters, term_one_place_time, event_num):
    prob_theta_time = {}

    cluster_fre = {};
    max_time = 0;
   
    #normalize term_time
    #for term, time_bin in term_one_place_time.iteritems():
    #    normalizeDic(time_bin);

    #event_num = len(clusters)       
    for i in range(1, event_num+1):
        cluster_fre[i] = {};

    for cluster_idx, cluster in clusters.iteritems():
        for token in cluster:
            if token not in term_one_place_time:
                continue;
            time_bins = term_one_place_time[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                if time > max_time:
                    max_time = time;

    max_time += 1;

    for cluster_idx, cluster in clusters.iteritems():
        for i in range(0, max_time):
            cluster_fre[cluster_idx][i] = 0;

        for token in cluster:
            if token not in term_one_place_time:
                continue;
            time_bins = term_one_place_time[token];
            for time, freq in time_bins.iteritems():
                time = int(time)
                cluster_fre[cluster_idx][time] = cluster_fre[cluster_idx][time] + freq;

    #cal p(theta|t)
#    for cluster_idx, cluster in clusters.iteritems():
#        for term in cluster:
#            #p(theta|t)
#            for time in range(0, max_time):
#                sum_fre = 0.0;
#                prob_theta_time[time] = {};
#                for j in range(1, event_num+1):
#                    if time in cluster_fre[j].keys():
#                        sum_fre += cluster_fre[j][time];
#
#                for j in range(1, event_num+1):
#                    if time in cluster_fre[j].keys():
#                        prob_theta_time[time][j] = cluster_fre[j][time] / sum_fre;
#                    else:
#                        prob_theta_time[time][j] = 0;
    
    #cal p(t|theta)
    prob_time_theta = cluster_fre;
    for clustetr_idx, time_fre in prob_time_theta.iteritems():
        normalizeDic(time_fre);  #notice: the time_fre is changed in the normalizeDic function

    return prob_theta_time, prob_time_theta;

#this function is used to calculate the filtering window p(l|theta)
#the windows can be gaussian, square, triangle, etc
def getThetaLocWindow(theta_locs):
    #normalize term_time
    x_num, y_num = getDimen(theta_locs);
    
    square_window = {};
    gauss_window = {};
    for theta, locs in theta_locs.iteritems():
        max_fre = 0;
        max_x = 0;
        max_y = 0;
        value = 0.1;
        square_window[theta] = allocMatrix(x_num, y_num, value); 
        gauss_window[theta] = allocMatrix(x_num, y_num, value);
        for x, list in locs.iteritems():
            for y, fre in list.iteritems():
                if fre > max_fre:
                    max_fre = fre;
                    max_x = x;
                    max_y = y;

        cumu_prob_thred = 0.5;
        #find the windows which cover 80% probability 
        sub_prob = locs[max_x][max_y];
        x_left = max_x - 1;
        x_right = max_x + 1;
        y_left = max_y - 1;
        y_right = max_y + 1;
        dis_sigma = 0;
        while sub_prob < cumu_prob_thred:
            sub_prob = 0;
            for x in range(x_left, x_right):
                for y in range(y_left, y_right):
                    sub_prob += locs[x][y];

            x_left -= 1;
            x_right += 1;
            y_left -= 1;
            y_right += 1;
            if x_left < 0:
                x_left = 0;
            if y_left < 0:
                y_left = 0;
            if x_right > x_num - 1:
                x_right = x_num - 1;
            if y_right > y_num - 1:
                y_right = y_num - 1;

            dis_sigma += 1;

        #gen the square window
        for x in range(x_left, x_right):
            for y in range(y_left, y_right):
                square_window[theta][x][y] = cumu_prob_thred;
       
        #gen the gauss window
        #mu = temp_max_time;
        #for time in range(0, max_time):
        #    gauss_window[theta][time] = gaussProb([mu, sigma], time);
    
    return square_window # gauss_window;

#location and time are continent _ time_bin
def getThetaTimeLocationWindow(cluster_fre):
    #now we have six continues whose are located in (0,1000), (1000, 2000)....(5000, 6000)
    #now we first find the place has the highest probabilty, then use the time window for this
    #place as the windows for every cluster
    new_cluster_fre = {}
    sum_fre = {}
    for theta, time_bin in cluster_fre.iteritems():
        max_fre = 0
        #then each cluster has the time location demision vector
        for time, fre in time_bin.iteritems():
            time = int(time)
            index = time/1000
            if index not in new_cluster_fre:
                new_cluster_fre[index] = {};
                sum_fre[index] = {}
            if theta not in new_cluster_fre[index]:
                new_cluster_fre[index][theta] = {};
                sum_fre[index][theta] = 0;
            new_cluster_fre[index][theta][time] = fre;
            sum_fre[index][theta] += fre;
    
    all_gauss_window = {};
    all_square_window = {};
    for index, theta_time_bin in new_cluster_fre.iteritems():
        for theta, time_bin in theta_time_bin.iteritems():
            for time, fre in time_bin.iteritems():
                if sum_fre[index][theta] > 0:
                    time_bin[time] /= sum_fre[index][theta];
        square_window, gauss_window = getThetaTimeWindow(theta_time_bin);
        all_gauss_window.update(gauss_window)
        all_square_window.update(square_window)

    return all_square_window, all_gauss_window


