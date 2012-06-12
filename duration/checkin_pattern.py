#!/usr/bin/python
import json, cjson
import cPickle as p;
import sys
import string
import sys
sys.path.append('../utility/')
from tokenExtract import *
from loadFile import *
from boundingBox import *
from getTweets import GetTweets;
from tweetFilter import *

def hour(a):
    # a:"%Y-%m-%d %H:%M:%S";
    s1 = a.split(' ');
    s2 = s1[1].split(':')
    hour = string.atoi(s2[0]) + 1;
    return hour;

def date(a):
    # a:"%Y-%m-%d %H:%M:%S";
    s1 = a.split(' ');
    s2 = s1[0].split('-')
    date = s2[0]+s2[1]+s2[2];
    return string.atoi(date);

def strToDatetime(str):
    f = "%Y-%m-%d %H:%M:%S";
    time = datetime.datetime.strptime(str, f);
    return time;

def interval(a, b):
    f = "%Y-%m-%d %H:%M:%S";
    time1 = datetime.datetime.strptime(a, f);
    time2 = datetime.datetime.strptime(b, f);
    intervaltime = time2 - time1;
    elapse = intervaltime.days * 24 * 3600 + intervaltime.seconds;
    return elapse;

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

def checkinsOfbb(filename, bbs, outfilename):
    infile = file(filename);
    lines = infile.readlines();
    place_checkins = {};

    count = 0;
    for line in lines:
        tweet = decodeLine(line);
        for place, bb in bbs.iteritems():
            if isTweetInbb(bb, tweet):
                print place, line;
                weekday =  tweet['time'].weekday();
                hour = tweet['time'].time().hour;
                #change from utc time to local time
                if tweet['time'].date().month < 3 or tweet['time'].date().month > 11:
                    hour = hour + bb[4];
                    if hour < 0:
                        hour = hour + 24;
                        weekday = weekday - 1;
                        if weekday < 0:
                            weekday = weekday + 7;
                else:
                    #summer time
                    hour = hour + bb[4] + 1;
                    if hour < 0:
                        hour = hour + 24;
                        weekday = weekday - 1;
                        if weekday < 0:
                            weekday = weekday + 7;
                
                checkins = place_checkins.get(place);
                if checkins == None:
                    checkins = {};
                    place_checkins[place] = checkins;

                checkin_aday = checkins.get(weekday);
                if checkin_aday == None:
                    checkin_aday = {};
                    checkins[weekday] = checkin_aday;
                
                freq = checkin_aday.get(hour);
                if freq == None:
                    checkin_aday[hour] = 1;
                else:
                    checkin_aday[hour] = checkin_aday[hour] + 1;

    outfile = file(outfilename, 'w');
    json.dump(place_checkins, outfile);
    outfile.close();

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

def loadCheckinsMain():
    filename = './data/place_bb.txt';
    place_bb = loadPlacebb(filename);
    outfilename = './output/checkins_bb.txt';
    checkinsOfbb('./data/checkin_data.txt', place_bb, outfilename);

def changeFormat():
    filename = './output/checkins_bb.txt';
    infile = file(filename);
    place_checkins = json.load(infile);
    filename2 = './output/checkins_bb2.txt';
    outfile = file(filename2, 'w');
    for place, checkins in place_checkins.iteritems():
        outfile.write(place + '\n');
        for weekday, day_checkins in checkins.iteritems():
            outfile.write(weekday + '\n');
            json.dump(day_checkins, outfile);
            outfile.write('\n');
        outfile.write('\n');

#the begin and end time the users are involved in a location
def getUserTweetsTime(tweets, bb, user_timelist):
    count = 0;
    for tweet in tweets:
        if not isTweetInbb(tweet, bb):
            continue;

        time = tweet['time'];
        time = tweetTimeToDatetime(time);

        user = tweet['user'];
        timelist = user_timelist.get(user);

        count = count + 1;
        print user, len(user_timelist), count;

        if timelist == None:
            timelist = [];
            user_timelist[user] = timelist;
        
        if len(timelist) == 0:
            timelist.append(time);
        else:
            if len(timelist) == 1:
                #repeative tweets
                if time == timelist[0]:
                    continue;

                if time < timelist[0]:
                    stop_time = timelist[0];
                    timelist.append(stop_time);
                    timelist[0] = time;
                else:
                    timelist.append(time);
            else:
                if len(timelist) == 2:
                    if time < timelist[0]:
                        timelist[0] = time;
                    if time > timelist[1]:
                        timelist[1] = time;

#cal the duration users stay in an event
def getUserDura(user_duraTimelist):
    user_dura = {};
    for user, timelist in user_duraTimelist.iteritems():
        #if len(timelist) == 1:
            #print 'only one checkin';

        if len(timelist) == 2:
            interval = timelist[1] - timelist[0];
            user_dura[user] = interval.days*24*3600 + interval.seconds;

    return user_dura;
       
loadCheckinsMain();
changeFormat();
