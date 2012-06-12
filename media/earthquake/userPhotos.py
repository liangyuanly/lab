#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
from getTweets import GetTweets;
simplejson = json
from getTweets import GetTweets
import shutil
from settings import Settings
from Utility import *


def loadPhotos2(dirname):
    dir_list = os.listdir(dirname);
    id_list = [];
    for dir in dir_list:
        sub_dir = dirname + dir + '/';
        files = os.listdir(sub_dir);
        for fname in files:
            if fname[len(fname)-1:len(fname)] == 'txt':
                continue;
            id_list.append(sub_dir + fname);

    return id_list;

def generateInfoForPhoto():
    image_path = Settings.japan_pics_folder + "/backup";
    dirs = os.listdir(image_path);
    image_list = [];
    for dir in dirs:
        path = image_path + dir + '/';
        if os.path.exists(path + 'ImageInfo.txt'):
            os.remove(path + 'ImageInfo.txt');
        list = loadPhotos(path);
        image_list = image_list + list;

    #load the images' tweets and write into file
    tweet_path = Settings.japan_pics_folder + "/backup/tweets/";
    tweet_list = loadTweets3(tweet_path, image_list, outfilename);

def loadTweets(filename):   
    getter = GetTweets();
    tweet_list = [];
    if filename != None:
        infile = file(filename);
        lines = infile.readlines();
        infile.close();
        for line in lines:
            tweet = cjson.decode(line);
            [rel, tweet_info] = getter.parseTweet(tweet);
            id = tweet_info['id'];
            time = tweetTimeToDatetime(tweet_info['time']);
            if time > datetime.datetime(2011, 3, 11, 5, 53, 40) and time < datetime.datetime(2011, 3, 13, 0, 0, 0):
                tweet_list.append(tweet_info);
    return tweet_list;

def classPhotoByUser(tweet_list, user_dic):
    for tweet in tweet_list:
        user = tweet['user'];

        photo_list = user_dic.get(user);
        if photo_list == None:
            user_dic[user] = [];
        
        user_dic[user].append(tweet);
    
    return user_dic;

def putUserPhotos(user_dic, image_list, out_folder):
    for user, list in user_dic.iteritems():
        if len(list) < 5:
            print 'photo num < 2';
            continue;

        if not os.path.exists(out_folder + '/' + str(user)):
            os.mkdir(out_folder + '/' + str(user));

        folder = out_folder + '/' + str(user) + '/';

        outfile = file(folder + 'ImageInfo.txt', 'w');
        for tweet in list:
            filename = genFileName(tweet['id'], tweet['time']);
            for image in image_list:
                if image.find(filename) >= 0:
                    shutil.copy(image, folder + filename + '.jpeg');
                    json.dump(tweet, outfile);
                    outfile.write(tweet['text'].encode('utf-8') + '\n');
                    print image;
        outfile.close();

def photoByUserMain():
    #put the photos into the users' folder
    image_path = Settings.japan_pics_tweets;
    
    files = os.listdir(image_path);
    user_dic = {};
    for afile in files:
        file_name = image_path + afile;
        tweet_list = loadTweets(file_name);
        classPhotoByUser(tweet_list, user_dic);

    #load the image list
    image_list = loadPhotos2(Settings.japan_pics_folder + 'backup/');

    out_folder = './output/TopImage/UserPhoto/';
    putUserPhotos(user_dic, image_list, out_folder);

photoByUserMain();
