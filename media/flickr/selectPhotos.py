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

def selectPhotosUseTag(dirname, tags):
    dirs = os.listdir(dirname);
    user_set = {};
    for dir in dirs:
        file_name = dirname + dir + '/PhotoInfo.txt';
        infile = file(file_name, 'r');
        lines = infile.readlines();
        for line in lines:
            item = cjson.decode(line);
            title = item["basic1"]["title"].encode('utf-8');
            discription = item["discription"];
            item_tags = item["tags"];
            
            find = 0;
            for tag in tags:
                if(title.find(tag) > 0):
                    find = 1;
                    break;

                if(discription.find(tag) > 0):
                    find = 1;
                    break;
            

