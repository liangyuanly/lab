#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, gzip, cjson, json
import fnmatch
import numpy 
import operator
import string
import math
import sys
sys.path.append('utility/')
from common import normalizeDic
from operator import itemgetter
from kmeans import kmeansTokens
import networkx as nx

class DisCalculator:
    @staticmethod
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
       
    @staticmethod
    def disOfArray(array1, array2, method = 'abs'):
        if len(array1) != len(array2):
            print 'dis of array error!'
            return 1000;

        dis = 0.0;
        for i in range(0.0, len(array1)):
            dis += abs(array2[i] - array1[i]);
        
        return dis;

    @staticmethod
    def printClosetPair(dis_matrix, K, rever=False):
        for term in dis_matrix.keys():
            count = 0;
            for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k), reverse = rever):
                print term.encode('utf-8'), term2.encode('utf-8'), dis;
                count = count + 1;
                if count > K:
                    break;
    @staticmethod
    def disOfTemp(term_time_bin):
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

                dis = DisCalculator.disOfDic(time_bin1, time_bin2);
                dis_matrix[term1][term2] = dis;
                dis_matrix[term2][term1] = dis;

        #test
        DisCalculator.printClosetPair(dis_matrix, 20);
        return dis_matrix;

    @staticmethod
    def disOfTempGraph(term_time_bin, weight_edge_threshold = 0):
        graph = nx.Graph();
        for term1 in term_time_bin.keys():
            for term2 in term_time_bin.keys():
                if cmp(term1, term2) > 0:
                    continue;

                if cmp(term1, term2) == 0:
                    continue;

                time_bin1 = term_time_bin[term1];
                time_bin2 = term_time_bin[term2];

                dis = DisCalculator.disOfDic(time_bin1, time_bin2);
                if dis > 0:
                    if 1/dis > weight_edge_threshold:
                        graph.add_edge(term1, term2, {'w': 1/dis})
                        #graph.add_edge(term1.encode('utf-8'), term2.encode('utf-8'), {'w': 1/dis})
                else:
                    graph.add_edge(term1, term2, {'w': 0})
                    #graph.add_edge(term1.encode('utf-8'), term2.encode('utf-8'), {'w': 1000})
        
        return graph;
    
    @staticmethod
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

    @staticmethod
    def disOfTimeGeo(term_matrix, method='abs'):
        term_num = len(term_matrix);

        dis_matrix = {};
        for term, time_locs in term_matrix.iteritems():
            dis = 0;
            dis_matrix[term] = {};
            for term2, time_locs2 in term_matrix.iteritems():
                if term2 == term:
                    dis_matrix[term][term] = 0;
                    continue;
                
                dis = DisCalculator.disOfTimeLocsList(time_locs, time_locs2, 'abs')  
                dis_matrix[term][term2] = dis;
                
            count = 0;
            for term2, dis in sorted(dis_matrix[term].iteritems(), key=lambda (k,v):(v,k)):
                #print term, term2, dis;
                count = count + 1;
                if count > 10:
                    break;

        return dis_matrix;
    
#    @staticmethod
#    def disOfOccur(term_occ):
#        #cal the total count of a term happened with other terms
#        count_term = {};
#        for term1 in term_occ:
#            count = 0;
#            for term2 in term_occ[term1]:
#                count += term_occ[term1][term2];
#
#            count_term[term1] = count;
#
#        sim_matrix = {};
#        for term1 in term_occ:
#            sim_matrix[term1] = {};
#            for term2 in term_occ[term1]:
#                #normalize the term count to get the distance based on co-occur
#                dis1 = term_occ[term1][term2];
#                
#                #wrong name, dis1 actually is the similarity
#                if count_term[term1] < count_term[term2]:
#                    dis1 /= count_term[term1] + 1;
#                else:
#                    dis1 /= count_term[term2] + 1;
#            
#            sim_matrix[term1][term2] = dis1;
#
#        #the similarity matrix
#        return sim_matrix;
    
    @staticmethod
    def disOfOccTimeGeo(sim_occ, dis_tmp, dis_geo, terms):
        dis_matrix = {};
        for term1 in terms:
            dis_matrix[term1] = {};
            for term2 in terms:
                if term1 == term2:
                    dis_matrix[term1][term2] = 0;
                    continue;
               
                sim1 = 100000; #actualy should call it dis1
                if term1 in sim_occ and term2 in sim_occ[term1]:
                    sim1 = sim_occ[term1][term2];
                else:
                    if term2 in sim_occ and term1 in sim_occ[term2]:
                        sim1 = sim_occ[term2][term1];
                
                #get the temporal distance
                dis2 = 10000;
                if term1 in dis_tmp and term2 in dis_tmp[term1]:
                    dis2 = dis_tmp[term1][term2];
                else:
                    if term2 in dis_tmp and term1 in dis_tmp[term2]:
                        dis2 = dis_tmp[term2][term1];

                #get the spatial distance
                dis3 = 10000;
                if term1 in dis_geo and term2 in dis_geo[term1]:
                    dis3 = dis_geo[term1][term2];
                else:
                    if term2 in dis_geo and term1 in dis_geo[term2]:
                        dis3 = dis_geo[term2][term1];

                #use the similarity 
                #new_dis = (dis2 + dis3) / (1+sim1);
    
                #use the distance
                new_dis = sim1*(dis2 + dis3);
                dis_matrix[term1][term2] = new_dis;

        return dis_matrix;

    @staticmethod
    def disOfGeo(term_loc_bin):
        dis_matrix = {};
        for term1 in term_loc_bin.keys():
            dis_matrix[term1] = {};

        for term1 in term_loc_bin.keys():
            for term2 in term_loc_bin.keys():
                if cmp(term1, term2) > 0:
                    continue;
            
                if cmp(term1, term2) == 0:
                    dis_matrix[term1][term2] = 0;
                    continue;
                
                loc_bin1 = term_loc_bin[term1];
                loc_bin2 = term_loc_bin[term2];

                dis = DisCalculator.disOfDic(loc_bin1, loc_bin2);
                dis_matrix[term1][term2] = dis;
                dis_matrix[term2][term1] = dis;
        
        #test
        DisCalculator.printClosetPair(dis_matrix, 20);
        return dis_matrix;
    
    @staticmethod
    def disOfGeoGraph(term_loc_bin, weight_edge_threshold = 0):
        graph = nx.Graph();
        for term1 in term_loc_bin.keys():
            for term2 in term_loc_bin.keys():
                if cmp(term1, term2) > 0:
                    continue;
            
                if cmp(term1, term2) == 0:
                    continue;
                
                loc_bin1 = term_loc_bin[term1];
                loc_bin2 = term_loc_bin[term2];

                dis = DisCalculator.disOfDic(loc_bin1, loc_bin2);
                if dis > 0:
                    if 1/dis > weight_edge_threshold:
                        graph.add_edge(term1, term2, {'w': 1/dis})
                        #graph.add_edge(term1.encode('utf-8'), term2.encode('utf-8'), {'w': 1/dis})
                else:
                    graph.add_edge(term1, term2, {'w': 0})
                    #graph.add_edge(term1.encode('utf-8'), term2.encode('utf-8'), {'w': 1000})
        
        return graph;
    
    @staticmethod
    def weightFromDisMatrix(dis_matrix, edge_weight_thredhold = 0):
        max_dis = 0.0;
        for term1, term_dis in dis_matrix.iteritems():
            for term2, dis in term_dis.iteritems():
                if dis > 0:
                    if 1/dis > edge_weight_thredhold:
                        yield term1, term2, 1/dis;
                
                #if dis > max_dis:
                #    max_dis = dis;
        
        #for term1, term_dis in dis_matrix.iteritems():
        #    for term2, dis in term_dis.iteritems():
        #        wei = (max_dis - dis) / max_dis;
        #        yield term1, term2, wei;

    @staticmethod
    def loadTopTerms(filename, K=1000):
        infile = file(filename);
        lines = infile.readlines();
        array = [];
        for line in lines:
            data = cjson.decode(line);
            array.append((data['tag'], int(data['freq'])));
       
        sort_array = sorted(array, key = itemgetter(1), reverse = True);
        top_terms = [];
        for i in range(0, K):
            term = sort_array[i][0];
            top_terms.append(term);

        return top_terms;

    @staticmethod
    def loadFeatures(filename, top_terms):
        infile = file(filename);
        lines = infile.readlines();
        infile.close();

        term_time_list = {};
        term_loc_list = {};
        for line in lines:
            data = cjson.decode(line);
            tag = data['tag'];
            if tag not in top_terms:
                continue;

            time_list = data['time_bin'];
            loc_list = data['loc_bin'];
            normalizeDic(time_list);
            normalizeDic(loc_list);

            term_time_list[tag] = time_list;
            term_loc_list[tag] = loc_list;

        return term_time_list, term_loc_list;

    @staticmethod
    def getTopTag(term_features, K):
        new_term_features = {};
        array = [];
        for term, features in term_features.iteritems():
            array.append((term, int(features['freq'])));
        sort_array = sorted(array, key = itemgetter(1), reverse = True);

        for i in range(0, K):
            term = sorted[i][0];
            new_term_features[term] = term_features[term];

        return new_term_features;

#def calDisMain():
#    inputfile = 'output/2011_2_8_features';
#    top_terms = loadTopTerms(inputfile, 1000);
#    term_time_list, term_loc_list = loadFeatures(inputfile, top_terms);
#
#    outfilename = 'output/cluster_result';
#    outfile = file(outfilename, 'w');
#    dis_matrix_temp = disOfTemp(term_time_list);
#    cluster, center = kmeansTokens(dis_matrix_temp, 100);
#    print cluster;
#    json.dump(cluster, outfile);
#    outfile.write('\n');
#
#    dis_matrix_geo = disOfGeo(term_loc_list);
#    cluster, center = kmeansTokens(dis_matrix_geo, 100);
#    json.dump(cluster, outfile);
#    outfile.write('\n');
#
#if __name__ == '__main__':
#    calDisMain()
