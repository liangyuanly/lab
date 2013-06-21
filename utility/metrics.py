#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
#import numpy as np
import operator
import string
import math
import random
from common import normalizeDic
from kmeans import centerTokensDis

def entropy(time_bin):
    normalizeDic(time_bin);
    entro = 0;
    for time, fre in time_bin.iteritems():
        if fre > 0:
            entro -= fre*math.log(fre);

    return entro;

def DBIndex(dis_matrix, clusters):
    centers, aver_dis = centerTokensDis(dis_matrix, clusters);
    DB = 0.0;
    for i in aver_dis:
        DB_i_max = 0;
        for j in aver_dis:
            if i == j:
                continue;
            
            dis = aver_dis[i] + aver_dis[j];
            if centers[i] in dis_matrix and centers[j] in dis_matrix[centers[i]]:
                center_dis = dis_matrix[centers[i]][centers[j]];
            else:
                print centers[i], centers[j], 'donot have distance in DBIndex';
                center_dis = 2.0;

            if center_dis > 0 and dis/center_dis > DB_i_max:
                DB_i_max = dis/center_dis;

        DB += DB_i_max;

    return DB/float(len(clusters));
        

def disOfCluster(dis_matrix, clusters):
    total_dis = 0;
    count = 0.0;
    for idx, cluster in clusters.iteritems():
        for term1 in cluster:
            for term2 in cluster:
                count += 1;
                if term1 in dis_matrix and term2 in dis_matrix[term1]:
                    total_dis += dis_matrix[term1][term2];
                else:
                    print term1, term2, 'donot have distance in term similarity'
                    total_dis += 2;

    return total_dis/count;
