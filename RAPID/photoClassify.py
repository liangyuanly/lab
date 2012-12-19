#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
#from scipy import *
import scipy
import random
import fnmatch

sys.path.append('../utility/')
#sys.path.append('../media/earthquake/')
from boundingBox import *
from loadFile import *
from common import *
from tokenization import *
#from graphOfTokens import disOfTerm, transPoints, disOfTemp2 

def transPoints(term_loc, useKernel, bb, useDegree=0):
    term_matrix = {};
    lat_num = 100;
    lon_num = 100;
    if useDegree == 1:
        lat_num = math.ceil(bb[1] - bb[0]);
        lon_num = math.ceil(bb[3] - bb[2]);

    for term, locs in term_loc.iteritems():
        matrix = allocMatrix(lat_num + 2, lon_num + 2);
        for loc in locs:
            lat = loc[0];
            log = loc[1];
            lati_index, longi_index = getIndexForbb(lat, log, bb, lat_num, lon_num);
            if lati_index > 0 and longi_index > 0:
                matrix[lati_index][longi_index] = matrix[lati_index][longi_index] + 1;

        if useKernel == 1:
            kernelGeoDis(matrix);

        norMatrix(matrix);
        term_matrix[term] = matrix;
    return term_matrix;

#this function is used to calculate the p(theta|t) p(t|theta)
def getThetaTimeProb(clusters, term_one_place_time, event_num):
    prob_theta_time = {}
    cluster_fre = {};
   
    #normalize term_time
    for term, time_bin in term_one_place_time.iteritems():
        normalizeDic(time_bin);

    for cluster_idx, cluster in clusters.iteritems():
        if cluster_idx not in cluster_fre.keys():
            cluster_fre[cluster_idx] = {};

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
def getThetaLocProb(clusters, term_locs, event_num):
    #normalize term_time
    for term, locs in term_locs.iteritems():
        normMatrix(locs);
        x_num = len(locs);
        y_num = len(locs[1])
    
    theta_locs = {};
    for cluster_idx, cluster in clusters.iteritems():
        theta_locs[cluster_idx] = allocMatrix(x_num, y_num);

        for token in cluster:
            if token not in term_locs.keys():
                continue;
            locs = term_locs[token];
            for x, list in locs.iteritems():
                for y, fre in list.iteritems():
                    theta_locs[cluster_idx][x][y] = theta_locs[cluster_idx][x][y] + fre;

    #cal p(l|theta)
    for clustetr_idx, locs in theta_locs.iteritems():
        normMatrix(locs);  #notice: the time_fre is changed in the normalizeDic function

    return theta_locs;

def loadTruthCluster(truth_file):
    #truth_file = 'data/event//truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, 'utf-8');

    #manually label these clusters
    new_cluster = {};
    new_cluster['congest'] = true_clusters[1];
    new_cluster['refuge'] =  true_clusters[2];
    new_cluster['fire'] = true_clusters[3];
    #new_cluster['earthquake'] = true_clusters[4];
    return new_cluster;

def loadImageInfo(dirname):
    all_images = [];
    image_cluster = {};
    dirs = os.listdir(dirname);
    for adir in dirs:
        image_cluster[adir] = [];
        path = dirname + adir + '/';
        filename = path + 'ImageInfo.txt';
        infile = file(filename);
        lines = infile.readlines()
        for i in range(0, len(lines), 2):
            info = json.loads(lines[i])
            image_cluster[adir].append(info['id']);
            all_images.append(info);

    return all_images, image_cluster;

def getTermClusterFeatures(true_cluster, term_time, term_locs):
    theta_time = getThetaTimeProb(true_cluster, term_time, len(true_cluster));
    theta_loc = getThetaLocProb(true_cluster, term_locs, len(true_cluster));

    outfile = file('data/event/jpeq_jp/theta_time.txt', 'w')
    json.dump(theta_time, outfile);
    outfile.close();

    return theta_time, theta_loc;

def accuracy(true_cluster, image_cluster):
    accu_count = 0.0;
    sum_count = 0.0;
    for cluster_idx, cluster in image_cluster.iteritems():
        true_clu = true_cluster[cluster_idx];
        for image in cluster:
            sum_count += 1;
            if image in true_clu:
                accu_count += 1;
    return accu_count / sum_count;

def photoClassifyUsingTerms(all_image, term_cluster):
    image_cluster = {};
    for image in all_image:
        text = image['text'];
        simi = {};
        for cluster_idx, terms in term_cluster.iteritems():
            simi[cluster_idx] = 0;
            for term in terms:
                if similarityCal(term, text) > 0:
                #if similarity4(text, term) > 0:
                    simi[cluster_idx] += 1;
        max_simi = 0;
        sel_cluster = cluster_idx; #use the last one as the default class
        for cluster_idx, similarity in simi.iteritems():
            if similarity > max_simi:
                max_simi = similarity;
                sel_cluster = cluster_idx

        if sel_cluster not in image_cluster.keys():
            image_cluster[sel_cluster] = [];

        image_cluster[sel_cluster].append(image['id']);
    return image_cluster;

def findClosestPoint(loc_index, locs):
    p = loc_index[0];
    q = loc_index[1];
    min_dis = 100000;
    prob = 0;
    for i in range(0, len(loc_index)):
        for j in range(0, len(loc_index[0])):
            if loc_index[i][j] > 0:
                dis = (i-p)**2 + (j-q)**2;
                dis = dis**0.5;
                if dis < min_dis:
                    min_dis = dis;
                    prob = loc_index[i][j]

    prob = prob/float(min_dis);
    return prob;

def photoClassifyUsingTimeLoc(all_image, cluster_time, cluster_loc, begin_time, boundingbox):
    image_cluster = {};
    for image in all_image:
        time = image['time'];
        loc = image['corrdinate'];
        time = tweetTimeToDatetime(time)
        time_index = getIndexForTime(time, begin_time);
        loc_index = getIndexForbb(loc[0], loc[1], boundingbox, 100, 100)
        print loc, loc_index

        max_prob = 0;
        prob_cluster = {};
        for cluster_index, time_bin in cluster_time.iteritems():
            #print 'image-cluster', image, cluster_index;
            prob = 0;
            if time_index in time_bin.keys():
                prob = time_bin[time_index];
            else:  # use the nearest one to approximate it
                print 'in temporal domain, should not happen'
            
            prob2 = 0;
            locs = cluster_loc[cluster_index]
            if loc_index[0] in locs.keys():
                if loc_index[1] in locs[loc_index[0]].keys():
                    prob2 = locs[loc_index[0]][loc_index[1]];

            if prob2 == 0:
                #use the nearest one to appoximate the prob
                prob2 = findClosestPoint(loc_index, locs)

            prob_cluster[cluster_index] = prob*prob2;

        max_simi = 0;
        sel_cluster = cluster_index; #use the last one as the default class
        for cluster_idx, similarity in prob_cluster.iteritems():
            if similarity > max_simi:
                max_simi = similarity;
                sel_cluster = cluster_idx

        if sel_cluster not in image_cluster.keys():
            image_cluster[sel_cluster] = [];

        image_cluster[sel_cluster].append(image['id']);
    return image_cluster;

def photoClassifyMain():
    truth_file = 'data/event/jpeq_jp/truth_cluster_3.txt';
    true_cluster = loadTruthCluster(truth_file);
    
    bb, tt = getbbtt('jpeq_jp'); 
    tt = transTime(tt);
    
    time_file = 'data/event/jpeq_jp/term_time.txt';
    infile = file(time_file);
    term_time = json.load(infile);
    infile.close();

    loc_file = 'data/event/jpeq_jp/term_location.txt';
    infile = file(loc_file);
    term_loc = json.load(infile);
    term_loc = transPoints(term_loc, 0, bb);
    infile.close();

    #get the temporal-spatial dis for clusters
    cluster_time, cluster_loc = getTermClusterFeatures(true_cluster, term_time, term_loc)
    
    image_folder = 'data/event/jpeq_jp/cluster_3/';
    all_image, image_cluster = loadImageInfo(image_folder);
    print image_cluster;

    cluster_term = photoClassifyUsingTerms(all_image, true_cluster);
    print cluster_term;
    accu = accuracy(image_cluster, cluster_term); 
    print 'accuracy using cosine similarity', accu;

    cluster_tl = photoClassifyUsingTimeLoc(all_image, cluster_time, cluster_loc, tt[0], bb);
    print cluster_tl
    accu = accuracy(image_cluster, cluster_tl); 
    print 'accuracy using temp-spatial similarity', accu;

photoClassifyMain();
