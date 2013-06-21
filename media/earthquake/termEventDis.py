#!/usr/bin/pythoni
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

gauss_func = lambda p, x: (1/(sqrt(2*pi)*p[1])) * exp(-(x-p[0])**2/(2*p[1]**2))
gauss_err_func = lambda p, x, y: gauss_func(p, x) - y

global g_selected_words

def plotthetatime(theta_time, name):
    return
#    for theta_index, time_bin in theta_time.iteritems():
#        x_list = [];
#        y_list = [];
#
#        keylist = time_bin.keys();
#        for i in range(0, len(keylist)):
#            keylist[i] = int(keylist[i]);
#        keylist.sort();
#
#        for i in range(0, len(keylist)):
#            time_index = keylist[i];
#            if time_index > 24*30*60:
#                break;
#            freq = time_bin[time_index];
#            x_list.append(time_index);
#            y_list.append(freq);
#        
#        plt.plot(x_list, y_list);
#    plt.title(name);
#    plt.xlabel('Time (Hour)');
#    plt.ylabel('Probability');
#    plt.show();

def plotTimeDis(time_bin, name):
    return
#    sel_names = ['apple', 'tornado', 'thunderstorm', 'issued'];
#    if name in sel_names:
#        x_list = [];
#        y_list = [];
#
#        keylist = time_bin.keys();
#        for i in range(0, len(keylist)):
#            keylist[i] = int(keylist[i]);
#        keylist.sort();
#
#        for i in range(0, len(keylist)):
#            time_index = keylist[i];
#            if time_index > 24*30*60:
#                break;
#            if time_index in time_bin:
#                freq = time_bin[time_index];
#            else:
#                freq = time_bin[str(time_index)];
#
#            x_list.append(time_index);
#            y_list.append(freq);
#        
#        plt.xlabel('Time (Hour)');
#        plt.ylabel('Probability');
#        plt.plot(x_list, y_list);
#        plt.title(name);
#        plt.show();

def gaussFit(data):
    sum_all = 0;
    for x in data:
        sum_all += int(x);

    mu = sum_all/len(data);
    sigmal_all = 0;
    for x in data:
        sigmal_all = sigmal_all + (int(x) - mu)**2;
    sigmal_all = sigmal_all / float(len(data));
    sigma = sqrt(sigmal_all);
    
    return mu, sigma;

def gaussProb(model, x):
    mu = model[0];
    sigma = model[1];
    return (1/(numpy.sqrt(2*numpy.pi)*sigma)) * numpy.exp(-(x-mu)**2/(2*sigma**2))

def loadTermTime(filename):
    infile = file(filename);
    term_time = json.load(infile);
    infile.close();

    for term, bins in term_time.iteritems():
        sum = 0;
        for time, freq in bins.iteritems():
            sum += freq;

        for time, freq in bins.iteritems():
            term_time[term][time] = freq/float(sum);

    return term_time;

def loadEventProb(filename):
    infile = file(filename);
    lines = infile.readlines();
    event_prob = {};
    index = 0;
    for line in lines:
        prob = json.loads(line);
        event_prob[index] = prob;
        index += 1;

    return event_prob;

def getEventProb(filename, hours):
    infile = file(filename);
    lines = infile.readlines();
    infile.close();

    model = {};
    #gauss model
    para = json.loads(lines[0]);
    for event_index, pa in para.iteritems():
        event_index = int(event_index)
        model[event_index] = {};
        mu = pa[0];
        sigma = pa[1];
        beg = int(math.floor(mu - sigma));
        end = int(math.ceil(mu + sigma));
        model[event_index]['gauss'] = {};
        for i in range(0, hours):
            prob = gaussProb([mu, sigma], i) 
            model[event_index]['gauss'][i] = prob;

        model[event_index]['square'] = {};
        for i in range(beg, end+1):
            model[event_index]['square'][i] = 1;

    return model;

def gaussNoise(term_prob):
    #use the first two days as the backgroud
    Max_hour = 96;
    bg_noise = {};
    
    for term, time_prob in term_prob.iteritems():
        bg_noise[term] = []

        for time in range(0, Max_hour):
            time = str(time)
            if time in time_prob:
                bg_noise[term].append(time_prob[time]);

        if len(bg_noise[term]) < 10:
            continue;

        mu = scipy.mean(bg_noise[term]);
        sigma = scipy.std(bg_noise[term]);

         #filter the bg noise
        for time, fre in time_prob.iteritems():
            noise = random.gauss(mu, sigma)
            temp = time_prob[str(time)] - noise;
            if temp > 0:
                time_prob[str(time)] = temp;
            else:
                time_prob[str(time)] = 0;


def BGNoiseFilter(term_prob, nr_method):
    return;

    if nr_method == 'gauss':
        return gaussNoise(term_prob)
    
    #use the first two days as the backgroud
    Max_hour = 48;
    bg_noise = {};
    
    for term, time_prob in term_prob.iteritems():
        bg_noise[term] = {}
        for i in range(0, 24):
            bg_noise[term][i] = 0;

        for time in range(0, Max_hour):
            index = time % 24
            time = str(time)
            if time in time_prob:
                bg_noise[term][index] += time_prob[time];
        for i in range(0, 24):
            bg_noise[term][i] /= 2;
    
        #filter the bg noise
        for time, fre in time_prob.iteritems():
            time = int(time)
            index = time % 24;
            temp = time_prob[str(time)] - bg_noise[term][index];
            if temp > 0:
                time_prob[str(time)] = temp;
            else:
                time_prob[str(time)] = 0;

def termWindowProb(time_bin, event_prob):
    term_event_time_dis = {};
        
    for time, freq in time_bin.iteritems():
        time = int(time);
        if time not in event_prob:
            theme_prob = 0;
        else:
            theme_prob = event_prob[time];
        term_event_time_dis[time] = freq * theme_prob;
    
    sum = 0;
    for time, freq in term_event_time_dis.iteritems():
        sum += freq;

    for time, freq in term_event_time_dis.iteritems():
        term_event_time_dis[time] = freq / float(sum);

    return term_event_time_dis;

def termEventProb(term_time, event_prob, tt):
    term_event_time_dis = {};
    for term, time_bin in term_time.iteritems():
        term_event_time_dis[term] = {};
        
        for time, freq in time_bin.iteritems():
            time = float(time);
            dura = int(math.ceil(time / 24));
            year = tt[0][0];
            month = tt[0][1];
            if month < 10:
                month = '0' + str(month);
            else:
                month = str(month);

            day = tt[0][2] + dura;
            key = str(year) + month + str(day);
            theme_prob = event_prob[key];
            
            term_event_time_dis[term][time] = freq * theme_prob;
        
        sum = 0;
        for time, freq in term_event_time_dis[term].iteritems():
            sum += freq;

        for time, freq in term_event_time_dis[term].iteritems():
            term_event_time_dis[term][time] = freq / float(sum);
    
    return term_event_time_dis;

def termThetaDisMain():
    event = '8_2011_events';
    prob_theta_word_time, freq_event = probThetaWordTime(event)
   
    filename = 'data/event/' + event + '/term_time_theta.txt';
    outfile = file(filename, 'w');
    json.dump(freq_event, outfile);
    outfile.close();

def termDisMain():
    #event = 'irene_overall';
    event = '3_2011_events';
    filename = 'data/event/' + event + '/term_time.txt';
    term_prob = loadTermTime(filename);

    bb, tt = getbbtt(event);
    days = tt[0][3] - tt[0][2];
    hours = days * 24 + 1;
    filename = 'data/event/' + event + '/filter_window.txt';
    event_prob = getEventProb(filename, hours);
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename, 'utf-8');
 
    new_term_gauss_freq = {};
    for event_index, cluster in clusters.iteritems():
        theme_prob = event_prob[event_index]['gauss'];
        for token in cluster:
            if token not in term_prob:
                term_prob[token] = {};
                continue;
            term_freq = term_prob[token];
            new_term_freq = termWindowProb(term_freq, theme_prob);
            new_term_gauss_freq[token] = new_term_freq;
    
    new_term_square_freq = {};
    for event_index, cluster in clusters.iteritems():
        theme_prob = event_prob[event_index]['square'];
        for token in cluster:
            term_freq = term_prob[token];
            new_term_freq = termWindowProb(term_freq, theme_prob);
            new_term_square_freq[token] = new_term_freq;
    
    outfilename = 'data/event/' + event + '/term_time_event.txt';
    outfile = file(outfilename, 'w');
    
    json.dump(event_prob, outfile);
    outfile.write('\n');
    
    json.dump(term_prob, outfile);
    outfile.write('\n');
    
    json.dump(new_term_gauss_freq, outfile);
    outfile.write('\n')
    
    json.dump(new_term_square_freq, outfile);
    outfile.write('\n')
    
    outfile.close();

def termEventDis():
    event = 'irene_overall';
    filename = 'data/event/' + event + '/term_time.txt';
    term_prob = loadTermTime(filename);

    filename = 'data/event/' + event + '/theme_prob.txt';
    event_prob = loadEventProb(filename);
    cluster_num = 3;
    bb,tt = getbbtt(event);

    event_term_time_dis = {};
    count = 0;
    for event_index, prob in event_prob.iteritems():
        event_term_time_dis[event_index] = termEventProb(term_prob, prob, tt);
        count += 1;
        if count >= cluster_num:
            break;

    outfilename = 'data/event/' + event + '/term_time_event.txt';
    outfile = file(outfilename, 'w');
    json.dump(term_prob, outfile);
    outfile.write('\n');
    
    for event_index, dis in event_term_time_dis.iteritems():
        json.dump(event_term_time_dis[event_index], outfile);
        outfile.write('\n')
    outfile.close();

def genGaussWindow(event):
    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    #term_prob = loadTermTime(filename);
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename);

    #build a gaussian for each cluster
    model = {};
    for cluster_index, cluster in clusters.iteritems():
        data = [];
        model[cluster_index] = [];
        for token in cluster:
            token = unicode(token, 'utf-8')
            if token not in term_prob:
                term_prob[token] = {};
                continue;
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                for i in range(0, freq):
                    data.append(time);

        model[cluster_index] = gaussFit(data);

    return model;

def genSquareWindow(event):
    #use gauss window
    return genGaussWindow(event);
    
    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename);
    
    #build a gaussian for each cluster
    model = {};
    cluster_time = {};
    for cluster_index, cluster in clusters.iteritems():
        model[cluster_index] = [];
    
        max_time = 0;
        for token in cluster:
            token = unicode(token, 'utf-8')
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);

                if time > max_time:
                    max_time = time;

        max_time += 1;
        cluster_freq = [0 for i in range(0, max_time)];
        cluster_time[cluster_index] = cluster_freq;
        
        #cal the freq of the cluster
        for token in cluster:
            token = unicode(token, 'utf-8')
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                cluster_freq[time] += freq;
       
        sum_all = 0;
        max = 0;
        max_index = 0;
        for time in range(0, max_time):
            freq = cluster_freq[time];
            sum_all += freq;
            if freq > max:
                max = freq;
                max_index = time;

        for time in range(0, max_time):
            cluster_freq[time] /= float(sum_all);
        
        #detect the changing point
        for time in range(max_index, 1, -1):
            y_dis = cluster_freq[time] - cluster_freq[time-1];
            if y_dis <= 0:
                break;

        begin_point = time;
        
        #detect the changing point
        for time in range(max_index, max_time):
            y_dis = cluster_freq[time] - cluster_freq[time+1];
            if y_dis <= 0:
                break;

        end_point = time;
        
        model[cluster_index] = [begin_point, end_point]

    return model;

#def genSlewWindow():
def genPosterWindow():
    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename);
    
    model = {};
    cluster_time = {};
    for cluster_index, cluster in clusters.iteritems():
        model[cluster_index] = [];
    
        max_time = 0;
        for token in cluster:
            token = unicode(token, 'utf-8')
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);

                if time > max_time:
                    max_time = time;

        max_time += 1;
        cluster_freq = [0 for i in range(0, max_time)];
        cluster_time[cluster_index] = cluster_freq;
        
        #cal the freq of the cluster
        for token in cluster:
            token = unicode(token, 'utf-8')
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                cluster_freq[time] += freq;
       
        sum_all = 0;
        max = 0;
        max_index = 0;
        for time in range(0, max_time):
            freq = cluster_freq[time];
            sum_all += freq;
            if freq > max:
                max = freq;
                max_index = time;

        for time in range(0, max_time):
            cluster_freq[time] /= float(sum_all);

    return cluster_freq;
 

##p(theta|t) p(t|theta) calculation using weighted words
#def getThetaTimeWeightProb(clusters, term_time, event_num):
#    prob_theta_time = {}
#
#    cluster_fre = {};
#    max_time = 0;
#   
#    #normalize term_time
#    for term, time_bin in term_time.iteritems():
#        normalizeDic(time_bin);
#
#    #event_num = len(clusters)       
#    for i in range(1, event_num+1):
#        cluster_fre[i] = {};
#
#    for cluster_idx, cluster in clusters.iteritems():
#        for token, weight in cluster.iteritems():
#            if token not in term_time:
#                continue;
#            time_bins = term_time[token];
#            for time, freq in time_bins.iteritems():
#                time = int(time);
#                if time not in cluster_fre[cluster_idx]:
#                    cluster_fre[cluster_idx][time] = 0.0;
#
#                cluster_fre[cluster_idx][time] = cluster_fre[cluster_idx][time] + freq*weight;
#
#                if time > max_time:
#                    max_time = time;
#
#    max_time += 1;
#
#    #cal p(theta|t)
#    for cluster_idx, cluster in clusters.iteritems():
#        for term in cluster:
#            #p(theta|t)
#            for time in range(0, max_time):
#                sum_fre = 0.0;
#                prob_theta_time[time] = {};
#                for j in range(1, event_num+1):
#                    if time in cluster_fre[j]:
#                        sum_fre += cluster_fre[j][time];
#
#                for j in range(1, event_num+1):
#                    if time in cluster_fre[j]:
#                        prob_theta_time[time][j] = cluster_fre[j][time] / sum_fre;
#                    else:
#                        prob_theta_time[time][j] = 0;
#    
#    #cal p(t|theta)
#    prob_time_theta = cluster_fre;
#    for clustetr_idx, time_fre in prob_time_theta.iteritems():
#        normalizeDic(time_fre);  #notice: the time_fre is changed in the normalizeDic function
#
#    return prob_theta_time, prob_time_theta;
#
#def getThetaTimeLocationWindow(cluster_fre):
#    #now we have six continues whose are located in (0,1000), (1000, 2000)....(5000, 6000)
#    #now we first find the place has the highest probabilty, then use the time window for this
#    #place as the windows for every cluster
#    new_cluster_fre = {}
#    sum_fre = {}
#    for theta, time_bin in cluster_fre.iteritems():
#        max_fre = 0
#        #then each cluster has the time location demision vector
#        for time, fre in time_bin.iteritems():
#            time = int(time)
#            index = time/1000
#            if index not in new_cluster_fre:
#                new_cluster_fre[index] = {};
#                sum_fre[index] = {}
#            if theta not in new_cluster_fre[index]:
#                new_cluster_fre[index][theta] = {};
#                sum_fre[index][theta] = 0;
#            new_cluster_fre[index][theta][time] = fre;
#            sum_fre[index][theta] += fre;
#    
#    all_gauss_window = {};
#    all_square_window = {};
#    for index, theta_time_bin in new_cluster_fre.iteritems():
#        for theta, time_bin in theta_time_bin.iteritems():
#            for time, fre in time_bin.iteritems():
#                if sum_fre[index][theta] != 0:
#                    time_bin[time] /= sum_fre[index][theta];
#        square_window, gauss_window = getThetaTimeWindow(theta_time_bin);
#        #print 'cal square, gauss window over for continent', index
#        all_gauss_window.update(gauss_window)
#        all_square_window.update(square_window)
#
#    return all_square_window, all_gauss_window
#
##this function is used to calculate the filtering window p(t|theta)
##the windows can be gaussian, square, triangle, etc
##cluster_fre is theta_prob
#def getThetaTimeWindow(cluster_fre):
#    max_time = 0.0;
#    for theta, time_bin in cluster_fre.iteritems():
#        for time, fre in time_bin.iteritems():
#            if time > max_time:
#                max_time = time;
#    max_time += 1;
#
#    square_window = {};
#    gauss_window = {};
#    for theta, time_bin in cluster_fre.iteritems():
#        max_fre = 0;
#        temp_max_time = 0;
#        square_window[theta] = {}; 
#        gauss_window[theta] = {};
#        for time, fre in time_bin.iteritems():
#            if fre > max_fre:
#                max_fre = fre;
#                temp_max_time = time;
#
#        if len(time_bin) <= 0:
#            continue;
#
#        cumu_prob_thred = 0.68;
#        #find the windows which cover 80% probability 
#        sub_prob = time_bin[temp_max_time];
#        left = temp_max_time - 1;
#        right = temp_max_time + 1;
#        while sub_prob < cumu_prob_thred:
#            if left in time_bin:
#                sub_prob += time_bin[left];
#            if right in time_bin:
#                sub_prob += time_bin[right];
#
#            left -= 1;
#            right += 1;
#
#        rev_left = left;
#        rev_right = right;
#
#        if left < 0:
#            left = 0;
#        if right > max_time - 1:
#            right = max_time - 1;
#
#        #gen the square window
#        bin_count = right - left;
#        for time in range(0, max_time):
#            if time <= right and time >= left:
#                square_window[theta][time] = cumu_prob_thred/bin_count;
#            else:
#                square_window[theta][time] = 0.1*(1 - cumu_prob_thred) / (max_time - bin_count);
#       
#        #gen the gauss window
#        mu = temp_max_time;
#        sigma = (rev_right - rev_left)/2; #cdf(mu, sigma) ~= 68%
#        for time in range(0, max_time):
#            gauss_window[theta][time] = gaussProb([mu, sigma], time);
#    
#    return square_window, gauss_window;
#
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

def maxMarginInit(dis_matrix, cluster_num, term_prob):
    try_num = 10;
    max_kl = 0;
    for i in range(0, 10):
        clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, [])
        #clusters, centers = kmeansTokens(dis_matrix, cluster_num);
        theta_time_prob, theta_prob = getWeightThetaTimeProb(clusters, centers, term_prob, cluster_num); 
        kl_dis  = KLDivergence(theta_prob);
        if kl_dis > max_kl:
            max_kl = kl_dis;
            sel_cluster = clusters;
            sel_center = centers;

    return sel_cluster, sel_center;

def initClusters(event, cluster_num, term_time, format, init_method, dis_method):
    global g_selected_words

    dirname = 'data/event/' + event 

    #init_method = 'temp'
    if init_method == 'coocur':
        print 'coocur initialization!'
        filename = dirname + '/term_coocurence2.txt'
        infile = file(filename);
        if format == 'utf-8':
            dis_matrix = json.load(infile, format);
        else:
            dis_matrix = json.load(infile);
    else: 
        print 'no other inition yet'
        filename = dirname + '/term_time.txt'
        dis_matrix = disOfTemp(filename, dis_method, 'hour');
    
    dis_matrix = disMatrixFilter(dis_matrix, g_selected_words)
    clusters, centers = kmeansTokens(dis_matrix, cluster_num);
    #test
    #clusters, centers = maxMarginInit(dis_matrix, cluster_num, term_time);

    #change the key of the cluster
    new_cluster = {};
    index = 1;
    for key, list in clusters.iteritems():
        new_cluster[index] = list;
        index += 1;

    #p1, p2 = getThetaTimeProb(new_cluster, term_time, cluster_num)
    return new_cluster, centers

def normalizeList(list):
    sum = 0.0;
    for ele in list:
        sum = sum + ele;
    for i in range(0,len(list)):
        list[i] = list[i]/sum;

def getWordThetaProb(term_time, theta_dis, clusters, filter_type):
    if 'average' in filter_type:
        return averageFilter(term_time, theta_dis, clusters)
    
    word_theta_prob = {};
    term_count = 0;
    for theta, cluster in clusters.iteritems():
        for term in cluster:
            term_count += 1;
            word_theta_prob[term] = {};
            if term not in term_time:
                print 'wried, token not in the keys', term
                term_time[term] = {};
    
    print 'term count for cluster, term count in the time', term_count, len(term_time)
    
    max_time = 0; 
    for theta, cluster in clusters.iteritems():
        for term in cluster:        
            time_bin = term_time[term]
            for time, freq in time_bin.iteritems():
                #time = int(time)
                #if time > max_time:
                #    max_time = time;
                
                #theta_time = time % mod; #if mod is 10000, it's same to no mod, cause we only consider 6 places, so the largest number if 6999
                prob = 0;
                #if time in theta_dis[theta].keys():
                prob = theta_dis[theta][time];
                word_theta_prob[term][time] = freq * prob;
            
            normalizeDic(word_theta_prob[term]);
#    max_time += 1;
#    for word, time_bin in word_theta_prob.iteritems():
#        normalizeDic(time_bin);
#        for time in range(0, max_time):
#            if time not in time_bin.keys():
#                time_bin[time] = 0;

    return word_theta_prob;

##def wordThetaProb(term_time, theta_prob, theta_dis, theta_num, mod=10000):
#    word_theta_prob = {};
#    for theta in range(1, theta_num+1):
#        word_theta_prob[theta] = {};
#
#        for term, time_bin in term_time.iteritems():
#            word_theta_prob[theta][term] = {};
#
#            for time, freq in time_bin.iteritems():
#                time = int(time)
#                theta_time = time % mod; #if mod is 10000, it's same to no mod, cause we only consider 6 places, so the largest number if 6999
#                #print time, theta_time
#                #if theta_time in theta_prob.keys() and theta in theta_prob[theta_time].keys():
#                prob = theta_prob[theta_time][theta];
#                word_theta_prob[theta][term][time] = freq * prob;
#
#    word_theta_prob2 = {};
#    for theta in range(1, theta_num+1):
#        word_theta_prob2[theta] = {};
#
#        for term, time_bin in term_time.iteritems():
#            word_theta_prob2[theta][term] = {};
#
#            for time, freq in time_bin.iteritems():
#                time = int(time)
#                theta_time = time % mod
#                prob = 0;
#                if theta_time in theta_dis[theta].keys():
#                    prob = theta_dis[theta][theta_time];
#                word_theta_prob2[theta][term][time] = freq * prob;
#
#
#    for theta, word_time in word_theta_prob.iteritems():
#        for word, time_bin in word_time.iteritems():
#            normalizeDic(time_bin);
#
#    for theta, word_time in word_theta_prob2.iteritems():
#        for word, time_bin in word_time.iteritems():
#            normalizeDic(time_bin);
#
#    return word_theta_prob, word_theta_prob2;

def findClosestTheta(word_theta_prob, theta_time_prob):
    distance = {};
    for theta, word_time_prob in word_theta_prob.iteritems():
        theta_prob = theta_time_prob[theta];

        for word, time_prob in word_time_prob.iteritems():
            if word not in distance:
                distance[word] = {};

            distance[word][theta] = 0;
            for time, prob in theta_prob.iteritems():
                if time in time_prob:
                    distance[word][theta] += abs(prob-time_prob[time])
                else:
                    distance[word][theta] += prob;

    word_sel_theta = {};
    clusters = {};
    for word, theta_dis in distance.iteritems():
        min_dis = 9999999;
        sel_theta = 0;
        for theta, dis in theta_dis.iteritems():
            if dis < min_dis:
                min_dis = dis;
                sel_theta = theta;
        
        word_sel_theta[word] = sel_theta;
        if sel_theta not in clusters:
            clusters[sel_theta] = [];
        clusters[sel_theta].append(word);

    return word_sel_theta, clusters;

def compare(pre_clusters, clusters):
    isChanging = False;
    for theta, cluster in pre_clusters.iteritems():
        com_cluster = clusters[theta];
        for elm in cluster:
            if elm not in com_cluster:
                isChanging = True;

    return isChanging;

def transferThetaProbForm(time_theta_prob):
    theta_time_prob = {};
    for time, theta_prob in time_theta_prob.iteritems():
        for theta, prob in theta_prob.iteritems():
            if theta not in theta_time_prob:
                theta_time_prob[theta] = {};

            theta_time_prob[theta][time] = prob;

    return theta_time_prob

def getNewWordTimeDis(word_theta_prob, cluster):
    word_time_dis = {};
    for theta, word_time_prob in word_theta_prob.iteritems():
        word_list = cluster[theta];
        for word, time_bin in word_time_prob.iteritems():
            if word in word_list:
                word_time_dis[word] = time_bin;
    return word_time_dis;

#calculate the weights that a word belongs to a theta
def wordThetaWeight(word_theta_prob, theta_prob):
    word_theta_weight = {};
    
    for theta, word_time_prob in word_theta_prob.iteritems():
        time_prob = theta_prob[theta]
        word_theta_weight[theta] = {};
        max_weight = 0.0;
        for word, time_bin in word_time_prob.iteritems():
            dis = 0.0;
            for time, prob in time_bin.iteritems():
                if time in time_prob:
                    prob2 = time_prob[time];
                    dis += (prob-prob2)**2;
                else:
                    dis += prob**2;
            for time, prob in time_prob.iteritems():
                if time in time_bin:
                    continue;
                else:
                    dis += prob**2

            word_theta_weight[theta][word] = 1/dis;
            if 1/dis > max_weight:
                max_weight = 1/dis;

        for word in word_time_prob:
            word_theta_weight[theta][word] /= max_weight;

    return word_theta_weight;

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

##use a soft cluster method 
#def softIterThetaWordTime(event, cluster_num, format, dis_method):
#    #first use the co-occur as the metric to cluster tokens
#    prob_theta_time = {};
#    prob_word_theta = {};
#
#    filename = 'data/event/' + event + '/term_time.txt';
#    infile = file(filename);
#    term_prob = json.load(infile);
#    infile.close();
# 
#    theta_file = 'data/event/' + event + '/iter_theta_prob.txt';
#    out_theta_file = file(theta_file, 'w');
#    
#    truth_file = 'data/event/' + event + '/truth_cluster.txt';
#    true_clusters, label = loadCluster(truth_file, format);
#    
#    
#    theta_time_prob, theta_prob = getThetaTimeProb(true_clusters, term_prob, cluster_num); 
#    json.dump(theta_prob, out_theta_file);
#    out_theta_file.write('\n');
#
#    #use the co-occorence to initialize the cluster
#    pre_clusters, centers = initClusters(event, cluster_num, term_prob, format, 'coocur', dis_method);
#    
#    json.dump(theta_prob, out_theta_file);
#    out_theta_file.write('\n');
#
#    #print pre_clusters;
#    puri = purityWrap(pre_clusters, truth_file, format)
#    print 'co-occure puriry=', puri
#
#    dis_matrix = disOfTemp2(term_prob, dis_method, 'hour')
#    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, centers)
#    #print clusters
#    puri = purityWrap(clusters, truth_file, format)
#    print 'temporal puriry=', puri
#
#    isChanging = True;
#    pre_puri = 0;
#    iter = 1;
#    while isChanging:
#        #get the new theta prob
#        word_theta_prob, word_theta_prob2 = wordThetaProb(term_prob, theta_time_prob, theta_prob, cluster_num);
#
#        word_theta_weight = wordThetaWeight(word_theta_prob, theta_prob);
#        
#        #use 1-NN to find cloest theta
#        word_sel_theta, clusters = findClosestTheta(word_theta_prob, theta_prob);
#        
#        #use previous cluster lable to re-calculate the distance
#        #word_time_dis = getNewWordTimeDis(word_theta_prob2, pre_clusters)
#        #dis_matrix = disOfTemp2(word_time_dis, 'abs', 'hour')
#        #clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, centers)
#        
#        #use the new theta prob to calculate the distance to each theta
#
#        #if not change a lot compare with the previous cluster
#        cluster_label = transClassLabel(pre_clusters)
#        puri = purity(cluster_label, clusters);
#        
#        print 'not changing rate=', puri
#        if puri >= 1 or iter >= 10:
#            isChanging = 0;
#        else:
#            pre_clusters = clusters;
#            pre_puri = puri;
#
#        #print clusters;
#        
#        #calculate the new theta prob
#        theta_time_prob, theta_prob = getThetaTimeWeightProb(word_theta_weight, term_prob, cluster_num); 
#        json.dump(theta_prob, out_theta_file);
#        out_theta_file.write('\n');
#
#        puri = purityWrap(clusters, truth_file, format)
#        print 'iter=', iter, 'puri=', puri;
#        iter += 1;
#    
#    out_theta_file.close();
def innerProduct(in_term_prob, pre_cluster, theta_prob):
    dis_matrix = {};

    for cluster_id, cluster in pre_cluster.iteritems():
        dis_matrix[cluster_id] = {};
        event_prob = theta_prob[cluster_id];
        for term in in_term_prob:
            term_prob = in_term_prob[term];
            dis = 0
            for time, prob in term_prob.iteritems():
                if time in event_prob:
                    dis += event_prob[time] * prob

            dis_matrix[cluster_id][term] = dis;

    return dis_matrix


def softIter(term_prob, pre_clusters, pre_theta_prob):
    dis_matrix = innerProduct(term_prob, pre_clusters, pre_theta_prob)

    for cluster_id, dis_arr in dis_matrix.iteritems():
        count = 0;
        for term, prob in sorted(dis_arr.iteritems(), key = lambda (k,v):(v,k), reverse = True):
            print cluster_id, '\t', term, '\t', str(prob), '\n'
            if count == 10:
                break;
            count += 1;

def postIter(term_prob, term_one_place_prob, theta_time_prob, pre_theta_prob, pre_clusters, centers, cluster_num, truth_file, out_theta_file, dis_method, format, filter_type):
    global g_selected_words

    isChanging = True;
    pre_puri = 0;
    ret_puri = 0;
    ret_accu = 0;
    iter = 1;
    
    for term, time_bin in term_prob.iteritems():
        plotTimeDis(time_bin, term);
    #test
    plotthetatime(pre_theta_prob, 'co-occur');
    
    while isChanging:
        ############use the probability window
        #get the new theta prob
        #word_theta_prob, word_theta_prob2 = wordThetaProb(term_prob, theta_time_prob, theta_prob, cluster_num);

        #use previous cluster lable to re-calculate the distance
        #word_time_dis = getNewWordTimeDis(word_theta_prob2, pre_clusters)
        word_time_dis = getWordThetaProb(term_prob, pre_theta_prob, pre_clusters, filter_type)
        print 'iter=', iter, 'get word dis over'
        dis_matrix = disOfTemp2(word_time_dis, dis_method, 'hour')
        print 'iter=', iter, 'get dis matrix over'
        dis_matrix = disMatrixFilter(dis_matrix, g_selected_words)
        print 'iter=', iter, 'filter matrix over'
        clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, centers)
        print 'iter=', iter, 'cluster over'

        puri = purityWrap(clusters, truth_file, format)
        accu = K_NN(dis_matrix, truth_file, 1, format)
        print 'iter=', iter, 'the post prob window puri=', puri, 'accuracy=', ret_accu;
 
        #################
        #it's another iterative method, use the new word distribution to calculate the theta prob
        #word_theta_prob, word_theta_prob2 = wordThetaProb(term_one_place_prob, theta_time_prob, theta_prob, cluster_num);
        #term_one_place_prob = getNewWordTimeDis(word_theta_prob2, clusters)
        
        ###############calculate the new theta prob
        theta_prob = getThetaTimeProb2(clusters, term_prob, cluster_num); 
        #theta_time_prob, theta_prob = getWeightThetaTimeProb(clusters, centers, term_prob, cluster_num); 
        
        print 'get theta dis over'
        #test
        plotthetatime(theta_prob, 'post' + str(iter));
        for word, time_dis in word_time_dis.iteritems():
            plotTimeDis(time_dis, word);
        
        if testGoal(pre_theta_prob, theta_prob, pre_clusters, clusters) or iter >= 10:
            isChanging = 0;
            if iter == 1:
                ret_puri = puri;
                ret_accu = accu;
        else:
            pre_clusters = deepcopy(clusters);
            pre_theta_prob = deepcopy(theta_prob);
            ret_puri = puri;
            ret_accu = accu;

        json.dump(theta_prob, out_theta_file);
        out_theta_file.write('\n');
        
        iter += 1;
        
        print 'post'
    
    ## test, need remove
    for term in dis_matrix:
        count = 0;
        for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
            print term.encode('utf-8'), term2.encode('utf-8'), dis;
            count = count + 1;
            if count > 10:
                break;

    return ret_puri, ret_accu, clusters;

def windowIter(term_prob, term_a_place_prob, pre_theta_prob, pre_cluster, centers, cluster_num, truth_file, out_theta_file, filter_type, dis_method, format):
    global g_selected_words
    isChanging = True;
    pre_puri = 0;
    ret_puri = 0;
    ret_accu = 0;
    iter = 1;
    
    plotthetatime(pre_theta_prob, 'co-occur');
    while isChanging:
        #############use the square window
        square_window, gauss_window = getThetaTimeLocationWindow(pre_theta_prob);
        print 'get window over'

        ############use the probability window
        #get the new theta prob
        if 'gauss' in filter_type:
            #word_theta_prob, word_theta_prob2 = wordThetaProb(term_prob, {}, gauss_window, cluster_num);
            word_time_dis = getWordThetaProb(term_prob, gauss_window, pre_cluster, filter_type)
        if 'square' in filter_type:
            word_time_dis = getWordThetaProb(term_prob, square_window, pre_cluster, filter_type)
            #word_theta_prob, word_theta_prob2 = wordThetaProb(term_prob, {}, square_window, cluster_num);
        print 'get word dis over'

        #use previous cluster lable to re-calculate the distance
        #word_time_dis = getNewWordTimeDis(word_theta_prob2, pre_cluster)
        dis_matrix = disOfTemp2(word_time_dis, dis_method, 'hour')
        print 'get dis matrix over'
        dis_matrix = disMatrixFilter(dis_matrix, g_selected_words)
        print 'filter dis matrix over'

        clusters, centers = kmeansTokensWrap(dis_matrix, cluster_num, centers)
        print 'cluster num', cluster_num;
        print 'cluster over'
        
        ###############calculate the new theta prob
        #theta_time_prob, theta_prob = getThetaTimeProb(clusters, term_prob, term_a_place_prob, cluster_num); 
        theta_time_prob, theta_prob = getWeightThetaTimeProb(clusters, centers, term_prob, cluster_num); 
        print 'get theta prob over'
         
        puri = purityWrap(clusters, truth_file, format)
        ret_puri = puri;
        ret_accu = K_NN(dis_matrix, truth_file, 1, format)
        print 'iter=', iter, filter_type, 'puri=', puri, 'accuracy=', ret_accu;
        
        #test
        if 'gauss' in filter_type:
            plotthetatime(pre_theta_prob, 'gauss' + str(iter));
            plotthetatime(gauss_window, 'gauss' + str(iter));
        else:
            plotthetatime(pre_theta_prob, 'square' + str(iter));
            plotthetatime(square_window, 'square' + str(iter));

        ###########control when to exit the iteration
        if testGoal(pre_theta_prob, theta_prob, pre_cluster, clusters) or iter >= 10:
            isChanging = 0;
        else:
            pre_cluster = deepcopy(clusters);
            pre_theta_prob = deepcopy(theta_prob);
        #print clusters;
        json.dump(theta_prob, out_theta_file);
        out_theta_file.write('\n');
        
        iter += 1;
    
        print filter_type
    return ret_puri, ret_accu, clusters;

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

    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_one_place_prob = json.load(infile);
    infile.close();
    for term, time_bin in term_one_place_prob.iteritems():
        normalizeDic(time_bin);


    theta_file = 'data/event/' + event + '/iter_theta_prob.txt';
    out_theta_file = file(theta_file, 'w');
    
    truth_file = 'data/event/' + event + '/truth_cluster.txt';
    true_clusters, label = loadCluster(truth_file, format);
   
    #only for comparison
    theta_prob = getThetaTimeProb2(true_clusters, term_prob, cluster_num); 
    plotthetatime(theta_prob, 'Ground Truth');
    #json.dump(theta_prob, out_theta_file);
    #out_theta_file.write('\n');

    pre_clusters, centers = initClusters(event, cluster_num, term_one_place_prob, format, 'coocur', dis_method); 
    #get the initial theta prob p(theta|t),  p(t|theta), cluster
    theta_prob = getThetaTimeProb2(pre_clusters, term_prob, cluster_num); 
    #theta_time_prob, theta_prob = getWeightThetaTimeProb(pre_clusters, centers, term_prob, cluster_num); 

    json.dump(theta_prob, out_theta_file);
    out_theta_file.write('\n');
    #print pre_clusters;
 
    ret, accu = iterFunc(term_prob, term_one_place_prob, [], theta_prob, pre_clusters, centers, cluster_num, truth_file, out_theta_file, dis_method, format)
    metrics['temp_post'] = ret[1]
    #metrics['temp_gauss'] = ret[2]
    #metrics['temp_square'] = ret[3]
    #metrics['temp_average'] = ret[4]
    accu_metrics['temp_post'] = accu[1]
    #accu_metrics['temp_gauss'] = accu[2]
    #accu_metrics['temp_square'] = accu[3]
    #accu_metrics['temp_average'] = accu[4]
 
    #use the temporal-location
    dis_matrix = disOfTemp2(term_prob, dis_method, 'hour')
    dis_matrix = disMatrixFilter(dis_matrix, g_selected_words) 
    center_temp = deepcopy(centers);
    clusters, center_temp = kmeansTokensWrap(dis_matrix, cluster_num, center_temp)
    #print clusters
    puri = purityWrap(clusters, truth_file, format)
    metrics['temp'] = puri;
    accu_metrics['temp'] = K_NN(dis_matrix, truth_file, 1, format)
    print 'temporal puriry=', puri, 'accuracy=', accu_metrics['temp']

    ####test, return first
    return metrics, accu_metrics
 
    #filter the background noise
    print '##############after filtering the noises'
    filter_method = 'average'
    term_prob_filter = deepcopy(term_prob)
    BGNoiseFilter(term_prob_filter, filter_method);

    ret, accu = iterFunc(term_prob_filter, term_one_place_prob, theta_time_prob, theta_prob, pre_clusters, centers, cluster_num, truth_file, out_theta_file, dis_method, format)
    metrics['temp_post_aver_nr'] = ret[1]
    metrics['temp_gauss_aver_nr'] = ret[2]
    metrics['temp_square_aver_nr'] = ret[3]
    metrics['temp_aver_aver_nr'] = ret[4]
    accu_metrics['temp_post_aver_nr'] = accu[1]
    accu_metrics['temp_gauss_aver_nr'] = accu[2]
    accu_metrics['temp_square_aver_nr'] = accu[3]
    accu_metrics['temp_aver_aver_nr'] = accu[4]    
    
    ####test, return first
    return metrics, accu_metrics
 
   
    filename = 'data/event/' + event + '/term_coocurence.txt'
    infile = file(filename);
    if format == 'utf-8':
        dis_matrix = json.load(infile, format);
    else:
        dis_matrix = json.load(infile);
    dis_matrix = disMatrixFilter(dis_matrix, g_selected_words)

    center_temp = deepcopy(centers);
    cooc_clusters, _ = kmeansTokensWrap(dis_matrix, cluster_num, center_temp); 
    puri = purityWrap(cooc_clusters, truth_file, format)
    metrics['coocur'] = puri;
    accu_metrics['coocur'] = K_NN(dis_matrix, truth_file, 1, format)
    print 'co-occure puriry=', puri, 'accuracy=', accu_metrics['coocur']
    
    #filter the background noise
    print '##############after filtering the noises'
    filter_method = 'gauss'
    term_prob_filter = deepcopy(term_prob)
    BGNoiseFilter(term_prob_filter, filter_method);

    ret, accu = iterFunc(term_prob_filter, term_one_place_prob, theta_time_prob, theta_prob, pre_clusters, centers, cluster_num, truth_file, out_theta_file, dis_method, format)
    metrics['temp_post_norm_nr'] = ret[1]
    metrics['temp_gauss_norm_nr'] = ret[2]
    metrics['temp_square_norm_nr'] = ret[3]
    metrics['temp_aver_norm_nr'] = ret[4]
    accu_metrics['temp_post_norm_nr'] = accu[1]
    accu_metrics['temp_gauss_norm_nr'] = accu[2]
    accu_metrics['temp_square_norm_nr'] = accu[3]
    accu_metrics['temp_aver_norm_nr'] = accu[4]

   
    return metrics, accu_metrics

def iterFunc(term_prob, term_one_place_prob, theta_time_prob, theta_prob, pre_clusters, centers, cluster_num, truth_file, out_theta_file, dis_method, format):
    
    softIter(term_prob, pre_clusters, theta_prob);
    return;
    
    metrics = {};
    accu_metrics = {};
    #post probability iteration
    theta_prob_temp = deepcopy(theta_prob);
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    print 'post iter begin.......'
    puri, accu, cluster_post = postIter(term_prob, term_one_place_prob, theta_time_prob, theta_prob_temp, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, dis_method, format, [])
    metrics[1] = puri;
    accu_metrics[1] = accu;
    
    ###test
    return metrics, accu_metrics
    
    cluster_file = 'output/cluster_post_day.txt';
    dumpCluster(cluster_post, cluster_file);
    
    print 'gauss iter begin.......'
    #gauss probability iteration
    theta_prob_temp = deepcopy(theta_prob);
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    puri, accu, cluster_gauss = windowIter(term_prob, term_one_place_prob, theta_prob_temp, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, ['gauss'], dis_method, format)
    metrics[2] = puri;
    accu_metrics[2] = accu;
 
    cluster_file = 'output/cluster_gauss.txt';
    dumpCluster(cluster_gauss, cluster_file);

    print 'square iter begin.......'
    #square probability iteration
    theta_prob_temp = deepcopy(theta_prob);
    cluster_temp = deepcopy(pre_clusters);
    centers_temp = deepcopy(centers);
    puri, accu, cluster_square = windowIter(term_prob, term_one_place_prob, theta_prob_temp, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, ['square'], dis_method, format)
    metrics[3] = puri;
    accu_metrics[3] = accu;

    cluster_file = 'output/cluster_square.txt';
    dumpCluster(cluster_square, cluster_file);

    print 'post average filter iter begin.......'
    puri, accu, cluster_post = postIter(term_prob, term_one_place_prob, theta_time_prob, theta_prob_temp, cluster_temp, centers_temp, cluster_num, truth_file, out_theta_file, dis_method, format, ['average'])
    metrics[4] = puri;
    accu_metrics[4] = accu;
    
    return metrics, accu_metrics

def probThetaWordTime(event):
    prob_theta_time = {};
    prob_word_theta = {};

    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename, 'utf-8');

    #build a gaussian for each cluster
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
            if token not in term_prob:
                continue;
            token_fre[token] = 0.0;

            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                time = int(time);
                if time not in cluster_fre[cluster_index]:
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
            if time in cluster_fre[j]:
                sum_fre += cluster_fre[j][time];

        for j in range(1, event_num):
            if time in cluster_fre[j]:
                prob_theta_time[time][j] = cluster_fre[j][time] / sum_fre;
            else:
                prob_theta_time[time][j] = 0;
    
    #p(w|theta)
    for j, cluster in clusters.iteritems():
        j = int(j);
        prob_word_theta[j] = {};
        
    for j, cluster in clusters.iteritems():
        j = int(j);
        for token in cluster:
            prob_word_theta[j][token] = token_fre[token] / cluster_sum_fre[j];

            #for other theta, all 0
            for i in range(1, event_num):
                if i == j:
                    continue;
                prob_word_theta[i][token] = 0;

    #p(theta|w,t) = p(theta, w, t)/sigma_theta{p(theta, w, t)}
    prob_theta_word_time = {};
    freq_time_word = {}; 
    for j, cluster in clusters.iteritems():
        j = int(j);
        for token in cluster:
            prob_theta_word_time[token] = {};
            freq_time_word[token] = {};
            for time in range(0, max_time):
                if time not in prob_theta_word_time[token]:
                    prob_theta_word_time[token][time] = {};

                prob = prob_theta_time[time][j]#*prob_word_theta[j][token];
                prob_sum = 0.0;
                for theta in range(1, event_num):
                     temp_prob = prob_theta_time[time][theta]#*prob_word_theta[theta][token];
                     prob_sum += temp_prob;

                #print prob_sum, prob;

                if prob_sum > 0.0:
                    prob_theta_word_time[token][time][j] = prob / prob_sum;
                else:
                    prob_theta_word_time[token][time][j] = 0;

                if str(time) in term_prob[token]:
                    freq_time_word[token][time] = term_prob[token][str(time)] * prob_theta_word_time[token][time][j]; 
    
    return prob_theta_word_time, freq_time_word;

def termEventTimeDis(event):
    filename = 'data/event/' + event + '/term_time.txt';
    infile = file(filename);
    term_prob = json.load(infile);
    infile.close();
    #term_prob = loadTermTime(filename);
    
    filename = 'data/event/' + event + '/truth_cluster.txt';
    clusters, label = loadCluster(filename);

    #build a gaussian for each cluster
    prob_event_time = {};
    for cluster_index, cluster in clusters.iteritems():
        all_fre = {};
        for token in cluster:
            token = unicode(token, 'utf-8')
            if token not in term_prob:
                continue;

            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                if time not in all_fre:
                    all_fre[time] = 0.0;

                all_fre[time] += freq;
        
        for token in cluster:
            token = unicode(token, 'utf-8')
            if token not in term_prob:
                continue;

            if token not in prob_event_time:
                prob_event_time[token] = {};
            
            time_bins = term_prob[token];
            for time, freq in time_bins.iteritems():
                prob_event_time[token][time] = freq / all_fre[time];

    return prob_event_time;

def termEventDisMain():
    event = '8_2011_events';

    prob = termEventTimeDis(event);

    filename = 'data/event/' + event + '/term_time_prob.txt';
    outfile = file(filename, 'w');
    json.dump(prob, outfile);
    outfile.write('\n');
    outfile.close();

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

    metric_sum = {};
    accu_metric_sum = {};
    for i in range(0, iter_count):
        print 'hard cluster, KL distance!!!!!!!\n\n\n'
        dis_method = 'KL'
        metric, accu_metric = iterThetaWordTime(event, cluster_num, format, dis_method)
        for key, value in metric.iteritems():
            if key not in metric_sum:
                metric_sum[key] = 0;
                accu_metric_sum[key] = 0;
            metric_sum[key] += metric[key];
            accu_metric_sum[key] += accu_metric[key];

    for key in metric_sum:
        metric_sum[key] /= iter_count;
        accu_metric_sum[key] /= iter_count;
 
    outfile.write('purity based on KL distance\n')
    for key, value in metric_sum.iteritems():
        outfile.write(key + '\t' + str(value) + '\n');
    outfile.write('\nAccuracy based on KL distance\n')
    for key, value in accu_metric_sum.iteritems():
        outfile.write(key + '\t' + str(value) + '\n');
    outfile.write('\n')
    outfile.close();

    #print 'soft cluster'
    #softIterThetaWordTime(event, cluster_num, format)

def genWindowMain():
    event = '8_2011_events';
    #event = 'jpeq_jp';
    #event = 'irene_overall';
    model1 = genGaussWindow(event);
    
    model2 = genSquareWindow(event);

    filename = 'data/event/' + event + '/filter_window.txt';
    outfile = file(filename, 'w');
    json.dump(model1, outfile);
    outfile.write('\n');

    json.dump(model2, outfile);
    outfile.write('\n');
    outfile.close();

def eventMain():
    #filter_type = [];
    filter_type = ['mean'];
    format = 'utf-8'
    
    event = 'irene_overall'
    cluster_num = 3;
    termIterEventMain(event, cluster_num, format, filter_type)
 
    return;
    
    event = 'jpeq_jp'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)
   
    event = '3_2011_events'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)
    
    event = '8_2011_events'
    cluster_num = 5;
    termIterEventMain(event, cluster_num, format, filter_type)
    
#genWindowMain();
#termDisMain();

#termEventDisMain();

#termThetaDisMain();

#termIterEventMain()

eventMain();
