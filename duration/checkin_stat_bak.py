#!/usr/bin/python

import cPickle as p;
import sys
import string

def load_checkin():
    infile = open('checkin_data.txt');
    map = {};
    venue_map = {};

    count = 0;
    lines = infile.readlines();
    line_count = len(lines);
#    item_array = [[]];

    print line_count;
    for i in range(0,line_count):
        line = lines[i];
        items = line.split('\t');
        
        if(len(items) < 7):
            continue;
	
        key = items[0];
        list = map.get(key);
        if list == None:
            list = [0,i];
            map[key] = list;
        list[0] = list[0] + 1;

        venue_key = items[6];

        if(venue_key != '\n'):
            venue_list = venue_map.get(venue_key);
            if venue_list == None:
                venue_list = [];
                venue_map[venue_key] = venue_list;
            venue_list.append(i);

        if i%1000 == 0:
            print i;
    
    infile.close();
    outfile = file('stat.txt', 'w');
#    p.dump(item_array, outfile);
    p.dump(map, outfile);
    p.dump(venue_map, outfile);
    outfile.close;
    print 'load complete!';

# the array storing the 20 million checkins
stored_array = [];
# the map of<userid, checkin-index>, the begining and number of checkin-index 
stored_map = {};
# the map of<venueid, checkin-index list>
stored_venuemap = {};
# the array of foursquare data
foursquare_array = [];

def get_checkin(filename):
    global stored_array, stored_map, stored_venuemap, foursquare_array;
    
    infile = open('checkin_data.txt');
    stored_array = infile.readlines();
    outfile = file(filename, 'r');
#    stored_array = p.load(outfile);
    stored_map = p.load(outfile);
    stored_venuemap = p.load(outfile);
    outfile.close();
    infile.close();

    #load the tweet type
    infile = file('ordered_tweet_type.txt');
    foursquare_array = infile.readlines();
    infile.close();

import datetime
# b - a
def interval(a, b):
    f = "%Y-%m-%d %H:%M:%S";
    time1 = datetime.datetime.strptime(a, f);
    time2 = datetime.datetime.strptime(b, f);
    intervaltime = time2 - time1;
    elapse = intervaltime.days * 24 * 3600 + intervaltime.seconds;
    return elapse;

import string
# add the tweet type to the stored array
def add_tweet_type():
    global stored_array;
    infile = file('checkin_sources.txt');
    lines = infile.readlines();
    tweet_map = {};
    for line in lines:
        item = line.split('\t');
        key = string.atol(item[0]);
        tweet_map[key]=item[1];
    infile.close();

    outfile = file('ordered_tweet_type.txt', 'w');
    outfile.close();
    outfile = file('ordered_tweet_type.txt', 'a');
    for line in stored_array:
        item = line.split('\t');
        if len(item) > 2:
            tweet_id = string.atol(item[1]);
            type = tweet_map.get(tweet_id);
            if type != None:
                outfile.write(item[1]+'\t'+type);
            #type = 'forsquare\n';
            #if type != None:
            #    line = line[0:(len(line)-1)] + '\t' + type[0:(len(type)-1)];
    outfile.close();        
    
duration = [];
period = [];
def duration_stat(venue_key):
    global stored_array, stored_map, stored_venuemap, foursquare_array;
    global duration, period;
    checkin_list = stored_venuemap[venue_key];
    user_map = {};
    duration = [];
    period = [];
    weight = [];
    lines_count = len(stored_array);
    #get the check in number of 24 hours

    #get the userlist of a specific venue
    for i in checkin_list:
        item_line = stored_array[i];
        item = item_line.split('\t');
        userid = item[0];
        userlist = user_map.get(userid);
        if userlist == None:
            userlist = [];
            user_map[userid] = userlist;
        userlist.append(i);
    
    #use the user list to calculate the period and duration
    for key in user_map.keys():
        user_checkin_list = stored_map[key];
        user_checkin_num = user_checkin_list[0];
        begin_item_index = user_checkin_list[1];
        begin_item = stored_array[begin_item_index].split('\t');
        end_item = stored_array[begin_item_index+user_checkin_num-1].split('\t');
        user_checkin_dura = 0;
        if(len(begin_item) > 5 and len(end_item) > 5):
            user_checkin_dura = interval(begin_item[4], end_item[4]);

        list = user_map[key];
        list.sort();
        leng = len(list);
        period_weight = [];
        if leng <= 1:
            period.append(0);
        else:
            for i in range(0, leng - 1):
                items2 = stored_array[list[i+1]].split('\t');
                items1 = stored_array[list[i]].split('\t');
                if len(items1) > 4 and len(items2) > 4:
                    time2 = items2[4];
                    time1 = items1[4];
                    elapse = interval(time1, time2);
                    period.append(elapse);

        next_id = 0;
        #pre_foursquare_index = -1;
        for j in range(0, len(list)):
            i = list[j];
            if i > lines_count:
                print 'error!only once is ok';
                continue;
            
            # if the checkins are successive or interval is too low, probablely is just noise
            k = j;
            while k < len(list)-1:
                real_k = list[k];
                real_k_next = list[k+1];
                item1 = stored_array[real_k].split('\t');
                item2 = stored_array[real_k_next].split('\t');
                inter = interval(item1[4], item2[4]);
                if real_k == real_k_next-1:
                    if abs(inter) < 900: # if less than 15 munites
                        k = k+1;
                        print 'noise 0 ' + str(inter);
                        continue;
                else:
                    if abs(inter) < 60: # is less than 1 minutes
                        k = k+1;
                        print 'noise 1 ' + str(inter);
                        continue;
                break;
            j = k;      
            next_id = list[k];

            # use the successive two checkin of the users to cal duration
            items2 = stored_array[next_id+1].split('\t')
            items1 = stored_array[i].split('\t'); 

            if items2[0] != items1[0]: #the checkin is belong to the other
                continue;
            if len(items1) <=4 or len(items2) <=4:
                continue;

            # just use the foursquare data
            tweet_type2 = foursquare_array[next_id+1].split('\t');
            tweet_type1 = foursquare_array[i].split('\t');
            # check whether this data comes from foursquare
            if tweet_type1[1] != 'foursquare\n' or tweet_type2[1] != 'foursquare\n':
                continue;

            time1 = items1[4];
            time2 = items2[4];
            elapse = interval(time1, time2);
            duration.append(elapse);
            # add the total checkin num and the interval between the first and last checkin of the user 
            # as the weight of this checkin
            weight.append(user_checkin_num);
            weight.append(user_checkin_dura);

            valid_checkin_num = 0;
            for k in range(begin_item_index, begin_item_index+user_checkin_num-1):
                item = stored_array[k].split('\t');
                temp_dura = interval(item[4], items2[4]);
                if abs(temp_dura) < 3600*24*15:
                    tweet_type = foursquare_array[k].split('\t');
                    if tweet_type[1] == 'foursquare\n':
                        valid_checkin_num = valid_checkin_num + 1;

                if temp_dura < -3600*24*15:
                    break;
            
            # add the number of closed(closed to the current checkin) checkins as the weight
            weight.append(valid_checkin_num);


    outfile = file('top_venue_duration.txt', 'a');
    #outfile.write(venue_key);
    for i in duration:
        outfile.write(str(i)); outfile.write('\t');
    #outfile.write('\n');
    outfile.close();
    print len(duration);

    outfile = file('top_venue_weight.txt', 'a');
    for i in weight:
        outfile.write(str(i)); outfile.write('\t');
    outfile.close();
    print len(weight);

    outfile = file('top_venue_period.txt', 'a');
    #outfile.write(venue_key);
    for i in period:
        outfile.write(str(i)); outfile.write('\t');
    #outfile.write('\n');
    outfile.close;
    print len(period);

def find_top_venue(threshold):
    list = [[]];
    for key in stored_venuemap.keys():
        if len(stored_venuemap[key]) > threshold:
            list.append([len(stored_venuemap[key]), key]);
    list.sort();
    outfile = file('top_venue.txt', 'w');
    for i in list:
        if len(i) < 2:
            continue;
        outfile.write(str(i[1]) + '\t' + str(i[0]));
        outfile.write('\n')
    outfile.write('\n');
    outfile.close();
	 

def extract_venueid_by_name():
    infile = file('500_checkins_venues.txt');
    name_map = {};
    while 1:
        line = infile.readline();
        if not line or len(line) < 2:
            break;
        list = [];
        line = line[0:(len(line)-1)];
        name_map[line] = list;
    infile.close();

    infile = file('225k_checkin_place.txt');
    lines = infile.readlines();
    infile.close();
    leng = len(lines);
    print leng;
    for i in range(0, leng):
        item_line = lines[i];
        item = item_line.split('\t');
        name = item[3];
        fullname = item[4];
        flag = 0;
        for venuename in name_map.keys():
            if name.find(venuename) != -1 or fullname.find(venuename)!= -1:
                id = item[0];
                name_map[venuename].append(id);
                break;
        print i;

    outfile = file('venue_name_ids.txt', 'w');
    for key in name_map.keys():
        outfile.write(key+'\n');
        list = name_map[key];
        for id in list:
            outfile.write(id+'\t');
        outfile.write('\n');

    outfile.close();

def distance_cal(dis1, dis2):
    dis1 = dis1.split('_');
    cor1x = string.atof(dis1[0]);
    cor1y = string.atof(dis1[1]);

    dis2 = dis2.split('_');
    cor2x = string.atof(dis2[0]);
    cor2y = string.atof(dis2[1]);

    return (cor2x-cor1x)**2 + (cor2y-cor1y)**2;


def distance_stat(venue_key):
    global stored_array, stored_map, stored_venuemap, foursquare_array;
    global user_coor;
    checkin_list = stored_venuemap[venue_key];
    user_map = {};
    distance = [];
    frequency = [];
    latency = [];
    checkin = [];
    lines_count = len(stored_array);
    #get the userlist of a specific venue
    for i in checkin_list:
        item_line = stored_array[i];
        item = item_line.split('\t');
        userid = item[0];
        userlist = user_map.get(userid);
        if userlist == None:
            userlist = [];
            user_map[userid] = userlist;
        userlist.append(i);
    
    #calculate the distance for the user_list
    for key in user_map.keys():
        # the user's location
        user_loc = user_coor.get(key);
        if user_loc == None:
            print key, 'doesnot exist!';
            continue;

        # the venue's location
        visit_list = user_map[key];
        items = stored_array[visit_list[0]];
        items = items.split('\t');
        corr = items[2]+'_'+items[3];

        dis = distance_cal(user_loc, corr);
        distance.append(dis);

        # calculate the checkin number of a user in this venue during the 3 months
        frequency.append(len(visit_list));
        
        # calculate the latence between the last and first checkin
        item1 = stored_array[visit_list[0]];
        item1 = item1.split('\t');
        item2 = stored_array[visit_list[len(visit_list)-1]];
        item2 = item2.split('\t');
        dura = interval(item1[4], item2[4]);
        latency.append(dura);

        # calculate the ratio of the user's checkin in this venus to his total checkin
        two_items = stored_map[key];
        checkin_num =  two_items[0];
        checkin.append(checkin_num);

    return (distance, frequency, latency, checkin);    

user_coor = {};
#calculate the distance between user and his checkin_venue
def distance_of_top_venue():
    global user_coor;
    # load the arrays and maps
    get_checkin('stat.txt');
 
    #load the users' location cordinates
    infile = file('../dataset/traj_user_stats.txt');
    lines = infile.readlines();
    for i in range(0, len(lines)):
        line = lines[i];
        items = line.split('\t');
        userid = items[0];
        userid = userid[1:len(userid)];
        log = items[4][0:len(items[4])-3];
        coors = items[3] + '_' + log;
        user_coor[userid] = coors;
   
    outfile = file('top_venue_distance.txt', 'w');
    outfile.close();
    
    infile = file('venue_name_ids.txt', 'r')
    while 1:
        name = infile.readline();
        if not name:
            break;
        line = infile.readline();
        ids = line.split('\t');
        
        distances = [];
        frequency = [];
        latency = [];
        total_checkin = [];
        outfile = file('top_venue_distance.txt', 'a');
        print 'process:', name;
        for id in ids:
            if id == '\n':
                continue;
            id = id + '\n';
            print id;
            (distances_tmp, frequency_tmp, latency_tmp, total_checkin_tmp) = distance_stat(id);
            distances = distances + distances_tmp;
            frequency = frequency + frequency_tmp;
            latency = latency + latency_tmp;
            total_checkin = total_checkin + total_checkin_tmp;
        outfile.write(name);
        for i in range(0, len(distances)):
            outfile.write(str(distances[i]));
            outfile.write('\t');
        outfile.write('\n');
        for i in range(0, len(frequency)):
            outfile.write(str(frequency[i]));
            outfile.write('\t');
        outfile.write('\n');
        for i in range(0, len(latency)):
            outfile.write(str(latency[i]));
            outfile.write('\t'); 
        outfile.write('\n');
        for i in range(0, len(total_checkin)):
            outfile.write(str(total_checkin[i]));
            outfile.write('\t');
        outfile.write('\n');
        outfile.write('\n');
        outfile.close();

import os
def duration_of_top_venue():
    outfile = file('top_venue_duration.txt', 'w');
    outfile.close();
    outfile = file('top_venue_period.txt', 'w');
    outfile.close();
    outfile = file('top_venue_weight.txt', 'w');
    outfile.close();
    
    # load the arrays and maps
    get_checkin('stat.txt');

    infile = file('venue_name_ids.txt', 'r')
    while 1:
        name = infile.readline();
        if not name:
            break;
        line = infile.readline();
        ids = line.split('\t');
        
        outfile = file('top_venue_duration.txt', 'a');
        outfile.write(name);
        outfile.close();

        outfile = file('top_venue_weight.txt', 'a');
        outfile.write(name);
        outfile.close();


        outfile = file('top_venue_period.txt', 'a');
        outfile.write(name);
        outfile.close();

        print 'process:', name;
        for id in ids:
            if id == '\n':
                continue;
            id = id + '\n';
            print id;
            duration_stat(id);

        outfile = file('top_venue_duration.txt', 'a');
        outfile.write('\n');
        outfile.close();

        outfile = file('top_venue_weight.txt', 'a');
        outfile.write(name);
        outfile.close();

        outfile = file('top_venue_period.txt', 'a');
        outfile.write('\n');
        outfile.close();
 
def duration_of_top_place():
    get_checkin('stat.txt');
    infile = file('top_venue.txt', 'r')
    while 1:
        line = infile.readline();
        if not line:
            break;
        duration_stat(line);
        line = infile.readline();
 
def user_checkin_interval():
    get_checkin('stat.txt');
    outfile = file('user_checkin_interval.txt', 'w');
    outfile.close();
    outfile = file('user_checkin_interval.txt', 'a');
    
    intervals = [];
    for key in stored_map.keys():
        list = stored_map[key];
        begin_item_index = list[1];
        item_num = list[0];
        #only count the users the number of whose checkins > n
        if item_num > 1000:
            for i in range(begin_item_index+1, begin_item_index+item_num):
                inter = interval(stored_array[i], stored_array[i-1]);
                intervals.append(inter);
    outfile.write(key+'\n');
    for i in range(0, len(intervals)):
        outfile.write(intervals[i]+'\t');
    outfile.write('\n');
    outfile.close();


def extract_venue_type():
    venue_file = file('500_checkins_venues.txt', 'r')
    infile = file('venue.txt', 'r');
    outfile = file('venue_type.txt', 'w');
    venues = infile.readlines();
    num = len(venues);
    while 1:
        line = venue_file.readline();
        line = line[0:len(line)-1];
        if not line:
            break;
        for i in range(1, num):
            venue = venues[i];
            venue = venue.split('\t');
            if(len(venue) < 10):
                continue;
            if(venue[1].lower().find(line.lower())!= -1):
                outfile.write(line+'\t'+venue[9]+'\n');
                break;
        line = venue_file.readline();
    venue_file.close();
    infile.close();
    outfile.close();

import string
alg = 6;
if alg == 1:
    load_checkin();    
if alg == 2:
    find_top_venue(10000);
if alg == 3:
    extract_venueid_by_name();
if alg == 4:
    duration_of_top_venue();
if alg == 5:
    extract_venue_type();
if alg == 6:
    distance_of_top_venue();
print 'caculate duration complete!';
