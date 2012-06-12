#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
simplejson = json
import ast
import random
import sys
sys.path.append('../utility/')
from tokenExtract import *
from boundingBox import *
from event_usercount import *
from event_duration import *
import cPickle as pickle;

def interval(time1, time2):
    intervaltime = time2 - time1;
    elapse = intervaltime.days * 24 * 3600 + intervaltime.seconds;
    return elapse;

def strToDatetime(str):
    f = "%Y-%m-%d %H:%M:%S";
    time = datetime.datetime.strptime(str, f);
    return time;

def loadPlacebb(filename):
    infile = file(filename);
    lines = infile.readlines();
    place_bb = {};
    for line in lines:
        if line[len(line)-1] == '\n':
            line = line[0:len(line)-1];
        items = line.split(',');
        name = items[0];
        #down up left right
        bb = [float(items[2]), float(items[1]), float(items[3]), float(items[4]), float(items[5])];
        place_bb[name] = bb;

    return place_bb;

def decodeLine(line):
    items = line.split('\t');
    tweet = {};
    tweet['user'] = items[0];
    tweet['id'] = items[1];
    tweet['geo'] = [float(items[2]), float(items[3])];
    tweet['time'] = strToDatetime(items[4]);
    tweet['text'] = items[5];
    tweet['venue'] = items[6];
    
    return tweet;

def addToDic(dic, key, value):
    #the first one should be put into the checkins
    freq = dic.get(key);
    if freq == None:
        dic[key] = value;
    else:
        dic[key] = dic[key] + value;

def isTweetInManhattan(place_bb, tweet):
    isInArea = 0;
    for place, bb in place_bb.iteritems():
        if isTweetInbb(bb, tweet):
            isInArea = 1;
            break;

    return isInArea;

#calculate the duration for manhattan 
def putUserInBinsManhattan(tweets, user_tweetIdx, loc_checkin, loc_checkout, loc_user_freq, loc_post, loc_newposts, loc_duration, place_bb, isFilter=0):
    #the outer bb of manhattan
    out_bb = place_bb['out bb'];
    del place_bb['out bb'];

    place = 'up manhattan';
    duration_out_out = [];
    duration_in_out = [];
    duration_out_in = [];
    for user, idx in user_tweetIdx.iteritems():
        number = idx[0];
        begin_idx = idx[1];

        i = begin_idx;
        while i < begin_idx + number:
            tweet = decodeLine(tweets[i]);

            chosen = 0;
            #first find a checkin outside the manhattan in the right corner for queen
            #in the left side for new jersy
            if isTweetInbb2(out_bb, -1, 0, tweet) and not isTweetInManhattan(place_bb, tweet):
                chosen = 1;
            if chosen == 0:
                i = i + 1;
                continue;
            else:
                first_out_tweet = tweet['time'];
                i = i + 1;
                tweet = decodeLine(tweets[i]);

            isInArea = isTweetInManhattan(place_bb, tweet); 
           
            #find the seccessive tweets happend in the manhattan
            if isInArea == 0:
                i = i + 1;
                continue;
            else:
                checkins = loc_checkin[place];
                checkouts = loc_checkout[place];
                user_freq = loc_user_freq[place];
                posts = loc_post[place];
                newposts = loc_newposts[place];
                duration = loc_duration[place];

                time = tweet['time'];
                index = time.time().hour - 5; #-5 is the time zone 
                
                if index < 0: # indicating that is our required test data
                    index = index + 24;

                #the first one should be put into the checkins
                addToDic(checkins, index, 1);
                    
                #all the posts should be added into the post of users
                addToDic(posts, index, 1);

                #the first one hour's post should be added to the new users' posts
                addToDic(newposts, index, 1);

                #record current index
                first_index = index;
                last_index = index;
                first_time = time;
                last_time = time;

                i = i + 1;
                freq = 1;
                while(i < begin_idx + number):
                    tweet = decodeLine(tweets[i]);

                    time = tweet['time'];
                    isStillIn = 0;
                    for place, bb in place_bb.iteritems():
                        if isTweetInbb(bb, tweet):
                            isStillIn = 1;
                    
                    #if it's not in the region, break;
                    if isStillIn == 0:
                        break;
                    else:
                        tweet = decodeLine(tweets[i]);
                        freq = freq + 1;
                        time = tweet['time'];
                        #time = tweetTimeToDatetime(time);
                        index = time.time().hour - 5; #-5 is the time zone 
                
                        if index < 0: # indicating that is our required test data
                            index = index + 24;

                        #all the posts should be added into the post of users
                        addToDic(posts, index, 1);

                        #the first one hour's post should be added to the new users' posts
                        if index == first_index:
                            addToDic(newposts, index, 1);
                
                        last_index = index;
                        last_time = time;
                        i = i + 1;
                
                #the first checkout tweet should be out side the manhattan
                tweet = decodeLine(tweets[i]);
                if not isTweetInbb2(out_bb, -1, 0, tweet):
                    print 'not checkout in ther outer bb';
                    i = i + 1;
                    continue;
                else:
                    i = i + 1;
                    second_out_tweet = tweet['time'];

                #record the duration
                print 'training data', first_time, last_time, first_out_tweet, second_out_tweet, freq;
                duration.append(interval(first_time, last_time));
                duration_out_out.append(interval(first_out_tweet, second_out_tweet));
                duration_in_out.append(interval(first_time, second_out_tweet));
                duration_out_in.append(interval(first_out_tweet, last_time));
                #add the frequency
                addToDic(user_freq, freq, 1);
               
                #record the last index as the checkout
                if last_index >= 0 and first_index >= 0:
                    print 'test data', first_time, last_time;
                    addToDic(checkouts, last_index, 1);
    
    return duration_out_out, duration_in_out, duration_out_in;

def putUserInBinsLoc(tweets, user_tweetIdx, loc_checkin, loc_checkout, loc_user_freq, loc_post, loc_newposts, loc_duration, periods, place_bb, isFilter=0):
    #get the begin and end time
    begin_time = periods[0];
    end_time = periods[1];
    
    for user, idx in user_tweetIdx.iteritems():
        number = idx[0];
        begin_idx = idx[1];

        i = begin_idx;
        while i < begin_idx + number:
            tweet = decodeLine(tweets[i]);
            flag = 0;
            for place, bb in place_bb.iteritems():
                if isTweetInbb(bb, tweet):
                    flag = 1;
                    checkins = loc_checkin[place];
                    checkouts = loc_checkout[place];
                    user_freq = loc_user_freq[place];
                    posts = loc_post[place];
                    newposts = loc_newposts[place];
                    duration = loc_duration[place];

                    time = tweet['time'];
                    #time = tweetTimeToDatetime(time);
                    index = getIndexForBinHour(begin_time, end_time, time);
                    
                    if index >= 0: # indicating that is our required test data
                        #the first one should be put into the checkins
                        addToDic(checkins, index, 1);
                        
                        #all the posts should be added into the post of users
                        addToDic(posts, index, 1);

                        #the first one hour's post should be added to the new users' posts
                        addToDic(newposts, index, 1);
                    

                    #record current index
                    first_index = index;
                    last_index = index;
                    first_time = time;
                    last_time = time;

                    i = i + 1;
                    freq = 1;
                    while(i < begin_idx + number):
                        tweet = decodeLine(tweets[i]);

                        time = tweet['time'];
                        #exceed one day, then break
                        #if interval(last_time, time) > 24*3600:
                        #    break;
                        
                        #if it's not in the region, break;
                        if not isTweetInbb(bb, tweet):
                            break;
                        else:
                            tweet = decodeLine(tweets[i]);
                            freq = freq + 1;
                            time = tweet['time'];
                            #time = tweetTimeToDatetime(time);
                            index = getIndexForBinHour(begin_time, end_time, time);
                            if index >= 0:
                                #all the posts should be added into the post of users
                                addToDic(posts, index, 1);

                                #the first one hour's post should be added to the new users' posts
                                if index == first_index:
                                    addToDic(newposts, index, 1);
                    
                            last_index = index;
                            last_time = time;
                            i = i + 1;
                    
                    #that data is used for training
                    if last_index == -1 and first_index == -1:
                        #record the duration
                        print 'training data', first_time, last_time, freq;
                        duration.append(interval(first_time, last_time));

                        #add the frequency
                        addToDic(user_freq, freq, 1);
                   
                    #record the last index as the checkout
                    if last_index >= 0 and first_index >= 0:
                        print 'test data', first_time, last_time;
                        addToDic(checkouts, last_index, 1);
                        
                    break;  #end if isTweetInbb
            if flag == 0:  
                i = i + 1; #end for place, bb in...

# the array storing the 20 million checkins
stored_array = [];
# the map of<userid, checkin-index>, the begining and number of checkin-index 
stored_map = {};
# the map of<venueid, checkin-index list>
stored_venuemap = {};
# the array of foursquare data
foursquare_array = [];
 
def get_checkin(filename1, filename2):
    infile = open(filename1);
    stored_array = infile.readlines();
    infile.close();

    infile = file(filename2);
    stored_map = pickle.load(infile);
    #stored_venuemap = pickle.load(infile);
    infile.close();

    return [stored_array, stored_map];

def getLocationUserMain():
    tweets, user_idx = get_checkin('data/checkin_data.txt', 'data/stat.txt');

    place_bb = loadPlacebb('data/mahanttan_bb.txt');

    loc_checkins = {};
    loc_checkouts = {};
    loc_posts = {};
    loc_newposts = {};
    loc_user_freq = {};
    loc_duration = {};
    for place in place_bb.keys():
        loc_checkins[place] = {};
        loc_checkouts[place] = {};
        loc_posts[place] = {};
        loc_newposts[place] = {};
        loc_user_freq[place] = {};
        loc_duration[place] = [];

    #putUserInBinsLoc(tweets, user_idx, loc_checkins, loc_checkouts, loc_user_freq, loc_posts, loc_newposts, loc_duration, g_period, place_bb, 0);
    duration_out_out, duration_in_out, duration_out_in = putUserInBinsManhattan(tweets, user_idx, loc_checkins, loc_checkouts, loc_user_freq, loc_posts, loc_newposts, loc_duration, place_bb, 0);
    
    for place in place_bb.keys():
        dir = 'data/' + place + '/';
        if not os.path.exists(dir):
            os.makedirs(dir);

        outfile = file(dir + 'checkout_post_manhattan.txt', 'w');
        json.dump(loc_checkins[place], outfile);
        outfile.write('\n');
        json.dump(loc_checkouts[place], outfile);
        outfile.write('\n');
        json.dump(loc_posts[place], outfile);
        outfile.write('\n');
        json.dump(loc_newposts[place], outfile);
        outfile.write('\n');
        json.dump(loc_user_freq[place], outfile);
        outfile.write('\n');
        json.dump(loc_duration[place], outfile);
        outfile.write('\n');
        json.dump(duration_out_out, outfile);
        outfile.write('\n');
        json.dump(duration_in_out, outfile);
        outfile.write('\n');
        json.dump(duration_out_in, outfile);

        outfile.close();

#use the 2011-01 as the test data
g_period = [datetime.datetime(2011,1,1,0,0,0), datetime.datetime(2011,1,30,23,59,59)];

getLocationUserMain();
