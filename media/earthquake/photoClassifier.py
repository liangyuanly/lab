#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import fnmatch
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#from matplotlib.dates import epoch2num, date2num
#import dateutil.parser
import numpy as np
import operator
import string
import math
#import getTweets;
from getTweets import GetTweets
import shutil
from settings import Settings
from Utility import *

tag_list = ['残','緊急', '爆発','停電','混雑','震','裂','摇','崩', 'earthquake', '災', '死', '惨', 'damage', '燃', '難', '煙', '지진', '壊'];

#load the tweets for the images
def loadTweets3(path, image_list, filename):
    getter = GetTweets();
    tweet_list = [];
    outfile = file(filename, 'w');
    
    image_set = [];
    for image in image_list:
        index2 = string.rfind(image, '_');
        if index2 >= 0:
            id = np.uint64(image[index2+1:len(image)]);
            image_set.append(id);

    image_set = set(image_set);
 
    
    dirList=os.listdir(path);
    for tweet_file in dirList:
        file_name = path+tweet_file;
        print file_name;
                
        infile = file(file_name);
        lines = infile.readlines();
        infile.close();
        for line in lines:
            tweet = cjson.decode(line);
            [rel, tweet_info] = getter.parseTweet(tweet);
            id = tweet_info['id'];
            if id in image_set:
                image_set.remove(id);
                #tweet_info['text'] = tweet_info['text'].encode('utf-8');
                tweet_list.append(tweet_info);
                
                s = json.dumps(tweet_info, encoding="utf-8");
                outfile.write(s+'\n');

    outfile.close();
    return tweet_list;


#load the tweets for the images
def loadTweets2(path, image_list, filename):
    getter = GetTweets();
    tweet_list = [];
    #outfile = file('output/JP_earthquake_image_tweets.txt', 'w');
    outfile = file(filename, 'w');
    #files = os.listdir(path);
    image_set = [];
    for image in image_list:
        index2 = string.rfind(image, '_');
        if index2 >= 0:
            id = np.uint64(image[index2+1:len(image)]);
            image_set.append(id);

    image_set = set(image_set);
 
    from_day = 10
    to_day = 12
    year = 2011;
    month_from = 3;
    month_to = 4; #<4

    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/' + str(year) + '/';
    for month in range(month_from, month_to):
        day_begin = from_day;
        day_end = to_day;

        for days in range(day_begin, day_end): # Japan earthquake
            path = main_path+str(month)+'/'+str(days)+'/';
            if not os.path.isdir(path):
                continue;
    
            dirList=os.listdir(path);
        
            for tweet_file in dirList:
                file_name = path+tweet_file;
                print file_name;
                
                for tweet in getter.iterateTweetsFromGzip(path+afile):
                    [rel, tweet_info] = getter.parseTweet(tweet);
                    id = tweet_info['id'];
                    if id in image_set:
                        image_set.remove(id);
                        tweet_info['text'] = tweet_info['text'].encode('utf-8');
                        tweet_list.append(tweet_info);
                
                        s = json.dumps(tweet_info, encoding="utf-8");
                        outfile.write(s+'\n');

    outfile.close();
    return tweet_list;


#load the tweets for the images
def loadTweets(path, image_list, filename):
    getter = GetTweets();
    tweet_list = [];
    #outfile = file('output/JP_earthquake_image_tweets.txt', 'w');
    outfile = file(filename, 'w');
#   path='/mnt/chevron/bde/Data/TweetData/GeoTweets/2011/3dd/11/11_3_2011_0:00-Tweets.txt.gz';

    for image in image_list:
        if len(image) < 1:
            continue;

        index1 = string.find(image, '_');
        hour = int(image[0:index1])
        hour = hour - 6;
        if hour < 0:
            hour = hour + 24;
        index2 = string.rfind(image, '_');
        print image;
        if index2 >= 0:
            id = np.uint64(image[index2+1:len(image)]);
        else:
            continue;

        name = '*_'+str(hour)+':*.gz';
        files = os.listdir(path);
        find = 0;
        idx = -1;
        tweet_info = {};
        for afile in files:
            if find == 1:
                break;
            if fnmatch.fnmatch(afile, name) ==  False:
                continue;

            for tweet in getter.iterateTweetsFromGzip(path+afile):
                [rel, tweet_info] = getter.parseTweet(tweet);
                if tweet_info['id'] == id:
                    find = 1;
                    break;

        print image, find;
        tweet_info['image'] = image;
        if find <= 0:
            tweet_info['text'] = ' ';
            
        print tweet_info['text'].encode("utf-8");
        tweet_list.append(tweet_info);
        s = json.dumps(tweet_info, encoding="utf-8");
        outfile.write(s+'\n');

    outfile.close();
    return tweet_list;

def photoClassify(tweet_list):
    label = []; 
    relevant = 0;
    for tweet in tweet_list:
        relevant = 0;
        if tweet['text'] == ' ': #not count
            label.append(2);
            continue;
        for tag in tag_list:
            if string.find(tweet['text'].encode('utf-8'), tag) != -1:
                print tag;
                relevant = 1;
                break;
        label.append(relevant);

    return label;

def precisionCal(label_std, label):
    cor_count = 0;
    recall_cor_count = 0;
    recall_count = 0;
    pre_count = 0;
    all_count = len(label_std);
    all_num = 0;
    for i in range(0, all_count):
        if label == 2: #not count
            continue;

        all_num = all_num + 1;
        if label[i] == label_std[i]:
            cor_count = cor_count + 1;

        if label_std[i] == 1:
            recall_count = recall_count + 1;
            if label[i] == 1:
                print 'true positive', i;
                recall_cor_count = recall_cor_count + 1;
        
        if label[i] == 1:
            pre_count = pre_count + 1;
            if label_std[i] == 0:
                print 'false positive', i;

    recall = recall_cor_count / float(recall_count);
    precision = recall_cor_count / float(pre_count);
    corr = cor_count / float(all_num);

    return [corr, recall, precision];

def loadLabel(filename):
    infile = file(filename, 'r');
    lines = infile.readlines();
    label = [];
    for line in lines:
        if len(line) < 7:
            continue;
        li = string.split(line[0:7], ' ');
        for i in li:
            label.append(int(i));
   
    return label;

def loadImageTweets(filename):
    infile = file(filename, 'r');
    lines = infile.readlines();
    tweet_list = [];
    getter = GetTweets();
    for i in range(1,len(lines)):
        line = lines[i];
        tweet = cjson.decode(line);
        rel, tweet = getter.parseTweet(tweet);
        print tweet['id'], tweet['text'].encode('utf-8');
        tweet_list.append(tweet);
    return tweet_list;

def generateInfoForPhoto():
    image_path = './data/03-11-cluster/';
    dirs = os.listdir(image_path);
    image_list = [];
    for dir in dirs:
        path = image_path + dir + '/';
        if os.path.exists(path + 'ImageInfo.txt'):
            os.remove(path + 'ImageInfo.txt');
        list = loadPhotos(path);
        image_list = image_list + list;

    #load the images' tweets and write into file
    tweet_path = "/mnt/chevron/kykamath/data/twitter/twitter_pics/japan/backup/tweets/";
    outfilename =  'output/image_tweets_temp.txt';
    tweet_list = loadTweets3(tweet_path, image_list, outfilename);

    #read the image tweets
    #image_tweet_file = 'output/image_tweets_temp.txt';
    #tweet_list = loadImageTweets(image_tweet_file);
    
    #put the tweets in the files
    for dir in dirs:
        path = image_path + dir + '/';
        file_name = path + 'ImageInfo.txt';
        outfile = file(file_name, 'a');
        
        list = loadPhotos(path);
        for image in list:
            index2 = string.rfind(image, '_');
            if index2 >= 0:
                id = np.uint64(image[index2+1:len(image)]);
            else:
                continue;

            for tweet_info in tweet_list:
                if id == tweet_info['id']:
                    tweet_info['text'] = tweet_info['text'].encode('utf-8');
                    json.dump(tweet_info, outfile, encoding='utf-8');
                    outfile.write('\n');
                    outfile.write(tweet_info['text']+'\n')
                    break;
        outfile.close();

def classifyPhotoes():
    #image_path = './data/2011-3-11-part/';
    image_path = './data/2011_3/';
    label_path = './data/photoLabel.txt';
    image_list = loadPhotos(image_path);
    image_list.sort();
    label_std = loadLabel(label_path);

    #write imagetweets into a file
    tweet_path='./data/tweets/';
    filename = 'output/JP_earthquake_image_tweets.txt';
    tweet_list = loadTweets(tweet_path, image_list, filename);
    
    #load the image tweets
    image_tweet_file = 'data/image_tweet.txt';
    tweet_list = loadImageTweets(image_tweet_file);
    label = photoClassify(tweet_list);

    [corr, recall, precision] = precisionCal(label_std, label);
    print corr, recall, precision;

def loadTopSentence(dirname):
    files = os.listdir(dirname);
    tweet_list = {};
    for filename in files:
        if os.path.isdir(dirname + filename):
            continue;
        infile = file(dirname + filename);
        lines = infile.readlines();
        tweet_list[filename] = [];
        for line in lines:
            if len(line) < 100:
                continue;
            index = line.rfind('"id":');
            if index < 0:
                continue;
            index2 = line.find('}', index);
            if index2 < 0:
                continue;
            sub_line = line[0:index2+1];
            print sub_line;
            tweet_info = cjson.decode(sub_line);
            tweet_list[filename].append(tweet_info);

    return tweet_list;

#2011-03-10_23:06:49_45983978028662784
def getTopImage(photos, tweets):
    id_list = {};
    for photo in photos:
        index = photo.rfind('_');
        if index > 0 and index < len(photo) - 6:
            id = int(photo[index+1:len(photo)-5]);
            id_list[id] = photo;

    out_folder = './output/TopImage/Image/';
    outfile = file(out_folder + "ImageInfo.txt", 'w')
    date_dic = {};
    for key, tweet_list in tweets.iteritems():
        for tweet in tweet_list:
            id = tweet['id'];
            if id in id_list.keys():
                #copy the photos into a folder
                index = id_list[id].rfind('/');
                name = id_list[id][index+1 : len(id_list[id])];
                #get the top photos for each day
                date = name[0:10];
                if date_dic.get(date) == None:
                    date_dic[date] = 1;
                else:
                    date_dic[date] = date_dic[date] + 1;
                if date_dic[date] > 20:
                    continue;
                
                shutil.copy(id_list[id], out_folder + 'top10/' + name);
                print key, out_folder + 'top10/' + name;
                
                json.dump(tweet, outfile, encoding = "utf-8");
                outfile.write('\n');
                outfile.write(tweet["text"].encode('utf-8'));
                outfile.write('\n');

    outfile.close();

def getTopImageMain():
    image_dir = Settings.japan_pics_folder + '/backup/';
    photos = loadPhotos2(image_dir);

    tweet_dir = './output/TopImage/';
    tweets = loadTopSentence(tweet_dir);

    getTopImage(photos, tweets);

def getClusterToken(cluster_file):
    infile = file(cluster_file);
    lines = infile.readlines();
    i = 0;
    cluster_dic = {};
    while i < len(lines):
        center = lines[i];
        cluster = lines[i+1];
        tokens = cluster.split('\t');
        for j in range(0, len(tokens)-1):
            tokens[j] = unicode(tokens[j], 'utf-8');

        cluster_dic[center[0:len(center)-1]] = tokens;

        i = i + 2;    
    return cluster_dic;

def getClusterPhoto(cluster_dic, photos_tweets, image_folder):
    filename = './data/stop_words.txt';
    stop_words = loadStopwords(filename);

    id_list = [];
    for tweet in photos_tweets:
        #tokens = tokenize(tweet['text'], 'Japanese', stop_words);
        for key, cluster in cluster_dic.iteritems():
            #score = similarity2(cluster, tokens);
            score = similarity3(cluster, tweet['text']);
            if score >= 1:
                print key;
                #for token in tokens:
                #    print token.encode('utf-8');
                print tweet['text'].encode('utf-8');
                name = genFileName(tweet['id'], tweet['time']);
                sub_folder = '/mnt/chevron/yuan/pic/layer_cluster/' + key + '/';
                if not os.path.exists(sub_folder):
                    os.mkdir(sub_folder);
                
                try:
                    shutil.copy(image_folder + name + '.jpeg', sub_folder + name + '.jpeg');
                except:
                    print "copy exception";
                    pass;

def getClusterPhotoMain():
    cluster_file = './output/TopSentence/cluster.txt';
    cluster_dic = getClusterToken(cluster_file);

    photo_file = './output/TopImage/Image/ImageInfo.txt'; 
    tweets = loadPhotoInfo(photo_file);

    image_folder = './output/TopImage/Image/'; 
    getClusterPhoto(cluster_dic, tweets, image_folder);

def getSPTClusterPhotoMain():
    SPT_file = './output/TopSentence/layer_cluster.txt';
    infile = file(SPT_file);
    layer_cluster = json.load(infile);

    cluster_dic = {};
    for layer, clusters in layer_cluster.iteritems():
        for node, acluster in clusters.iteritems():
            if acluster != []:
                key = str(layer) + node;
                cluster_dic[key] = acluster;
                cluster_dic[key].append(key);
    
    #read the image tweets
    image_tweet_file = Settings.japan_pic_tweets_w + '/2011_3_11';
    #image_tweet_file = 'output/image_tweets_temp.txt';
    tweets = loadImageTweets(image_tweet_file);
    
    #photo_file = Setting.japan_pics_folder + 'tweets/2011-3-11';
    #photo_file = './output/TopImage/Image/ImageInfo.txt'; 
    #tweets = loadPhotoInfo(photo_file);

    image_folder =  Settings.japan_pic_folder_w + '/2011_3_11/';
    #image_folder = './output/TopImage/Image/'; 
    getClusterPhoto(cluster_dic, tweets, image_folder);    

def getRetweetImage(image_tweets, tweet_list):
    image_ids = {};
    for tweet in image_tweets:
        image_ids[tweet['id']] = tweet;
        tweet['retweeted_num'] = 0;

    for tweet in tweet_list:
        if tweet['retweet'] == True:
            id = tweet['retweet_from']
            if id in image_ids.keys():
                images_ids[id]['retweeted_num'] = images_ids[id]['retweeted_num'] + 1;

def getRetweetedImageMain():
    image_tweet_file = Settings.japan_pic_tweets_w + '/2011_3_11';
    for tweet in image_tweets:
        if tweet['retweeted_num'] > 0:
            #shutil.copy(tweet['path'], )
            print tweet;

getTopImageMain();
#generateInfoForPhoto();
#getClusterPhotoMain();
#getSPTClusterPhotoMain();
