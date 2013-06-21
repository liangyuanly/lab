#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json

def purityOfCluster(cluster1, cluster2):
    cluster_lable= {};
    label = 1;
    for key, a_cluster in cluster1.items():
        for term in a_cluster:
            cluster_lable[term] = label;
        label += 1;

    purity_num = 0;
    for key, a_cluster in cluster2.items():
        mixed_item = {};
        for term in a_cluster:
            if not term in cluster_lable:
                continue;

            label = cluster_lable[term];
            if mixed_item.get(label) == None:
                mixed_item[label] = 0;
            mixed_item[label] = mixed_item[label] + 1;

        max_purity = 0;
        for label, freq in mixed_item.iteritems():
            if freq > max_purity:
                max_purity = freq;

        purity_num = purity_num + max_purity;

    return purity_num / float(len(cluster_lable));

def purity(cluster_truth, cluster):
    purity_num = 0;
    for key, a_cluster in cluster.iteritems():
        mixed_item = {};
        for term in a_cluster:
            if not term in cluster_truth:
                continue;

            label = cluster_truth[term];
            if mixed_item.get(label) == None:
                mixed_item[label] = 0;
            mixed_item[label] = mixed_item[label] + 1;
        max_purity = 0;
        for label, freq in mixed_item.iteritems():
            if freq > max_purity:
                max_purity = freq;

        purity_num = purity_num + max_purity;

    return purity_num / float(len(cluster_truth));

def closest(term, dis_matrix, sel_tokens):
    min_dis = 10000;
    chosen_term = '';
    for term2, dis in dis_matrix[term].iteritems():
        if term == term2:
            continue;
            
        if dis < min_dis and term2 in sel_tokens:
            min_dis = dis;
            chosen_term = term2;
    return chosen_term;

def K_NN(dis_matrix, truth_file, K, format='unicode'):
    cluster, truth_label = loadCluster(truth_file, format);
    #k-nn
    accu = 0;
    for term in dis_matrix:
        if term not in truth_label:
            continue;

        chosen_term = closest(term, dis_matrix, truth_label);
        if chosen_term == '':
            continue;

        chosen_cluster = truth_label[chosen_term];
        truth_cluster = truth_label[term];
        
        if chosen_cluster == truth_cluster:
            accu = accu + 1;

    return accu/float(len(truth_label));

def purityFunc(truth_file, cluster_file, format='unicode'):
    cluster, truth_label = loadCluster(truth_file, format);
    cluster, label = loadCluster(cluster_file, format);

    purity_ratio = purity(truth_label, cluster);
    return purity_ratio;

