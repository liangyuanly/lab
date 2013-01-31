#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import sys
import numpy
import copy
from copy import deepcopy
from scipy import *

sys.path.append('../../utility/')
from common import *
from boundingBox import *
from loadFile import *
from kmeans import *
from evaluate import *
from graphOfTokens import disOfTerm, disOfTimeGeo, transPoints, disOfTemp2, transTimePoints 
from termEventCommon import *
#from filterType import meanFilterTimeLocs
from filterType import *

def normMatrix(matrix):
    sum = 0.0
    for x, list in matrix.iteritems():
        for y, value in list.iteritems():
            sum += value;
    
    for x, list in matrix.iteritems():
        for y, value in list.iteritems():
            if sum == 0:
                matrix[x][y] = 0
            else:
                matrix[x][y] /= sum;

def allocMatrix(x_num, y_num, value=0):
    matrix = {};
    for i in range(0, x_num):
        matrix[i] = {};
        for j in range(0, y_num):
            matrix[i][j] = value;
    return matrix

def transClassLabel(clusters):
    cluster_label = {};
    for index, cluster in clusters.iteritems():
        for term in cluster:
            cluster_label[term] = index;

    return cluster_label;

def purityWrap(clusters, truth_file, format, dis_matrix):
    outfilename = 'output//cluster_temp.txt'
    outfile = file(outfilename, 'w');
    for key, tokens in clusters.iteritems():
        for token in tokens:
            outfile.write(token.encode('utf-8')+'\t');
        outfile.write('\n\n');
    outfile.close();

    puri = purityFunc(truth_file, outfilename, format);
    accu = K_NN(dis_matrix, truth_file, 1, format)
    
    return puri, accu;

def indexKey(term_time_locs):
    min_datetime = datetime.datetime(2030, 1, 1);
    for term, time_locs in term_time_locs.iteritems():
        for time, locs in time_locs.iteritems():
            time = strTimeToDatetime(time, '%Y-%m-%d');
            if time < min_datetime:
                min_datetime = time;
    
    for term, time_locs in term_time_locs.iteritems():
        #print term, time_locs.keys()
        for time in time_locs.keys():
            date_time = strTimeToDatetime(time, '%Y-%m-%d');
            day = (date_time - min_datetime).days;
            locs_temp = deepcopy(time_locs[time]);
            del time_locs[time];
            time_locs[day] = locs_temp;

def initClusters(event, cluster_num, format, init_method, sel_terms):
    dirname = 'data/event/' + event 

    if init_method == 'coocur':
        print 'coocur initialization!'
        filename = dirname + '/term_coocurence.txt'
        infile = file(filename);
        if format == 'utf-8':
            dis_matrix = json.load(infile, format);
        else:
            dis_matrix = json.load(infile);
    else: 
        filename = dirname + '/term_time.txt'
        dis_matrix = disOfTemp(filename, 'abs', 'hour');
    
    disMatrixFilter(dis_matrix, sel_terms)
    clusters, centers = kmeansTokens(dis_matrix, cluster_num);
   
    #change the key of the cluster
    new_cluster = {};
    index = 1;
    for key, list in clusters.iteritems():
        new_cluster[index] = list;
        index += 1;

    return new_cluster, centers

##this function is used to calculate the p(theta|t, l) p(t, l|theta)
#def getTimeLocThetaProb(clusters, term_time_locs, event_num):
#    #normalize term_time
#    for term, time_locs in term_time_locs.iteritems():
#        normMatrix(time_locs);
#    
#    theta_locs = {};
#    for cluster_idx, cluster in clusters.iteritems():
#        theta_locs[cluster_idx] = allocMatrix(x_num, y_num);
#
#        for token in cluster:
#            if token not in term_locs.keys():
#                continue;
#            locs = term_locs[token];
#            for x, list in locs.iteritems():
#                for y, fre in list.iteritems():
#                    theta_locs[cluster_idx][x][y] = theta_locs[cluster_idx][x][y] + fre;
#
#    #cal p(l|theta)
#    for clustetr_idx, locs in theta_locs.iteritems():
#        normMatrix(locs);  #notice: the time_fre is changed in the normalizeDic function
#
#    return theta_locs;
#
##this function is used to calculate the p(theta|t) p(t|theta)
#def getLocThetaProb(clusters, term_locs, event_num):
#    #normalize term_time
#    for term, locs in term_locs.iteritems():
#        normMatrix(locs);
#        x_num = len(locs);
#        y_num = len(locs[1])
#    
#    theta_locs = {};
#    for cluster_idx, cluster in clusters.iteritems():
#        theta_locs[cluster_idx] = allocMatrix(x_num, y_num);
#
#        for token in cluster:
#            if token not in term_locs.keys():
#                continue;
#            locs = term_locs[token];
#            for x, list in locs.iteritems():
#                for y, fre in list.iteritems():
#                    theta_locs[cluster_idx][x][y] = theta_locs[cluster_idx][x][y] + fre;
#
#    #cal p(l|theta)
#    for clustetr_idx, locs in theta_locs.iteritems():
#        normMatrix(locs);  #notice: the time_fre is changed in the normalizeDic function
#
#    return theta_locs;

def getDimen(theta_locs):
    for theta, locs in theta_locs.iteritems():
        #normMatrix(locs);
        x_num = len(locs);
        y_num = len(locs[1])
        return x_num, y_num

def getThetaWeightProb(clusters, term_time, event_num):
    prob_theta_time = {}

    cluster_fre = {};
    max_time = 0;
   
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

                if time > max_time:
                    max_time = time;

    max_time += 1;

    #cal p(theta|t)
    for cluster_idx, cluster in clusters.iteritems():
        for term in cluster:
            #p(theta|t)
            for time in range(0, max_time):
                sum_fre = 0.0;
                prob_theta_time[time] = {};
                for j in range(1, event_num+1):
                    if time in cluster_fre[j]:
                        sum_fre += cluster_fre[j][time];

                for j in range(1, event_num+1):
                    if time in cluster_fre[j]:
                        prob_theta_time[time][j] = cluster_fre[j][time] / sum_fre;
                    else:
                        prob_theta_time[time][j] = 0;
    
    #cal p(t|theta)
    prob_time_theta = cluster_fre;
    for clustetr_idx, time_fre in prob_time_theta.iteritems():
        normalizeDic(time_fre);  #notice: the time_fre is changed in the normalizeDic function

    return prob_theta_time, prob_time_theta;

def getNewWordDis(word_theta_prob, cluster):
    word_loc_dis = {};
    for theta, word_locs_prob in word_theta_prob.iteritems():
        word_list = cluster[theta];
        for word, locs in word_locs_prob.iteritems():
            if word in word_list:
                word_loc_dis[word] = locs;
    return word_loc_dis;

def wordThetaProb(term_locs, theta_prob, theta_num):
    x_num, y_num = getDimen(term_locs);
    word_theta_prob = {};
    for theta in range(1, theta_num+1):
        word_theta_prob[theta] = {};

        for term, locs in term_locs.iteritems():
            word_theta_prob[theta][term] = allocMatrix(x_num, y_num, 0);
            
            for x in range(0, x_num):
                for y in range(0, y_num):
                    prob = theta_prob[theta][x][y];
                    word_theta_prob[theta][term][x][y] += locs[x][y]*prob;

    for theta, word_locs in word_theta_prob.iteritems():
        for word, locs in word_locs.iteritems():
            normMatrix(locs);

    return word_theta_prob;

#the term_time_locs changes when this function is called
def getWordTimeLocs2(term_time_locs_in, theta_prob, clusters):
    term_time_locs = deepcopy(term_time_locs_in)
    for cluster_index, cluster in clusters.iteritems():
        for term in cluster:
            time_locs = term_time_locs[term];
            #use the time window
            for time, locs in time_locs.iteritems():
                prob_loc = theta_prob[cluster_index][time];
                for loc_index in locs:
                    prob = prob_loc[loc_index];
                    locs[loc_index] *= prob

            normTimeLocs(time_locs);
    return term_time_locs

#the term_time_locs changes when this function is called
def getWordTimeLocs(term_time_locs_in, theta_prob, clusters):

    #return meanFilterTimeLocs(term_time_locs_in, clusters)

    term_time_locs = deepcopy(term_time_locs_in)
    for cluster_index, cluster in clusters.iteritems():
        for term in cluster:
            time_locs = term_time_locs[term];
            #use the time window
            prob_time = theta_prob[cluster_index];
            for time, locs in time_locs.iteritems():
                prob = prob_time[time];
                for loc_index in locs:
                    locs[loc_index] *= prob

            normTimeLocs(time_locs);
    return term_time_locs


def postIter(term_time_locs, pre_clusters, centers, cluster_num, truth_file, out_theta_file):
    isChanging = True;
    pre_puri = 0;
    iter = 1;
    
    #use the co-occur cluster the gen the theta prob
    #term_day_time = getTimeProbFromTimeLoc(term_time_locs)
    #theta_prob = getThetaTimeProb2(pre_clusters, term_day_time, cluster_num)
    theta_prob = getThetaTimeLocProb(pre_clusters, term_time_locs, cluster_num);
    print 'theta prob init over'
    
    ret_puri = 0;
    ret_accu = 0;
    while isChanging:
        ############use the probability window
        #get the new theta prob
        #word_theta_prob = wordThetaProb(term_prob, theta_prob, cluster_num);

        #use previous cluster lable to re-calculate the distance
        #word_locs_dis = getNewWordDis(word_theta_prob, pre_clusters)
        word_time_locs =  getWordTimeLocs2(term_time_locs, theta_prob, pre_clusters);
        print 'iter=', iter, 'new time locs cal over'

        dis_matrix = disOfTimeGeo(word_time_locs, 'abs');
        print 'iter=', iter, 'new dis matrix cal over'
        clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, centers)
        print 'iter=', iter, 'cluster over'

        puri,accu = purityWrap(clusters, truth_file, format, dis_matrix)
        print 'iter=', iter, 'the post prob window puri=, accu', puri, accu;
        #ret_puri = puri;

        ###########control when to exit the iteration
        #if not change a lot compare with the previous cluster
        cluster_label = transClassLabel(pre_clusters)
        temp_puri = purity(cluster_label, clusters);
        
        print 'not changing rate=', puri
        if temp_puri >= 1 or iter >= 5:
            isChanging = 0;
            if iter == 1:
                ret_puri = puri;
                ret_accu = accu;
        else:
            pre_clusters = clusters;
            pre_puri = puri;
            ret_puri = puri;
            ret_accu = accu;

        #print clusters;
       
        ###############re-calculate the new theta prob
        theta_prob = getThetaTimeLocProb(clusters, term_time_locs, cluster_num); 
        
        json.dump(theta_prob, out_theta_file);
        out_theta_file.write('\n');
        
        iter += 1;
        
        print 'post', 'iter=', iter, 'new the prob cal over'

    return ret_puri, ret_accu;

def genTestWindow(window):
    for theta, time_bin in window.iteritems():
        for time, fre in time_bin.iteritems():
            window[theta][time] = 0;

        window[theta][10] = 1;
        window[theta][11] = 1;
        window[theta][12] = 0.5;
    return window;

def windowIter(term_time_locs, pre_cluster, centers, cluster_num, truth_file, out_theta_file, window_type):
    isChanging = True;
    pre_puri = 0;
    iter = 1;
    ret_puri = 0;
    #use the co-occur cluster the gen the theta prob
    #term_day_time = getTimeProbFromTimeLoc(term_time_locs)
    
    theta_prob = getThetaTimeLocProb(pre_cluster, term_time_locs, cluster_num)
    while isChanging:
        #############use the square window
        square_window, gauss_window = tmpLocWindowFilter(theta_prob);
        print square_window, '\n', gauss_window

        ############use the probability window
        #use previous cluster lable to re-calculate the distance
        #word_locs_dis = getNewWordDis(word_theta_prob, pre_cluster)
        if window_type == 'gauss':
            word_time_locs = getGaussFilterTmpLocDis(term_time_locs, gauss_window, pre_cluster);
        else:
            word_time_locs = getSquareFilterTmpLocDis(term_time_locs, square_window, pre_cluster);
        
        dis_matrix = disOfTimeGeo(word_time_locs, 'abs');
        clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, centers)
        
        puri, accu = purityWrap(clusters, truth_file, format, dis_matrix)
        print 'iter=', iter, window_type, 'puri=', puri, 'accu=', accu;
        #ret_puri = puri;
        ###########control when to exit the iteration
        #if not change a lot compare with the previous cluster
        cluster_label = transClassLabel(pre_cluster)
        temp_puri = purity(cluster_label, clusters);
        
        print 'not changing rate=', puri
        if temp_puri >= 1 or iter >= 5:
            isChanging = 0;
            if iter == 1:
                ret_puri = puri;
                ret_accu = accu;
        else:
            pre_cluster = clusters;
            pre_puri = puri;
            ret_puri = puri;
            ret_accu = accu;

        #print clusters;
       
        ###############calculate the new theta prob
        theta_prob = getThetaTimeLocProb(clusters, term_time_locs, cluster_num); 
        json.dump(theta_prob, out_theta_file);
        out_theta_file.write('\n');
        
        iter += 1;
    
        print window_type
    return ret_puri, ret_accu;

def disOfGeo(term_locs, method, use_kernel=0, bydegree=0):
    #put the positions of terms into bins, 0 means no kernel, 1 means use kernel
    term_matrix = transPoints(term_locs, use_kernel, map, bydegree);
    
    #cal the distance between each pair of terms
    dis_matrix = disOfTerm(term_matrix, method);

def filterTerms(term_dic, term_list):
    for term in term_dic.keys():
        if term not in term_list:
            del term_dic[term];

def iterThetaWordLoc(event, cluster_num, format, use_kernel, map, bydegree):
    #first use the co-occur as the metric to cluster tokens
    prob_theta_time = {};
    prob_word_theta = {};
    out_puri = {};
    
    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
 
    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_time = json.load(infile);
    filterTerms(term_time, label);
    infile.close();
 
    filename = 'data/event/' + event + '/term_time_geo.txt';
    infile = file(filename);
    term_locs = json.load(infile);
    infile.close();
    filterTerms(term_locs, label);
    term_time_locs = transTimePoints(term_locs, use_kernel, map, bydegree, 100);
    indexKey(term_time_locs);
    
    if use_kernel == 1:
        meanFilterTimeLocs(term_time_locs);
    print 'mean filter time locs over'

    theta_file = 'data/event/' + event + '/iter_theta_prob.txt';
    out_theta_file = file(theta_file, 'w');
    
    #use co-occur init the cluster
    pre_clusters, centers = initClusters(event, cluster_num, format, 'coocur', label);
    #json.dump(theta_prob, out_theta_file);
    #out_theta_file.write('\n');
    
    #use the geo-spatial distance to cluster, for comparison
    dis_matrix = disOfTimeGeo(term_time_locs, 'abs')
    center_temp = deepcopy(centers);
    clusters_temp, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, center_temp)
    #print clusters
    puri, accu = purityWrap(clusters_temp, truth_file, format, dis_matrix)
    out_puri['temp_spa'] = puri;
    out_puri['temp_spa_accuracy'] = accu;
 
    #post probability iteration
    #theta_prob_temp = deepcopy(theta_prob);
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    out_puri['temp_spa_post'], out_puri['temp_spa_post_accuracy']= postIter(term_time_locs, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file)
    
    return out_puri;

    #sqaure probability iteration
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    out_puri['temp_spa_square'], out_puri['temp_spa_square_accuracy'] = windowIter(term_time_locs, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, 'square')
 
    #gauss probability iteration
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    out_puri['temp_spa_gauss'], out_puri['temp_spa_gauss_accuracy'] = windowIter(term_time_locs, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, 'gauss')
    
    return out_puri;

def termThetaCluterMain():
    event = 'irene_overall'
    cluster_num = 3;
    bb = getUSbb()
    use_kernel = 1;
    termThetaCluster(event, cluster_num, bb, use_kernel);
 
    event = '3_2011_events'
    cluster_num = 5;
    bb = getUSbb()
    use_kernel = 1;
    termThetaCluster(event, cluster_num, bb, use_kernel);
 
    event = '8_2011_events'
    cluster_num = 5;
    bb = getUSbb()
    use_kernel = 1;
    termThetaCluster(event, cluster_num, bb, use_kernel);
    
    event = 'jpeq_jp'
    cluster_num = 5;
    bb = getJPbb()
    use_kernel = 1;
    termThetaCluster(event, cluster_num, bb, use_kernel);

def termThetaCluster(event, cluster_num, bb, use_kernel):
    byDegree = 0;
    format = 'utf-8'
    
    final_puri = {};
    iter_num = 1;
    for i in range(0, iter_num):
        puri = iterThetaWordLoc(event, cluster_num, format, use_kernel, bb, byDegree)
        
        print puri;

        for key, f in puri.iteritems():
            if key not in final_puri:
                final_puri[key] = 0;
            final_puri[key] += f;
    for key in final_puri:
        final_puri[key] /= iter_num;
    
    filename = 'data/event/' + event + '/result_tmp_loc.txt';
    outfile = file(filename, 'w');
    json.dump(final_puri, outfile);
    outfile.write('\n');
    outfile.close();

termThetaCluterMain()
