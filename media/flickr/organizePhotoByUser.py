#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import flickrapi 
from hashlib import md5
import urllib, urlparse
import os, cjson
import sys
import datetime
from datetime import timedelta
import time

def getFileName(photo_info):
    times = photo_info['dates']['posted'];
    file_name = datetime.datetime(1970, 1, 1, 0, 0, 0) + timedelta(days = int(times)/(3600*24), seconds = int(times)%(3600*24));
    dir_name = str(file_name.year) + '_' + str(file_name.month) + '_' + str(file_name.day);
            
    url = photo_info['url'];
    post_fix = url[(len(url)-4) : len(url)];
    file_name = photo_info['basic1']['id'] + '_' + file_name.strftime('%d_%m_%y_%H:%M');
    full_name = dir_name + '/' + file_name + post_fix;
    return full_name;


def organizePhotoByUser(dirname):
    #dirs = os.listdir(dirname);
    user_photos = {};
    for i in range(11, 21):
        dir = dirname + '2011_3_' + str(i) + '/';
        filename = dir + "PhotoInfo.txt";
        infile = file(filename);
        lines = infile.readlines();
        for line in lines:
            items = cjson.decode(line);
            user_id = items['basic1']['owner'];
            value = user_photos.get(user_id);
            if value == None:
                user_photos[user_id] = [];
            
            value = (items['basic1']['id'] + '\t' + 
                    items['basic1']['title'].encode('utf-8') + '\t' + 
                    items['location']['latitude'] + '\t' + 
                    items['location']['longitude'] + '\t' + 
                    items['dates']['taken'] + '\t'+ 
                    items['dates']['posted'] + '\t' +
                    getFileName(items) + '\n');
            user_photos[user_id].append(value);
        infile.close();

    outfile = file('./output/UserPhotoList.txt', 'w');
    for user, lines in user_photos.iteritems():
        if len(lines) > 10:
            outfile.write(user + '\n');
            for line in lines:
                outfile.write(line);
            outfile.write('\n');
    outfile.close();

dir_name = '/mnt/chevron/kykamath/data/twitter/twitter_pics/japan/JapanPhoto/';
organizePhotoByUser(dir_name)
