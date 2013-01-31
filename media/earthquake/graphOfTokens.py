#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
import ast
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.api import *
from tinysegmenter import *
from settings import Settings
from operator import itemgetter
#from Utility import *
import random
from utility.dijkstra import *
from utility.MST import *
from evaluate import *
import sys
sys.path.append('../../utility/')
from boundingBox import *
from loadFile import *
from sklearn import neighbors, datasets
from kmeans import kmeansTokens
from common import normalizeDic

def disOfDic(dic1, dic2, method = 'abs'):
    dis = 0.0;
    for term, value in dic1.iteritems():
        value2 = 0;
        if term in dic2.keys():
            value2 = dic2[term];
        dis += abs(value - value2);
    
    for term, value in dic2.iteritems():
        if term in dic1.keys():
            continue;
        dis += abs(value - 0.0);

    return dis;

def allocMatrix(n, m):
    matrix = {};
    #array
    if n == 1:
        for j in range(0, m):
            matrix[j] = 0;
    else:
        for i in range(0, n):
            matrix[i] = {};
            for j in range(0, m):
                matrix[i][j] = 0;
    return matrix;

def norMatrix(matrix):
    sum = 0;
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            sum = sum + matrix[i][j];
    
    if sum == 0:
        return;

    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            matrix[i][j] = matrix[i][j]/float(sum);

def loadSparseDisMatrix(filename):
    infile = file(filename);
    lines = infile.readlines();
    matrix = cjson.decode(lines[0]);

    return matrix;

def loadDisMatrix(filename):
    infile = file(filename);
    lines = infile.readlines();
    matrix = cjson.decode(lines[2]);

    return matrix;

#def loadTokens(token_filename):
#    #load the selected tokens
#    infile = file(token_filename);
#    lines = infile.readlines();
#    for line in lines:
#        line = string.lower(line);
#        dic = cjson.decode(line);
#        key = str(year) + '-' + str(month) + '-' + str(day);
#        tokens = dic.get(key);
#        if tokens != None:
#            break;

 #   for token, freq in sorted(tokens.iteritems(), key=lambda (k,v):(v,k), reverse = True):
 #       print token.encode('utf-8'), freq;

#    return tokens;

def loadTopSentence(dirname):
    if os.path.isfile(dirname):
        infile = file(dirname);
        lines = infile.readlines();
        tweet_list = [];
        for line in lines:
            index = line.rfind('"id":');
            if index < 0:
                continue;
            index2 = line.find('}', index);
            if index2 < 0:
                continue;
            sub_line = line[0:index2+1];
            tweet_info = cjson.decode(sub_line);
            tweet_list.append(tweet_info);

        return tweet_list;

    files = os.listdir(dirname);
    tweet_list = {};
    for filename in files:
        if os.path.isdir(dirname + filename):
            continue;
        infile = file(dirname + filename);
        lines = infile.readlines();
        tweet_list[filename] = [];
        for line in lines:
            index = line.rfind('"id":');
            if index < 0:
                continue;
            index2 = line.find('}', index);
            if index2 < 0:
                continue;
            sub_line = line[0:index2+1];
            tweet_info = cjson.decode(sub_line);
            tweet_list[filename].append(tweet_info);

    return tweet_list;


#construct the matrix between tokens
def buildMatrix(tweets, tokens, token_matrix):
    for tweet in tweets:
        for i in range(0, len(tokens)):
            token = tokens[i];
            if tweet.find(token) < 0:
                continue;
            for j in range(i, len(tokens)):
                if tweet.find(tokens[j]):
                    token_matrix[i][j] = token_matrix[i][j] + 1; 

def loadTweets(filename, tweets, format='json'):
    in_file = file(filename);
    lines = in_file.readlines();
    for line in lines:
        if format == 'json':
            tweet_info = cjson.decode(line);
            #print tweet_info["hashtag"];
        else:
            tweet_info = ast.literal_eval(line);
        tweets.append(tweet_info);

def calRelevance(sel_tokens, rel_matrix, tweets, stop_words):
    #count = 0;
    for tweet in tweets:
        #count = count + 1;
        #if count > 100:
        #    break;
        text = string.lower(tweet['text']);
        for token in sel_tokens:
            if text.find(token) < 0:
                continue;

            for token2 in sel_tokens:
                if token == token2:
                    continue;

                if text.find(token2) < 0:
                    continue;

                rel_matrix[token][token2] = rel_matrix[token][token2] + 1;
                rel_matrix[token2][token] = rel_matrix[token2][token] + 1;

 
def calRelevance2(sel_tokens, rel_matrix, tweets, stop_words):
    #count = 0;
    for tweet in tweets:
        #count = count + 1;
        #if count > 100:
        #    break;

        tokens = tokenize(tweet['text'], 'Japanese', stop_words);
        token_list = tokens.keys();
        for i in range(0, len(token_list)):
            token = token_list[i];
            if token not in sel_tokens:
                continue;

            for j in range(i+1, len(token_list)):
                token2 = token_list[j];
                if token2 not in sel_tokens:
                    continue;

                rel_matrix[token][token2] = rel_matrix[token][token2] + 1;
                rel_matrix[token2][token] = rel_matrix[token2][token] + 1;

                #print token, token2, rel_matrix[token][token2];

def loadTweets(year, month, day, isImage):
    path = Settings.tweet_folder;
    sub_path = '/' + str(year) + '/' + str(month) + '/' + str(day) + '/';
    path = path + sub_path;
    files = os.listdir(path);
    getter = GetTweets();
    similar_tweets = [];
    for afile in files:
        filename = path + afile;
        print filename;
        tweet_list = [];
        for tweet in getter.iterateTweetsFromGzip(filename):
            [rel, tweet_info] = getter.parseTweet(tweet);
            if not isTweetInJapan(tweet_info):
                continue;
    
            if isImage:
                if tweet_info['url'] == None or tweet_info['url'] == []:
                    continue;

            tweet_list.append(tweet_info);
    
    return tweet_list;

def PrimWrap(dis_matrix):
    nodes = dis_matrix.keys();
    edges = [];
    for i in range(0, len(dis_matrix.keys())):
        key = dis_matrix.keys()[i];
        for j in range(i+1, len(dis_matrix.keys())):
            key2 = dis_matrix.keys()[j];
            if dis_matrix[key][key2] > 0:
                edges.append((key, key2, dis_matrix[key][key2]));

    return Prim(nodes, edges);
   
def DijkstraWrap(dis_matrix, root):
    matrix_tmp = {};
    for key in dis_matrix.keys():
        matrix_tmp[key] = {};
        for key2 in dis_matrix.keys():
            if dis_matrix[key][key2] > 0:
                if key == key2:
                    continue;
                matrix_tmp[key][key2] = dis_matrix[key][key2];
     
    return Dijkstra(matrix_tmp, root);

def fillDisMatrix(dis_matrix):
    matrix_tmp = {};
    for key in dis_matrix.keys():
        matrix_tmp[key] = {};
        for key2 in dis_matrix.keys():
            if dis_matrix[key][key2] > 0:
                if key == key2:
                    continue;
                matrix_tmp[key][key2] = dis_matrix[key][key2];
             
    for key in dis_matrix.keys():
        for key2 in dis_matrix[key]:
            if dis_matrix[key][key2] == 0:
                if key == key2:
                    continue;
                D, path = Dijkstra(matrix_tmp, key);
                for des, dis in D.iteritems():
                    #print key.encode('utf-8'), des.encode('utf-8'), dis;
                    
                    #if dis == 0 and des != key:
                    dis_matrix[key][des] = dis;
                    dis_matrix[des][key] = dis;
    
    for key in dis_matrix.keys():
        for key2 in dis_matrix.keys():
            if dis_matrix[key][key2] == 0:
                if key == key2:
                    continue;
                dis_matrix[key][key2] = 1;
     
def reverse(dis_matrix):
    for key in dis_matrix.keys():
        key_sum = 1;
        #for key2 in dis_matrix[key]:
        #    key_sum = key_sum + dis_matrix[key][key2];

        for key2 in dis_matrix[key]:
            if dis_matrix[key][key2] != 0:
                dis_matrix[key][key2] = key_sum/float(dis_matrix[key][key2]);

def loadTokens(token_filename, year, month, day, isImage):
    #load the selected tokens
    infile = file(token_filename);
    lines = infile.readlines();
    for line in lines:
        line = string.lower(line);
        dic = cjson.decode(line);
        key = str(year) + '-' + str(month) + '-' + str(day);
        if isImage:
            key = 'image-' + key;
        tokens = dic.get(key);
        if tokens != None:
            break;

    if tokens == None:
        return;
    
    #for token, freq in sorted(tokens.iteritems(), key=lambda (k,v):(v,k), reverse = True):
    #    print token.encode('utf-8'), freq;


def relevanceOfToken(tokens, stop_words, year, month, day, day_to, event='JP'):
    matrix = {};
    for token in tokens:
        if token == 'totaltokennum':
            continue;
        matrix[token] = {};
        for token2 in tokens:
            if token2 == 'totaltokennum':
                continue;
            matrix[token][token2] = 0; 

    if event == 'JP':
        path = './output/TopSentence/';
    else:
        path = '/mnt/chevron/yuan/tweet/';

    for aday in range(day, day_to):
        fname = str(year) + '-' + str(month) + '-' + str(aday) + '.txt';
        if event == 'JP':
            tweet_list = loadTopSentence(path + fname);
        else:
            fname = str(year) + '_' + str(month) + '_' + str(aday) + '.txt';
            tweet_list = loadSimpleTweetsFromFile(path + fname);

        calRelevance(tokens, matrix, tweet_list, stop_words);

    reverse(matrix);

    outfile = file('./output/TopSentence/dis_matrix' + str(month) + '_' + str(day) + '.txt', 'w');
    
    json.dump(matrix, outfile, encoding = 'utf-8');
    outfile.write('\n\n');
    
    #calculate the distances betweet each pair
    fillDisMatrix(matrix);
    json.dump(matrix, outfile, encoding = 'utf-8');
   
    outfile.close();
    return matrix;

#def clusterTokensMain(isImage, fromFile):
#    #token_file = './output/JP_earthquake_daily_token_filter.txt';
#    tokens = loadTerms('./data/US_cluster_truth.txt');
#
#    year = 2011;
#    month = 8;
#    day = 24;
#    day_to = 26;
#
#    stop_file = './data/stop_words.txt';
#    stop_words = loadStopwords(stop_file);
#
#    if fromFile == 1:
#        matrix = loadDisMatrix("./output/TopSentence/dis_matrix_coocur.txt");
#    else:
#        if fromFile == 2:
#            matrix = loadSparseDisMatrix("./output/TopSentence/dis_matrix.txt");
#        if fromFile == 3:
#            #cal the relevance betwee Japan data
#            matrix = relevanceOfToken(tokens, stop_words, year, month, day, day_to, 'JP');
#        if fromFile == 4:
#            #cal the relevance using US data
#            matrix = relevanceOfToken(tokens, stop_words, year, month, day, day_to, 'US');
#       
#    cluster = kmeansTokens(matrix, 6);
#    
#    outfile = file('./output/Map/cluster_of_ococur' + str(month) + '_' + str(day) + '.txt', 'w');
#    for key, tokens in cluster.iteritems():
#        #outfile.write(key.encode('utf-8') + '\n');
#        for token in tokens:
#            outfile.write(token.encode('utf-8') + '\t');
#        outfile.write('\n');
#
#    outfile.close();

def genShortPathTree(matrix):
    max_sum = 0;
    for key in matrix.keys():
        sum = 0;
        for key2 in matrix.keys():
            if matrix[key][key2] > 0:
                sum = sum + 1;
        if sum > max_sum:
            max_sum = sum;
            root = key;

    root = "earthquake";

    #for key in matrix.keys():
    #    root = key;
    #    print root.encode("utf-8");
    D, path = DijkstraWrap(matrix, root);
        
    #    print '\nroot = ', root.encode('utf-8');
    #    layer_cluster = {};
    #    drawTree(root, path, 1, layer_cluster);

    return root, D, path;

def drawTree(node, path, layer, layer_cluster):
    #store the clusters in each layer
    clusters = layer_cluster.get(layer);
    if clusters == None:
        clusters = {};
        layer_cluster[layer] = clusters;

    aCluster = clusters.get(node);
    if aCluster == None:
        aCluster = [];
        clusters[node] = aCluster;

    #path[v] is the predecessor of v in the path from root to v
    list = [];
    for key, pred in path.iteritems():
        #add direct son
        if pred == node:
            list.append(key);
            aCluster.append(key);
            aCluster.append(pred);
            continue;
        #add all the grandsons
        father = pred;
        temp_list = [key, father];
        while father != None and father != 'earthquake':
            father = path.get(father);
            if father != None:
                if father not in temp_list:
                    temp_list.append(father);
                if father == node:
                    aCluster = aCluster + temp_list;
                    break;
        
    temp_set = set(aCluster);
    clusters[node] = [];
    for item in temp_set:
        clusters[node].append(item);
        #print node, item;
        #aCluster.append(key);
        
    for node in list:
        str = "";
        for i in range(0, layer):
            str = str + '    ';
        print str + node.encode('utf-8');
    
        drawTree(node, path, layer + 1, layer_cluster);

def genShortPathTreeMain():
    matrix = loadSparseDisMatrix("./output/TopSentence/dis_matrix.txt");
    root, D, path = genShortPathTree(matrix);
    
    layer_cluster = {};
    print root.encode('utf-8');
    drawTree(root, path, 1, layer_cluster);
    
    outfile = file("output/TopSentence/layer_cluster.txt", 'w');
    json.dump(layer_cluster, outfile);
    outfile.close();

def genMSTMain():
    matrix = loadSparseDisMatrix("./output/TopSentence/dis_matrix.txt");
    mst = PrimWrap(matrix);
    path = {};
    
    root = mst[0][0];
    for n1, n2, c in mst:
        path[n2] = n1;

    layer_cluster = {};
    print 'root=', root;
    drawTree(root, path, 1, layer_cluster);

def getIndexForUS(lati, longi):
    # US
    lati_down = 29.6;
    lati_up = 49.1;
    longi_left = -125.5;
    longi_right = -69.3; 
 
    step = 100;
    lati_step = (lati_up - lati_down)/step;
    longi_step = (longi_right - longi_left)/step;
          
    lati_index = -1;
    longi_index = -1;
    if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
        lati_index = math.floor((lati - lati_down)/lati_step);
        longi_index = math.floor((longi - longi_left)/longi_step);
    
    return int(lati_index), int(longi_index);

def getIndexForJP(lati, longi):
    # Japan
    lati_down = 30.4;
    lati_up = 45.4;
    longi_left = 129.5;
    longi_right = 147.0; 
    step = 100;
    lati_step = (lati_up - lati_down)/step;
    longi_step = (longi_right - longi_left)/step;
          
    lati_index = -1;
    longi_index = -1;
    if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
        lati_index = math.floor((lati - lati_down)/lati_step);
        longi_index = math.floor((longi - longi_left)/longi_step);
    
    return lati_index, longi_index;

def loadPoints(filename):
    infile = file(filename);
    lines = infile.readlines();
    term_loc = {};
    for i in range(0, len(lines)-1, 2):
        term = lines[i];
        line = lines[i+1];
        items = line.split('\t');
        term_loc[term] = [];
        for item in items:
            item = item[1:len(item)-1];
            geo = item.split(',');
            if len(geo) < 2:
                continue;

            lat = float(geo[0]);
            log = float(geo[1]);
            term_loc[term].append((lat, log));
    
    return term_loc;

def transTimePoints(term_time_loc, useKernel, bb, useDegree=0, grid_count=100):
    term_matrix = {};
    lat_num = grid_count;
    lon_num = grid_count;
    if useDegree == 1:
        lat_num = math.ceil(bb[1] - bb[0]);
        lon_num = math.ceil(bb[3] - bb[2]);

    for term, time_locs in term_time_loc.iteritems():
        term_matrix[term] = {};
        for day, locs in time_locs.iteritems():
            matrix = {};
            term_matrix[term][day] = matrix;
            #matrix = allocMatrix(lat_num + 2, lon_num + 2);
            for loc in locs:
                lat = loc[0];
                log = loc[1];
                lati_index, longi_index = getIndexForbb(lat, log, bb, lat_num, lon_num);
                if lati_index > 0 and longi_index > 0:
                    #key = lati_index * lat_num + longi_index;
                    key = str(lati_index) + '_' + str(longi_index);
                    if key not in matrix.keys():
                        matrix[key] = 0;

                    matrix[key] += 1;

            #if useKernel == 1:
            #    kernelGeoDis(matrix);

    #        norMatrix(matrix);
    return term_matrix;

def transPoints(term_loc, useKernel, bb, useDegree=0, grid_count=100):
    term_matrix = {};
    lat_num = grid_count;
    lon_num = grid_count;
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

#use 1-dimension list but not matrix to stand for locs
def transPoints2(term_loc, useKernel, bb, useDegree=0, grid_count=100):
    lat_num = grid_count;
    lon_num = grid_count;
    if useDegree == 1:
        lat_num = math.ceil(bb[1] - bb[0]);
        lon_num = math.ceil(bb[3] - bb[2]);

    term_matrix = {};
    for term, locs in term_loc.iteritems():
        loc_list = {};
        for loc in locs:
            lat = loc[0];
            log = loc[1];
            lati_index, longi_index = getIndexForbb(lat, log, bb, lat_num, lon_num);
            if lati_index >= 0 and longi_index >= 0:
                key = str(lati_index) + '_' + str(longi_index);
                if key not in loc_list.keys():
                    loc_list[key] = 0;
                loc_list[key] += 1;
 
        normalizeDic(loc_list)
        term_matrix[term] = loc_list;
    
    return term_matrix;

def disOfTimeLocsList(time_locs1, time_locs2, method):
    dis = 0.0;
    for time1, locs1 in time_locs1.iteritems():
        if time1 in time_locs2.keys():
            locs2 = time_locs2[time1];
        else:
            locs2 = {};
        for loc_index, fre in locs1.iteritems():
            if loc_index in locs2.keys():
                dis += abs(fre-locs2[loc_index]);
            else:
                dis += fre;
    
    for time2, locs2 in time_locs2.iteritems():
        if time2 in time_locs1.keys():
            locs1 = time_locs1[time1];
        else:
            locs1 = {};
        for loc_index, fre in locs2.iteritems():
            if loc_index in locs1.keys(): #already calculated
                continue;
            else:
                dis += abs(fre-locs2[loc_index]);
    return dis;

def disOfTimeGeo(term_matrix, method):
    term_num = len(term_matrix);

    dis_matrix = {};
    for term, time_locs in term_matrix.iteritems():
        dis = 0;
        dis_matrix[term] = {};
        for term2, time_locs2 in term_matrix.iteritems():
            if term2 == term:
                dis_matrix[term][term] = 0;
                continue;
            
            dis = disOfTimeLocsList(time_locs, time_locs2, 'abs')  
            dis_matrix[term][term2] = dis;
            
        count = 0;
        for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
            #print term, term2, dis;
            count = count + 1;
            if count > 10:
                break;

    return dis_matrix;

def disOfTerm(term_matrix, method):
    term_num = len(term_matrix);

    dis_matrix = {};
    for term, matrix in term_matrix.iteritems():
        dis = 0;
        dis_matrix[term] = {};
        for term2, matrix2 in term_matrix.iteritems():
            if term2 == term:
                dis_matrix[term][term] = 0;
                continue;
            dis = 0;
            for i in range(0, len(matrix)):
                for j in range(0, len(matrix[i])):
                    if method == 'KL':
                        if matrix[i][j] != 0 and matrix2[i][j] != 0:
                            dis = dis + math.log(matrix[i][j]/float(matrix2[i][j])) * matrix[i][j];
                    else:
                        dis = dis + abs(matrix[i][j] - matrix2[i][j]);
            
            dis_matrix[term][term2] = dis;

        count = 0;
        for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
            #print term, term2, dis;
            count = count + 1;
            if count > 10:
                break;

    return dis_matrix;

def kernelGeoDis(dis_matrix):
    for i in range(0, len(dis_matrix)):
        for j in range(0, len(dis_matrix[0])):
            if dis_matrix[i][j] == 0:
                up = 0; down = 0; left = 0; right = 0;
                window = 2;
                if i - window > 0:
                    up = i - window;
                if i + window < len(dis_matrix):
                    down = i + window;
                if j - window > 0:
                    left = j - window;
                if j + window < len(dis_matrix[0]):
                    right = j + window;

                parzen_nodes = 0;
                for p in range(up, down):
                    for q in range(left, right):
                        parzen_nodes = parzen_nodes + dis_matrix[p][q];
                size = (down - up) * (right - left);
                dis_matrix[i][j] = parzen_nodes/float(size);

#use the geo-based distance to build up the SPT
def SPTGeoDis(filename, map, method, use_kernel=0, bydegree=0):
    #filename = './output/Map/term_location_2011_3.txt';
    #load the position of terms
    #term_locs = loadPoints(filename);
    infile = file(filename);
    term_locs = json.load(infile);
    infile.close();

    #put the positions of terms into bins, 0 means no kernel, 1 means use kernel
    term_matrix = transPoints(term_locs, use_kernel, map, bydegree);
    
    #cal the overlay of term
    #cover_matrix = geoOverlap(term_matrix);

    #normalize the term_matrix
    
    #cal the distance between each pair of terms
    dis_matrix = disOfTerm(term_matrix, method);
    
    outfile = file('./output/Map/geo_dis.txt', 'w');
    json.dump(dis_matrix, outfile);
    outfile.close();
    
    outfile = file('./output/Map/geo_overlap.txt', 'w');
    json.dump(cover_matrix, outfile);
    outfile.close();
    
    return dis_matrix;

#use the geo-based overlap to build up the hierarchy tree
def geoOverlap(term_matrix):
    term_num = len(term_matrix);

    #cover_pairs = {};
    cover_matrix = {};
    for term, matrix in term_matrix.iteritems():
        covers = 0;
        #cover_pairs[term] = [];
        cover_matrix[term] = {};
        for term2, matrix2 in term_matrix.iteritems():
            if term2 == term:
                continue;

            covers = 0;
            sup = 0;
            sub  = 0;
            for i in range(0, len(matrix)):
                for j in range(0, len(matrix[i])):
                    if matrix2[i][j] > 0:
                        sub = sub + 1;

                    if matrix[i][j] > 0:
                        sup = sup + 1;
                        
                        if matrix2[i][j] > 0:
                            covers = covers + 1;

            #the percentage of terms been covered by term1
            cover_matrix[term][term2] = covers/float(sub);
            #print term, term2, covers/float(sup), covers/float(sub);

    return cover_matrix;

def getSons(cover_pairs, father, descents):
    sons = cover_pairs[father];
    if sons != None and sons != []:
        descents = descents + sons;
    
    for son in sons:
        #might exist circle
        if son in descents:
            continue;
        getSons(cover_pairs, son, descents);            
    
    return descents;

def buildHierarchy(cover_pairs):
    new_pairs = {};
    for term, subs in cover_pairs.iteritems():
        descents = [];
        grandsons = [];
        for son in subs:
            grandson = getSons(cover_pairs, son, descents);
            grandsons = grandsons + grandson;

        new_pairs[term] = [];
        for sub in subs:
            if sub in grandsons:
                continue;
            new_pairs[term].append(sub);
    
    for term, subs in new_pairs.iteritems():
        print term.encode('utf-8');
        for sub in subs:
            print '\t' + sub.encode('utf-8');
        print '\n';

    return new_pairs;

def hierarchyGeoMain():
    #user the overlap to build the hierarchy structure
    infile = file('./output/Map/geo_overlap.txt');
    cover_matrix = json.load(infile);
    infile.close();

    cover_pair = {};
    for term1 in cover_matrix.keys():
        cover_pair[term1] = [];
        for term2 in cover_matrix.keys():
            if term1 == term2:
                continue;
            
            #cover matrix is the percentage of term1 covers term2
            if cover_matrix[term1][term2] > 0.7 and cover_matrix[term2][term1] < 0.8:
                cover_pair[term1].append(term2);

    for term, subs in cover_pair.iteritems():
        print term.encode('utf-8');
        for sub in subs:
            print '\t' + sub.encode('utf-8');
        print '\n';
    buildHierarchy(cover_pair);

def kmeansPurity(dis_matrix, cluster_num, truthfile, format='unicode'): 
    accu = K_NN(dis_matrix, truthfile, 1, format);
    
    #kmeans
    sum_puri = 0;
    puri = {};
    outfilename = 'output/cluster_temp.txt';
    iter_num = 1;
    for i in range(0, iter_num):
        cluster, cluster_label = kmeansTokens(dis_matrix, cluster_num);
        
        dumpCluster(cluster, outfilename);

        puri[i] = purityFunc(truthfile, outfilename, format);
        sum_puri = sum_puri + puri[i];
    average_puri = sum_puri/float(iter_num);
    print puri;
    print 'accuracy, average purity=', accu, average_puri;
    return accu, average_puri;

def clusterCoocurMain(infilename, cluster_num, truthfile, format):
    infile = file(infilename);
    dis_matrix = json.load(infile);
    
    for term in dis_matrix.keys():
        count = 0;
        for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
            #print term.encode('utf-8'), term2.encode('utf-8'), dis;
            count = count + 1;
            if count > 10:
                break;

    return kmeansPurity(dis_matrix, cluster_num, truthfile, format);

#cluster the tokens according to their geo-distances
#place: 'US', 'JP'
def clusterGeoDisMain(infilename, method, use_kernel, bb, cluster_num, truthfile, useDegree, format):
    outfilename = './output/Map/clusters.txt';
    dis_matrix = SPTGeoDis(infilename, bb, method, use_kernel, useDegree);
    
    return kmeansPurity(dis_matrix, cluster_num, truthfile, format);
    
    #root = 'earthquake\n';
    #D, path = DijkstraWrap(dis_matrix, root);
   
    #layer_cluster = {};
    #drawTree(root, path, 1, layer_cluster);

def disOfTemp(filename, dis_method, dayorhour='hour'):
    infile = file(filename);
    lines = infile.readlines();
    if dis_method == 'gauss':
        time_unit = json.loads(lines[1]);
    else:
        if dis_method == 'square':
            time_unit = json.loads(lines[2]);
        else:
            time_unit = json.loads(lines[0]);
    infile.close();

    return disOfTemp2(time_unit, dis_method, dayorhour);

def disOfTemp2(term_time_bin, dis_method, dayorhour):
    dis_matrix = {};
    for term1 in term_time_bin.keys():
        dis_matrix[term1] = {};
    
    count = 1;
    for term1 in term_time_bin.keys():
        for term2 in term_time_bin.keys():
            if cmp(term1, term2) > 0:
                continue;

            if cmp(term1, term2) == 0:
                dis_matrix[term1][term2] = 0;
                continue;

            time_bin1 = term_time_bin[term1];
            time_bin2 = term_time_bin[term2];

            dis = disOfDic(time_bin1, time_bin2);
            dis_matrix[term1][term2] = dis;
            dis_matrix[term2][term1] = dis;

    return dis_matrix;

def disOfTemp3(time_unit, dis_method, dayorhour):
    
    print 'term numbers in disOfTemp is', len(time_unit);
    
    max_time = 0;
    for term, bins in time_unit.iteritems():
        sum = 0;
        for time, freq in bins.iteritems():
            sum = sum + freq;
            if int(time) > max_time:
                max_time = int(time);
        
        if sum <= 0:
            continue;

        for time, freq in bins.iteritems():
            bins[time] = freq / float(sum);

    new_units = {};
    for term, bins in time_unit.iteritems():
        array = np.zeros(max_time + 1);
        for time, freq in bins.iteritems():
            array[int(time)] = freq;
        new_units[term] = array;

    if dayorhour == 'day':
        new_units = {};
        for term, bins in time_unit.iteritems():
            max_day = math.ceil(max_time/24);
            array = np.zeros(max_day + 2);
            for time, freq in bins.iteritems():
                time = float(time);
                day = math.ceil(time/24);
                array[day] = array[day] + freq;
            new_units[term] = array;

    dis_matrix = {};
    for term, bins in new_units.iteritems():
        dis = 0;
        dis_matrix[term] = {};
        for term2, bins2 in new_units.iteritems():
            if term2 == term:
                dis_matrix[term][term] = 0;
                continue;
            dis = 0;
            for i in range(0, len(bins)):
                if dis_method == 'KL':
                    if bins[i] != 0 and bins2[i] != 0:
                        dis = dis + math.log(bins[i]/float(bins2[i]))*bins[i]; 
                else:
                    dis = dis + abs(bins[i] - bins2[i]);
            
            dis_matrix[term][term2] = dis;
        count = 0;
        for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
            #print term.encode('utf-8'), term2.encode('utf-8'), dis;
            count = count + 1;
            if count > 10:
               break;

    return dis_matrix;

#cluster the tokens according to their temporal distance
def clusterTmpEventDisMain(infilename, method, cluster_num, truthfile, hourorday, format):
    dis_matrix = disOfTemp(infilename, method, hourorday);

    return kmeansPurity(dis_matrix, cluster_num, truthfile, format);

#cluster the tokens according to their temporal distance
def clusterTmpDisMain(infilename, method, cluster_num, truthfile, hourorday, format):
    #infilename = './output/Map/time_unit_2011_3.txt';
    #temporary file
    #outfilename = './output/Map/clusters.txt';
    dis_matrix = disOfTemp(infilename, method, hourorday);

    return kmeansPurity(dis_matrix, cluster_num, truthfile, format);

    #root = 'earthquake\n';
    #D, path = DijkstraWrap(dis_matrix, root);
   
    #layer_cluster = {};
    #drawTree(root, path, 1, layer_cluster);
    
def normList(user_list):
    sum = 0;
    for user, freq in user_list.iteritems():
        sum = sum + freq;
    
    for user, freq in user_list.iteritems():
        user_list[user] = freq/float(sum);

def user_KLDis(user_list1, user_list2):
    dis = 0;
    for user1, freq1 in user_list1.iteritems():
        if user1 in user_list2.keys():
            freq2 = user_list2[user1];
            if freq2 == 0:
                continue;

            dis = dis + math.log(freq1/freq2)*freq1;

    return dis;

def userIntersection(user_list1, user_list2):
    score = 0;
    for user1, count1 in user_list1.iteritems():
        if user1 in user_list2.keys():
            count2 = user_list2[user1];
            if count2 < count1:
                score = score + count2;
            else:
                score = score + count1;
    return score;

def normMatrix(dis_matrix):
    for term1 in dis_matrix.keys():
        max = 0;
        for term2, count in dis_matrix[term1].iteritems():
            #sum = sum + count;
            if  count > max:
                max = count;

        if max <= 0:
            continue;

        for term2 in dis_matrix.keys():
            if term1 == term2:
                continue;
            if dis_matrix[term1][term2] == 0:
                dis_matrix[term1][term2] = 1000;
            else:    
                dis_matrix[term1][term2] = max/float(dis_matrix[term1][term2]);

    #for term1, count1 in dis_matrix.iteritems():
    #    for term2, count2 in dis_matrix.iteritems():
    #        if term1 == term2:
    #            continue;
    #        if dis_matrix[term1][term2] == 0:
    #            dis_matrix[term1][term2] = 10000; # a large distance
            
def KL_cal(truth_file, dis_matrix):
    cluster, truth_label = loadCluster(truth_file);
    kl_diver = 0;
    kl_count = 0;    
    for key1, a_cluster1 in cluster.iteritems():
        for terms1 in a_cluster1:
            for key2, a_cluster2 in cluster.iteritems():
                if key1 == key2:
                    continue;
                for terms2 in a_cluster2:
                    kl_diver = kl_diver + dis_matrix[term1][term2];
                    kl_count = kl_count + 1;
    
    return kl_diver/float(kl_count);

#user the user graph to cluster the terms
def clusterUserDisMain(infilename, method, cluster_num, truthfile, format):
    #infilename = './output/Map/user_2011_3.txt';
    infile = file(infilename);
    term_user = json.load(infile);
    dis_matrix = {};
    #norm user_lists
    for term, user_list in term_user.iteritems():
        normList(user_list);

    for term1, user_list1 in term_user.iteritems():
        dis_matrix[term1] = {};
        for term2, user_list2 in term_user.iteritems():
            if term1 == term2:
                dis_matrix[term1][term2] = 0;
                continue;
            if method == "KL":
                score = user_KLDis(user_list1, user_list2);
            else:
                score = userIntersection(user_list1, user_list2);
            dis_matrix[term1][term2] = score;
    
    #for displaying
    #for term1 in dis_matrix.keys():
    #    for term2, freq in sorted(dis_matrix[term1].iteritems(), key= lambda (k,v):(v,k)):
    #        print term1.encode('utf-8'), term2.encode('utf-8'), freq;
    #end
    #normalize and reverse the matrix
    normMatrix(dis_matrix);
     
    return kmeansPurity(dis_matrix, cluster_num, truthfile, format);
    
def geoTmpClusterMain():
    infilename = './output/Map/time_unit_2011_3.txt';
    dis_matrix1 = disOfTemp(infilename);
    
    filename = './output/Map/term_location_2011_3.txt';
    dis_matrix2 = SPTGeoDis(filename, 'JP');

    matrix = {};
    for key1 in dis_matrix1.keys():
        matrix[key1] = {};
        for key2 in dis_matrix1.keys():
            matrix[key1][key2] = 0.5*dis_matrix1[key1][key2] + 0.5*dis_matrix2[key1+'\n'][key2+'\n'];
    
    cluster = kmeansTokens(matrix, 6);

    outfile = file('./output/Map/cluster_of_geotmpdis_JPEQ.txt', 'w');
    for key, tokens in cluster.iteritems():
        #outfile.write(key.encode('utf-8') + '\n');
        for token in tokens:
            outfile.write(token.encode('utf-8') + '\t');
        outfile.write('\n\n');
    outfile.close();

def clusterFunc(event, cluster_num, format):
    dirname = './data/event/' + event + '/';
    location_file = dirname + 'term_location.txt';
    time_file = dirname + 'term_time.txt';
    time_event_file = dirname + 'term_time_event.txt';
    user_file = dirname + 'term_user.txt';
    coocur_file = dirname + 'term_coocurence.txt';
    truthfile = dirname + 'truth_cluster.txt'
    bb, tt = getbbtt(event);
    tt = transTime(tt);
    conditional_time_file = dirname + 'term_time_theta.txt';

    purities = {};
    
    #use the time adjusted by windows to cluster
    print 'temporal windows distance...'
    #purities['tmp_gauss_window'] = clusterTmpDisMain(time_event_file, 'gauss', cluster_num, truthfile, 'hour', format);
    #purities['tmp_square_window'] = clusterTmpDisMain(time_event_file, 'square', cluster_num, truthfile, 'hour', format);

    #use co-occurence
    print 'co-ocur.....';
    purities['coocur'] = clusterCoocurMain(coocur_file, cluster_num, truthfile, format);
    
    #use the temporal distance to cluster
    print 'temporal distance...'
    #purities['tmp_abs'] = clusterTmpDisMain(time_file, 'abs', cluster_num, truthfile, 'day', format);
    #purities['tmp_KL'] = clusterTmpDisMain(time_file, 'KL', cluster_num, truthfile, 'hour', format);

    #use the conditional temporal distance to cluster Fre*p(t|theta)
    #purities['tmp_abs'] = clusterTmpDisMain(conditional_time_file, 'abs', cluster_num, truthfile, 'hour', format);
    
    #use the geo distance to cluster
    print 'geo-spatial distance...'
    #purities['geo_abs_noker'] = clusterGeoDisMain(location_file, 'abs', 0, bb, cluster_num, truthfile, 1, format);
    #purities['geo_abs_ker'] = clusterGeoDisMain(location_file, 'abs', 1, bb, cluster_num, truthfile, 1, format);
    
    #purities['geo_kl_noker'] = clusterGeoDisMain(location_file, 'KL', 0, bb, cluster_num, truthfile, 1, format);
    #purities['geo_kl_ker'] = clusterGeoDisMain(location_file, 'KL', 1, bb, cluster_num, truthfile, 1, format);

    #use the user distance to cluster
    #print 'user-distance...'
    #purities['user_abs'] = clusterUserDisMain(user_file, 'abs', cluster_num, truthfile, format);

    outfilename = dirname + 'cluster_purity.txt';
    outfile = file(outfilename, 'a');
    json.dump(purities, outfile);
    outfile.write('\n');
    outfile.close();

def genClusterTruth():
    event = '8_2011_events';
    #events = ['earthquake_JP', 'arab_spring', 'earthquake_NZ', 'gov_shutdown', 'background'];
    events = ['irene', 'jobs_resign', 'earthquake_US', 'arab_spring_late', 'background']
    all_tokens = [];
    out_cluster_file = './data/event/' + event + '/cluster_truth.txt';
    out_file = file(out_cluster_file, 'w');

    for event in events:
        filename_15 = '/home/yuan/lab/duration/data/' + event + '/top15.txt';
        tokens = loadToken(filename_15);
        for token in tokens:
            out_file.write(token + '\n');
        out_file.write('\n');
    out_file.close();

def knn(train_data, test_date, train_labels, K):
    clf = neighbors.KNeighborsClassifier(K)
    clf.fit(train_data, train_labels);
    return clf.predict(test_data);

def accuracy(test_label, predic_label):
    accu = 0;
    for i in range(0, len(test_label)):
        if test_label[i] == predic_label[i]:
            accu = accu + 1;

    return accu/float(len(test_label));

def clusterMain():
    event = '3_2011_tags';
    cluster_num = 100;
    clusterFunc(event, cluster_num, 'unicode');
    return;

    event = 'jpeq_jp';
    cluster_num = 5;
    clusterFunc(event, cluster_num, 'utf-8');

    #all the events co-happend with irene
#    event = 'irene_overall';
#    cluster_num = 3;
#    clusterFunc(event, cluster_num, 'unicode');
        
#    event = 'NBA';
#    cluster_num = 3;
#    clusterFunc(event, cluster_num);

#    event = '3_2011_events';
#    cluster_num = 5;
#    clusterFunc(event, cluster_num, 'unicode');
 
if __name__ == '__main__':
    #genShortPathTreeMain();
    #genMSTMain();
    #hierarchyGeoMain();
    #geoTmpClusterMain();

    #4 cluster method
    #clusterTmpDisMain('abs');
    #clusterGeoDisMain('KL', 1);
    #clusterUserDisMain('abs');
    #clusterTokensMain(False, 4);

    clusterMain();
