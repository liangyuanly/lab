#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import fnmatch
#import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
import ast
from tinysegmenter import *
from operator import itemgetter
import random

g_stop_symbol = [' ', '\t', '\n', '.', ',', ':', ';', '?', '"', '-', '!', '(', ')', '。', '，', '\\', '/', '！', '；', '‘', '“','［', '］', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '？', '_', '@'];

g_segmenter = TinySegmenter();

def tokenize(text, language, stop_words):
    # tokenize
    if language == 'Japanese':
        tokens = g_segmenter.tokenize(text);
    else:
        text = string.lower(text);
        tokens = text.split(' ');
    
    sel_tokens = {};
    sel_tokens['TotalTokenNum'] = 0;
    for token in tokens:
        token = string.lower(token);
        token = token.strip();

        #token = token.encode('utf-8');        
        if token == '' or token == ' ' or token == '\t' or token == '\n':
            continue;

        end = len(token) - 1;
        while end >= 0 and (token[end] in g_stop_symbol):
            token = token[0:end];
            end = end - 1;
                
        if token == '':
            continue;

        begin = 0;
        while begin >= 0 and begin < len(token) and (token[begin] in g_stop_symbol):
            begin = begin + 1;
            if begin < len(token) - 1:
                token = token[begin:len(token)];
            else:
                if begin == len(token) - 1:
                    token = '';
                break;

        if token in stop_words:
            continue;
                
        if token.find('http') >= 0:
            continue;
                
        if token == '' or token == ' ' or token == '\t' or token == '\n':
            continue;

        if len(token) < 2:
            continue;
            
        freq = sel_tokens.get(token);
        if freq == None:
            sel_tokens[token] = 1;
        else:
            sel_tokens[token] = sel_tokens[token] + 1;

        sel_tokens['TotalTokenNum'] = sel_tokens['TotalTokenNum'] + 1;

    return sel_tokens;


def tokenize2(text, language, stopwords = None):
    # tokenize
    if language == 'Japanese':
        tokens = g_segmenter.tokenize(text);
    else:
        text = string.lower(text);
        #tokens = text.split(' ');
        #find all the word whoes length is larger or equal to 3
        tokens = re.findall(r'w{3,}', text)

    sel_tokens = {};
    for token in tokens:
        if stopwords != None:
            if token in stopwords:
                continue;

        freq = sel_tokens.get(token);
        if freq == None:
            sel_tokens[token] = 1;
        else:
            sel_tokens[token] = sel_tokens[token] + 1;

        sel_tokens['TotalTokenNum'] = sel_tokens['TotalTokenNum'] + 1;

        sel_tokens.append(token);
       
    return sel_tokens;

# token and text
def similarityCal(token, text):
    text = string.lower(text);
    if text.find(token) >= 0:
        return 1;
    return 0;

def similarityCal2(token, tweetInfo, isUseTag):
    if isUseTag == 0:
        text = tweetInfo['text']
        text = string.lower(text);
        if text.find(token) >= 0:
            return 1;
        return 0;
    else:
        tags = tweetInfo['hashtag']
        if token in tags:
            return 1;
        return 0;

def loadStopwords(filename):
    in_file = file(filename);
    lines = in_file.readlines();
    stop_words = [];
    mark = 0;
    for line in lines:
        line = line.strip();
   
        if line == "unicode":
            mark = 1;
            continue;
        
        if mark > 0:
            line = unicode(line, 'utf-8');
        if line == '' or line == ' ' or line == '\n' or line == '\t':
            continue;
    
        if line[len(line)-1] == '\n' or line[len(line)-1] == '\t':
            line = line[0:len(line)-1];
 
        stop_words.append(line);

    return stop_words;
