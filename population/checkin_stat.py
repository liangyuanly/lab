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
def interval(a, b):
    f = "%Y-%m-%d %H:%M:%S";
    time1 = datetime.datetime.strptime(a, f);
    time2 = datetime.datetime.strptime(b, f);
    intervaltime = time2 - time1;
    elapse = intervaltime.days * 24 * 3600 + intervaltime.seconds;
    return elapse;

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

# ues the number of checkins in the recent month as the weight 3
def get_weight3(begin_item_index, user_checkin_num, cur_item):
    #user_checkin_list = stored_map[key];
    #user_checkin_num = user_checkin_list[0];
    #begin_item_index = user_checkin_list[1];
    global stored_array;
    begin_item = stored_array[begin_item_index].split('\t');
    end_item = stored_array[begin_item_index+user_checkin_num-1].split('\t');

    valid_checkin_num = 0;
    for k in range(begin_item_index, begin_item_index+user_checkin_num-1):
        item = stored_array[k].split('\t');
        temp_dura = interval(item[4], cur_item[4]);
        if abs(temp_dura) < 3600*24*15:
            #tweet_type = foursquare_array[k].split('\t');
            #if tweet_type[1] == 'foursquare\n':
            valid_checkin_num = valid_checkin_num + 1;

        if temp_dura < -3600*24*15:
            break;
    return valid_checkin_num;
 
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

        # the checkin list of a specific user in the this venue
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
        #for j in range(0, len(list)):
        j = -1;
        while j < len(list) - 1:
            j = j + 1;
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
                    if abs(inter) < 600: # if less than 10 munites
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
            # the number of interval checkins between somewhere else and this venue
            d = 1;
            
            # if the duration is calculated according to the area
            # find the next checkin of this user when the checkin is out of the area
            global area_dura, down, up, a1, b1, a2, b2;
            if area_dura == 1:
                # the first checkin of this user checked in whereesle
                p = next_id + d;
                flag = 0;
                while p < begin_item_index + user_checkin_num:
                    item = stored_array[p].split('\t');
                    mag = float(item[2]);
                    log = float(item[3]);
                    log = -log;
                   
                    if log < a1*mag + b1 and log > a2*mag + b2 and mag < up and mag > down:
                        p = p + 1;
                        d = d + 1;
                        continue;
                    flag = 1;
                    break;
                if flag == 0 and p == begin_item_index + user_checkin_num:
                    continue;

            # use the successive two checkin of the users to cal duration
            items2 = stored_array[next_id+d].split('\t')
            items1 = stored_array[i].split('\t'); 

            if items2[0] != items1[0]: #the checkin is belong to the other
                continue;
            if len(items1) <=4 or len(items2) <=4:
                continue;

            # just use the foursquare data
            tweet_type2 = foursquare_array[next_id+d].split('\t');
            tweet_type1 = foursquare_array[i].split('\t');
            # check whether this data comes from foursquare
            if tweet_type1[1] != 'foursquare\n' or tweet_type2[1] != 'foursquare\n':
                continue;

            time1 = items1[4];
            time2 = items2[4];
            elapse = interval(time1, time2);
            
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
            
            #record to the checkin time 
            h = hour(time1);
            duration.append(str(h)+'_'+str(elapse));
            weight.append(user_checkin_num);
            weight.append(user_checkin_dura);
            # add the number of closed(closed to the current checkin) checkins as the weight
            weight.append(valid_checkin_num);
    outfile = file('top_venue_duration.txt', 'a');
    outfile.write(venue_key);
    for i in duration:
        outfile.write(str(i)); outfile.write('\t');
    outfile.write('\n');
    outfile.close();
    print len(duration);

    outfile = file('top_venue_weight.txt', 'a');
    outfile.write(venue_key);
    for i in weight:
        outfile.write(str(i)); outfile.write('\t');
    outfile.write('\n');
    outfile.close();
    print len(weight);

    outfile = file('top_venue_period.txt', 'a');
    outfile.write(venue_key);
    for i in period:
        outfile.write(str(i)); outfile.write('\t');
    outfile.write('\n');
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
        outfile.write(name+str(len(ids))+'\n');
        outfile.close();

        outfile = file('top_venue_weight.txt', 'a');
        outfile.write(name+str(len(ids))+'\n');
        outfile.close();


        outfile = file('top_venue_period.txt', 'a');
        outfile.write(name+str(len(ids))+'\n');
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

date_map = {};
hour_map = {};
down = 0;
up = 0;
a1 = 0;
b1 = 0;
a2 = 0;
b2 = 0;
area_dura = 0;
def newyork_venues_dura():
    global stored_array, date_map, hour_map;
    global down, up, a1, b1, a2, b2, area_dura;
    area_dura = 1;
    up = 40.7983;
    down = 40.7003;
    a1 = -0.7352;
    b1 = 103.9673;
    a2 = -0.7352;
    b2 = 103.9170;
    venue_map = {};
    date_map = {};
    hour_map = {};
    count = 0;
    venue_tmp_map = {};
    for line in stored_array:
        item = line.split('\t');
        venue_key = item[6];
        if venue_key == '\n':
            continue;
        if len(item) > 2:
            mag = float(item[2]);
            log = float(item[3]);
            log = -log;
            if log < a1*mag + b1 and log > a2*mag + b2 and mag < up and mag > down :
                # record the checkin num in this area
                time = item[4];
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
                
                # compute the durations in this area
                rs = venue_tmp_map.get(venue_key);
                if rs != None:
                    continue;
                venue_tmp_map[venue_key] = 1;
                
                duration_stat(venue_key);
                #if count >= 2:
                #    return 2;
    return count;    

def newyork_dura():
    outfile = file('top_venue_duration.txt', 'w');
    outfile.close();
    outfile = file('top_venue_period.txt', 'w');
    outfile.close();
    outfile = file('top_venue_weight.txt', 'w');
    outfile.close();    
    
    outfile = file('newyork_checkin.txt', 'w');
    outfile.close();
    outfile = file('newyork_checkin.txt', 'a');
 
    # load the arrays and maps
    get_checkin('stat.txt');
 
    count = newyork_venues_dura();
    global stored_array, date_map, hour_map;
    outfile.write(str(count) + '\t' + str(len(date_map.keys())) + '\n');
    for key in date_map.keys():
        outfile.write(str(key)+'\t'+str(date_map[key])+'\t');
    outfile.write('\n');
    for key in hour_map.keys():
        outfile.write(str(key)+'\t'+str(hour_map[key])+'\t');
    outfile.write('\n');
    outfile.close();

# another method to cal the duration of new york
#direc indicate whether we need to consider the leave direction
# -1 indicate the left, 1 indicate the right
def newyork_dura2(direc=0):
    # load the arrays and maps
    get_checkin('stat.txt');
 
    # newyork area
    up = 40.7983;
    down = 40.7003;
    a1 = -0.7352;
    b1 = 103.9673;
    a2 = -0.7352;
    b2 = 103.9170;
    
    duration = [];
    weight = [];
    count = 0;
    global stored_array, date_map, hour_map;
    for key in stored_map.keys():
        user_checkin = stored_map[key];
        checkin_num = user_checkin[0];
        checkin_begin_item = user_checkin[1];
        begin_item = stored_array[checkin_begin_item].split('\t');
        end_item = stored_array[checkin_begin_item+checkin_num-1].split('\t');
        user_checkin_dura = 0;
        if(len(begin_item) > 5 and len(end_item) > 5):
            user_checkin_dura = interval(begin_item[4], end_item[4]);
       
        #for i in range(checkin_begin_item, checkin_begin_item+checkin_num):
        i = checkin_begin_item;
        while i < checkin_begin_item + checkin_num:
            item = stored_array[i];
            item = item.split('\t');
            mag1 = float(item[2]);
            log1 = float(item[3]);
            log1 = -log1;
            time1 = item[4];
            
            j = i + 1;
            if log1 < a1*mag1 + b1 and log1 > a2*mag1 + b2 and mag1 < up and mag1 > down :
                leave_flag = 0;
                time = item[4];
                h = hour(time);
                da = date(time);

                #record the duration in this area
                for j in range(i+1, checkin_begin_item+checkin_num):
                    item = stored_array[j];
                    item = item.split('\t');
                    mag2 = float(item[2]);
                    log2 = float(item[3]);
                    log2 = -log2;
                    time2 = item[4];           
                    #skip the successive checkins in this area 
                    if log2 < a1*mag2 + b1 and log2 > a2*mag2 + b2 and mag2 < up and mag2 > down :
                        continue;

                    # only consider the leave direction is left
                    if direc == -1:
                        if log2 <= a2*mag2 + b2:
                            continue;
                    if direc == 1:
                        if log2 > a2*mag2 + b1:
                            continue;
                    if j < checkin_begin_item+checkin_num:
                        leave_flag = 1;
                        dura = interval(time1, time2);
                        duration.append(str(h)+'_'+str(dura));
                        weight.append(checkin_num);
                        weight.append(user_checkin_dura);
                        weight3 = get_weight3(checkin_begin_item, checkin_num, item);
                        weight.append(weight3); 
                        j = j + 1;
                        count = count + 1;
                        print str(key) +' '+ str(i) + ' ' + str(j-1);
                        break;

                # record the checkin num in this area (the ones who used to leave this area)
                if leave_flag == 1:
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

            i = j;
        #if count >= 10:
        #    break;
    outfile1 = file('newyork_duration.txt', 'w');
    outfile2 = file('newyork_weight.txt', 'w');
    outfile3 = file('newyork_checkin2.txt', 'w');
    for i in duration:
        outfile1.write(str(i)); outfile1.write('\t');
    outfile1.write('\n');
    outfile1.close();
    
    for i in weight:
        outfile2.write(str(i)); outfile2.write('\t');
    outfile2.write('\n');
    outfile2.close();

    for key in date_map.keys():
        outfile3.write(str(key)+'\t'+str(date_map[key])+'\t');
    outfile3.write('\n');
    for key in hour_map.keys():
        outfile3.write(str(key)+'\t'+str(hour_map[key])+'\t');
    outfile3.write('\n');
    outfile3.close();


import string
#load_checkin();    
#find_top_venue(10000);
#extract_venueid_by_name();
#duration_of_top_venue();
#extract_venue_type();
#newyork_dura();
newyork_dura2(-1);
print 'caculate duration complete!';
