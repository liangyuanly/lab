#!/usr/bin/python

import cPickle as p;
import sys
import string

import datetime
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

def interval(a, b):
    f = "%Y-%m-%d %H:%M:%S";
    time1 = datetime.datetime.strptime(a, f);
    time2 = datetime.datetime.strptime(b, f);
    intervaltime = time2 - time1;
    elapse = intervaltime.days * 24 * 3600 + intervaltime.seconds;
    return elapse;

checkin_lines = [];
checkin_num = 0;
def loadfile():
    global checkin_lines, checkin_num;
    infile = open('checkin_data.txt');

    checkin_lines = infile.readlines();
    checkin_num = len(checkin_lines);
    infile.close();

date_map = {};
hour_map = {};
def get_checkin_num(up, down, left, right):
    global date_map, hour_map;
    date_map = {};
    hour_map = {};
    count = 0;
    for i in range(checkin_num):
        line = checkin_lines[i];
        items = line.split('\t');
        mag = float(items[2]);
        log = float(items[3]);
        if mag >= down and mag <= up and log >= left and log <= right:
            count = count + 1;
            time = items[4];
            h = hour(time);
            da = date(time);
            daily_num = date_map.get(da);
            if daily_num == None:
                date_map[da] = 1;
            else:
                date_map[da] = date_map[da] + 1;

            hour_num = hour_map.get(h);
            if hour_num == None:
                hour_map[h] = 1;
            else:
                hour_map[h] = hour_map[h] + 1;
            count = count + 1;
            #if count == 100:
            #    return 100;
    return count;    

#get checkin info for a area
def get_area_checkin():
    global date_map, hour_map;
    loadfile();
    #up = 30.63446111;
    #down = 30.603425;
    #left = -96.36021499;
    #right = -96.3250722;
    up = 40.7708;
    down = 40.7406;
    left = -74.0076;
    right = -73.9602;
    date_map = {};
    hour_map = {};
    outfile = file('timesquare_checkin.txt', 'w');
    outfile.close();
    outfile = file('timesquare_checkin.txt', 'a');

    count = get_checkin_num(up, down, left, right);
    outfile.write(str(count) + '\t' + str(len(date_map.keys())) + '\n');
    for key in date_map.keys():
        outfile.write(str(key)+'\t'+str(date_map[key])+'\t');
    outfile.write('\n');
    for key in hour_map.keys():
        outfile.write(str(key)+'\t'+str(hour_map[key])+'\t');
    outfile.write('\n');
    outfile.close();

get_area_checkin();
