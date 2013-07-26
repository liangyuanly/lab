#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, gzip, cjson, json
import fnmatch
import numpy 
import operator
import string
import math
import sys
sys.path.append('../utility/')
from common import normalizeDic
from operator import itemgetter
from kmeans import kmeansTokens
from metrics import entropy

class FeatureExt:
    @staticmethod
    def selectTermsByEntro(term_timebin, K):
        entro = [];
        for term, timebin in term_timebin.iteritems():
            entro.append([term, entropy(timebin)]);
        
        entro = sorted(entro, key = itemgetter(1));
        if K >= len(entro):
            K = len(entro) - 1;
        
        ret_list = [];
        for i in range(0,K):
            ret_list.append(entro[i][0]);
        
        return ret_list;

    @staticmethod
    def getTopTermFeatures(filename, K):
        term_timebin, term_loc, term_occur = FeatureExt.getFeatures(filename);

        terms = FeatureExt.selectTermsByEntro(term_timebin, K);
        new_timebin = {};
        new_loc = {};
        new_occur = {};
        for term in terms:
            new_timebin[term] = term_timebin[term];
            new_loc[term] = term_loc[term];
            if term in term_occur:
                new_occur[term] = {};
                for term2, fre in term_occur[term].iteritems():
                    if term2 in terms:
                        new_occur[term][term2] = fre;
        return new_timebin, new_loc, new_occur, terms;
        
    @staticmethod
    def getFeatures(filename):
        term_time_bin = {};
        term_loc_bin = {};
        term_occur = {};

        infile = file(filename);
        lines = infile.readlines();
        for line in lines:
            try:
                #line = line[1:len(line)-2];
                key_value = json.loads(line);
                value = int(key_value[1]);
                key = key_value[0];
                items = key.split('_');
                term = items[0];
                if items[1] == 't':
                    time_index = int(items[2]);
                    if term not in term_time_bin:
                        term_time_bin[term] = {};
                    
                    if time_index not in term_time_bin[term]:
                        term_time_bin[term][time_index] = value;
                else:
                    if items[1] == 'l':
                        lat = int(items[2]);
                        lon = int(items[3]);
                        loc_index = str(lat) + '_' + str(lon);
                        if term not in term_loc_bin:
                            term_loc_bin[term] = {};

                        if loc_index not in term_loc_bin[term]:
                            term_loc_bin[term][loc_index] = value;
                    else:
                        term2 = items[1];
                        if term not in term_occur:
                            term_occur[term] = {};
                        
                        if term2 not in term_occur:
                            term_occur[term2] = {};

                        term_occur[term][term2] = value;
                        term_occur[term2][term] = value;
            except: 
                print 'exception', line
        
        for term, time_bin in term_time_bin.iteritems():
            normalizeDic(time_bin);
        for term, loc_bin in term_loc_bin.iteritems():
            normalizeDic(loc_bin);

        return term_time_bin, term_loc_bin, term_occur;
