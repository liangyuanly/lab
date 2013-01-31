#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
import scipy
from scipy import *
sys.path.append('../../utility/')
from common import *
from disMeasure import DisCalculator
from termEventCommon import normTimeLocs

def meanFilter(term_dis):
    window = 2;
    new_term_dis = {};
    for term, dis in term_dis.iteritems():
        new_term_dis[term] = {};
        for time, fre in dis.iteritems():
            time = int(time);
            if time - window > 0:
                begin = time - window;
            else:
                begin = 0;
            for i in range(begin, time + window):
                i = str(i);
                if i not in new_term_dis[term]:
                    new_term_dis[term][i] = 0;
                new_term_dis[term][i] += fre / float(window);

        normalizeDic(new_term_dis[term]);
    return new_term_dis;

def meanLocFilter(term_dis):
    window = 2;
    new_term_dis = {};
    for term, dis in term_dis.iteritems():
        new_term_dis[term] = {};
        for loc_index, fre in dis.iteritems():
            lat, lon = loc_index.split('_');
            lat = int(lat);
            lon = int(lon);
            for i in range(lat - window, lat + window):
                for j in range(lon - window, lon + window):
                    i = str(i);
                    j = str(j);
                    index = i + '_' + j;
                    if index not in new_term_dis[term]:
                        new_term_dis[term][index] = 0;
                    
                    new_term_dis[term][index] += dis[loc_index] / float(window);

        normalizeDic(new_term_dis[term]);
    return new_term_dis;

def meanFilterTimeLocs(term_dis):
    window = 2;
    new_term_dis = {};
    for term, tmp_dis in term_dis.iteritems():
        new_term_dis[term] = {};
        for tmp, dis in tmp_dis.iteritems():
            new_term_dis[term][tmp] = {};
            for loc_index, fre in dis.iteritems():
                lat, lon = loc_index.split('_');
                lat = int(lat);
                lon = int(lon);
                for i in range(lat - window, lat + window):
                    for j in range(lon - window, lon + window):
                        i = str(i);
                        j = str(j);
                        index = i + '_' + j;
                        if index not in new_term_dis[term]:
                            new_term_dis[term][tmp][index] = 0;
                        
                        new_term_dis[term][tmp][index] += dis[loc_index] / float(window);

        normTimeLocs(new_term_dis[term]);
    return new_term_dis;

#average of multiple terms
def averageFilter(term_dis, theta_prob, clusters):
    new_dis = {};
    for cluster_index, cluster in clusters.iteritems():
        mean_prob = theta_prob[cluster_index];
        for term in cluster:
            new_dis[term] = {};
            time_prob = term_dis[term];
            for time, fre in time_prob.iteritems():
                if time in mean_prob:
                    fre = fre*0.5 + mean_prob[time]*0.5;
                else:
                    fre = fre*0.5;
                new_dis[term][time] = fre;

            for time, fre in mean_prob.iteritems():
                if time in time_prob:
                    continue;
                new_dis[term][time] = fre*0.5;
            
            normalizeDic(new_dis[term]);
    return new_dis;

def averageLocFilter(term_dis, theta_prob, clusters):
    new_dis = {};
    for cluster_index, cluster in clusters.iteritems():
        mean_prob = theta_prob[cluster_index];
        for term in cluster:
            new_dis[term] = {};
            time_prob = term_dis[term];
            for time, fre in time_prob.iteritems():
                if time in mean_prob:
                    fre = fre*0.5 + mean_prob[time]*0.5;
                else:
                    fre = fre*0.5;
                new_dis[term][time] = fre;

            for time, fre in mean_prob.iteritems():
                if time in time_prob:
                    continue;
                new_dis[term][time] = fre*0.5;
            
            normalizeDic(new_dis[term]);
    return new_dis;

def tmpLocWindowFilter(cluster_fre):
    square_window = {};
    gauss_window = {};
    for theta, tmp_locs in cluster_fre.iteritems():
        square_window[theta] = {};
        gauss_window[theta] = {};
        for temp, loc in tmp_locs.iteritems():
            square_window[theta][temp], gauss_window[theta][temp] = locWindow(loc);

    return square_window, gauss_window;


#this function is used to calculate the filtering window p(t|theta)
#the windows can be gaussian, square, triangle, etc
#cluster_fre is theta_prob
def locWindowFilter(cluster_fre):
    square_window = {};
    gauss_window = {};
    for theta, loc_bin in cluster_fre.iteritems():
        square_window[theta], gauss_window[theta] = locWindow(loc_bin);
    
    return square_window, gauss_window;

def locWindow(loc_bin):
    max_fre = 0;
    temp_max_loc = 0;
    square_window = {}; 
    gauss_window = {};
    for time, fre in loc_bin.iteritems():
        if fre > max_fre:
            max_fre = fre;
            temp_max_loc = time;

    if len(loc_bin) <= 0:
        return {},  {};

    cumu_prob_thred = 0.68;
    #find the windows which cover 68% probability 
    sub_prob = loc_bin[temp_max_loc];
    lat, lon = temp_max_loc.split('_');
    lat = int(float(lat));
    lon = int(float(lon));
    left = lon - 1;
    right = lon + 1;
    up = lat - 1;
    down = lat + 1;
    #print loc_bin.keys();
    steps = 0;
    while sub_prob < cumu_prob_thred:
        steps += 1;
        if steps > 100:
            break;

        #fix the lat, increase lon
        for i in range(left, right):
            index = str(up) + '.0' + '_' + str(i) + '.0';
            #print index;
            if index in loc_bin:
                sub_prob += loc_bin[index];
            
            index = str(down) + '.0' + '_' + str(i) + '.0';
            if index in loc_bin:
                sub_prob += loc_bin[index];
        
        for i in range(down, up):
            index = str(left) + '.0' + '_' + str(i) + '.0';
            if index in loc_bin:
                sub_prob += loc_bin[index];
            
            index = str(right) + '.0' + '_' + str(i) + '.0';
            if index in loc_bin:
                sub_prob += loc_bin[index];

        left -= 1;
        right += 1;
        up += 1;
        down -= 1;

    #gen the square window
    width = right - left;
    square_window['mu'] = [lat, lon];
    square_window['width'] = width;
    square_window['weight'] = cumu_prob_thred/float(width);
    square_window['out_weight'] = 0.001;
   
    #gen the gauss window
    sigma = (right - left)/2; #cdf(mu, sigma) ~= 68%
    gauss_window['mu'] = [lat, lon];
    gauss_window['sigma'] = sigma;
    #for time in range(0, max_time):
    #    #gauss_window[theta][time] = gaussProb([mu, sigma], time);
    #    gauss_window[theta][time] = scipy.stats.norm.cdf(time, mu, sigma) - scipy.stats.norm.cdf(time-1, mu, sigma); 
    
    return square_window, gauss_window;

def getSquareFilterTmpLocDis(term_dis, window, clusters):
    new_term_dis = {};
    for cluster_index, cluster in clusters.iteritems():
        cluster_index = int(cluster_index);
        for term in cluster:
            new_dis = {};
            tmp_loc_dis = term_dis[term];
            for tmp, loc_dis in tmp_loc_dis.iteritems():
                if len(window[cluster_index][tmp]) <= 0:
                    break;
                [lat_mu, lon_mu] = window[cluster_index][tmp]['mu'];
                width = window[cluster_index][tmp]['width'];
                new_dis[tmp] = {};
                for loc, fre in loc_dis.iteritems():
                    [lat, lon] = loc.split('_');
                    lat = int(float(lat));
                    lon = int(float(lon));
                    
                    if abs(lat - lat_mu) < width and abs(lon - lon_mu) < width:
                        new_dis[tmp][loc] = fre;
                    else:
                        new_dis[tmp][loc] = fre*0.1;
                
            normTimeLocs(new_dis);
            new_term_dis[term] = new_dis;
    
    return new_term_dis;
 
def getGaussFilterTmpLocDis(term_dis, window, clusters):
    new_term_dis = {};
    for cluster_index, cluster in clusters.iteritems():
        cluster_index = int(cluster_index);
        for term in cluster:
            new_dis = {};
            tmp_loc_dis = term_dis[term];
            for tmp, loc_dis in tmp_loc_dis.iteritems():
                new_dis[tmp] = {};
                if len(window[cluster_index][tmp]) <= 0:
                    break;
                [lat_mu, lon_mu] = window[cluster_index][tmp]['mu'];
                sigma = window[cluster_index][tmp]['sigma'];
                for loc, fre in loc_dis.iteritems():
                    [lat, lon] = loc.split('_');
                    lat = int(float(lat));
                    lon = int(float(lon));
                    dis = (lat-lat_mu)**2 + (lon-lon_mu)**2;
                    dis = dis**0.5;
                    mu = lat_mu;
                    dis = mu + dis;
                    pro = scipy.stats.norm.cdf(dis, mu, sigma) - scipy.stats.norm.cdf(dis-1, mu, sigma); 
                    
                    new_dis[tmp][loc] = fre*pro;
   
            normTimeLocs(new_dis);
            new_term_dis[term] = new_dis;
    
    return new_term_dis;
   
def getSquareFilterLocDis(term_dis, window, clusters):
    new_term_dis = {};
    for cluster_index, cluster in clusters.iteritems():
        cluster_index = int(cluster_index);
        [lat_mu, lon_mu] = window[cluster_index]['mu'];
        width = window[cluster_index]['width'];
        for term in cluster:
            new_term_dis[term] = {};
            loc_dis = term_dis[term];
            for loc, fre in loc_dis.iteritems():
                [lat, lon] = loc.split('_');
                lat = int(float(lat));
                lon = int(float(lon));
                
                if abs(lat - lat_mu) < width and abs(lon - lon_mu) < width:
                    new_term_dis[term][loc] = fre;
                else:
                    new_term_dis[term][loc] = fre*0.1;
            
            normalizeDic(new_term_dis[term]);
    return new_term_dis;

def getGaussFilterLocDis(term_dis, window, clusters):
    new_term_dis = {};
    print window;
    for cluster_index, cluster in clusters.iteritems():
        cluster_index = int(cluster_index);
        [lat_mu, lon_mu] = window[cluster_index]['mu'];
        sigma = window[cluster_index]['sigma'];
        for term in cluster:
            new_term_dis[term] = {};
            loc_dis = term_dis[term];
            for loc, fre in loc_dis.iteritems():
                [lat, lon] = loc.split('_');
                lat = int(float(lat));
                lon = int(float(lon));
                dis = (lat-lat_mu)**2 + (lon-lon_mu)**2;
                dis = dis**0.5;
                mu = lat_mu;
                dis = mu + dis;
                pro = scipy.stats.norm.cdf(dis, mu, sigma) - scipy.stats.norm.cdf(dis-1, mu, sigma); 
                
                new_term_dis[term][loc] = fre*pro;
            
            normalizeDic(new_term_dis[term]);
    return new_term_dis;
