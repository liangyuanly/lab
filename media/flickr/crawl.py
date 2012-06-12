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

api_key = '482af3991aff842411bc407df69554a1';
secret = 'e53a58406c2b308d';
flickr = flickrapi.FlickrAPI(api_key, secret);

class Photo:
    url = '';
    title = '';
    tags = [];
    time = '';
    lon = '';
    lat = '';
    owner = '';
   
global g_tags;

def genRandomUsers(user_set):
    count = 0;
    bbox = {"long_left":129.5, "lati_down":30.4, "long_right":147.0, "lati_up":45.4};
    while count < 10:
        photos = flickr.photos_getRecent(per_page = 100, page = 100);
        for photo in photos[0]:
            photo_info = getPhotoInfo(photo, bbox, None);
            if photo_info != None:
                user = photo_info['basic1']['owner'];
                if user_set.get(user) == None:
                    user_set[user] = 0;
                    count = count + 1;
                    print 'gen random user = ', user;

#craw photos by users
def crawlPhotosByUser(user_set, date_from, date_to):
    while 1:
        for user in user_set.keys():
            if user_set[user] == 1:
                continue;

            print 'dealing with user = ', user;
            #first get this users' photo 
            photos = flickr.people_getPublicPhotos(user_id = user, min_upload_date=date_from, max_upload_date=date_to, page=10);
            bbox = {"long_left":129.5, "lati_down":30.4, "long_right":147.0, "lati_up":45.4};
            timesp = {"from":date_from, "to":date_to};
            for photo in photos[0]:
                photo_info = getPhotoInfo(photo, bbox, timesp);
                if photo_info != None:
                    getPhoto(photo_info);

            #then get this users' contact users
            contact_list = flickr.contacts_getPublicList(user_id = user, pages="10", per_page = "1000");
            for contact in contact_list[0]:
                if user_set.get(contact.get('nsid')) == None:
                    user_set[contact.get('nsid')] = 0;

            user_set[user] = 1;
        
        genRandomUsers(user_set);

def genInitSet(dirname):
    dirs = os.listdir(dirname);
    user_set = {};
    for dir in dirs:
        file_name = dirname + dir + '/PhotoInfo.txt';
        infile = file(file_name, 'r');
        lines = infile.readlines();
        for line in lines:
            item = cjson.decode(line);
            user = item["basic1"]["owner"];
            user_set[user] = 0;
    return user_set;

#craw photos by area
def crawlPhotosInPeriod(date_from, date_to):
    global g_tags;
    photo_set = {};
    index = 1;
    while 1:
        photos = flickr.photos_search(bbox='129.5,30.4,147.0,45.4', min_upload_data=date_from, max_upload_date=date_to, per_page = 500, page = index);
        #photos = flickr.photos_search(tags='boston', lat='42.355056', lon='-71.065503', radius='5')
        count = 0;
        for photo in photos[0]:
            print 'title = ', photo.attrib['title']
            #photo_info = photo.attrib;
            photo_info = getPhotoInfo(photo, None, None);
            if photo_info != None and photo_set.get(photo_info["basic1"]["id"]) == None:
                getPhoto(photo_info);
                time.sleep(0.5);
                photo_set[photo_info["basic1"]["id"]] = 0;
        
        index = index + 1;
 
def crawlPhotosByTag(date_from, date_to, in_tags):
    index = 1;
    #bb = '129.5,30.4,147.0,45.4';
    # for the US
    bb = '-125.5, 29.6, －69.3, 49.1'

    while 1:
        photos = flickr.photos_search(bbox = bb, min_upload_data=date_from, max_upload_date=date_to, per_page = 500, page = index, tags = in_tags);
        count = 0;
        for photo in photos[0]:
            print 'title = ', photo.attrib['title']
            #photo_info = photo.attrib;
            photo_info = getPhotoInfo(photo, None, None);
            if photo_info != None:
                getPhoto(photo_info);
                time.sleep(2);
        index = index + 1;    
 
def getPhotoInfo(photo, boundbox, timespan):
    photo_info = {};
    photo_info['basic1'] = photo.attrib;

    try:
        #get the date
        info = flickr.photos_getInfo(secret=secret, photo_id = photo.attrib['id']);
        #photo_info['dates'] = info[0].attrib['dates'];
            
        photo_info['basic2'] = info.attrib;
        photo_info['owner'] = info[0][0].attrib;
        photo_info['title'] = info[0][1].attrib;
        photo_info['discription'] = info[0][2].attrib;
        photo_info['dates'] = info[0][4].attrib;
        photo_info['comments'] = [];
        for comment in info[0][8]:
            photo_info['comments'].append(comment.attrib);
        photo_info['notes'] = info[0][9].attrib;
        photo_info['people'] = info[0][10].attrib;
        photo_info['tags'] = [];
        for tag_name in info[0][11]:
            photo_info['tags'].append(tag_name.attrib['raw']);
        if len(info[0]) > 12:
            photo_info['location'] = info[0][12].attrib;
        else:
            photo_info['location'] = None;

        #if len(info[0])> 14:
        #    photo_info['pageurl'] = info[0][14].attrib;
        #else:
        #    photo_info['pageurl'] = None;
        
        #filter some photos
        if boundbox != None:
            if photo_info['location'] == None or photo_info['location'] == {}:
                return None;

            lati = photo_info['location']['latitude'];
            longi = photo_info['location']['longitude'];
            if lati != None and lati != []  and longi != None and longi != []:
                lati = float(lati);
                longi = float(longi);
                if lati > boundbox['lati_up'] or lati < boundbox['lati_down'] or longi < boundbox['long_left'] or longi > boundbox['long_right']:
                    return None;
            else:
                return None;

        if timespan != None:
            time = datetime.datetime.strptime(photo_info['dates']['taken'], '%Y-%m-%d %H:%M:%S');
            if time < timespan['from']:
                return None;
            if time > timespan['to']:
                return None;
        
        #photo_tags = flickr.tags_getListPhoto(photo_id = photo.attrib['id']); 
        #photo_info['tags'] = photo_tags[0][0].attrib;
        #print 'tags=', photo_info['tags'];
        
        #get the favourite
        favorite = flickr.photos_getFavorites(photo_id=photo.attrib['id']);
        photo_info['favorite'] = [];
        for favor in favorite[0]:
            photo_info['favorite'].append( favor.attrib['nsid']);
        
        #get the url of photos  
        sizes = flickr.photos_getSizes(photo_id = photo.attrib['id']);
        photo_info['url'] = None;
        photo_info['size'] = None;
        for size in sizes[0]:
            if size.attrib['label'] == 'Medium':
                url = size.attrib['source'];
                width = size.attrib['width'];
                height = size.attrib['height'];
                    
                photo_info['url'] = url;
                photo_info['size'] = [width, height];

        if photo_info['url'] == None:
            for size in sizes[0]:
                if size.attrib['label'] == 'Original':
                    url = size.attrib['source'];
                    width = size.attrib['width'];
                    height = size.attrib['height'];
                    
                    photo_info['url'] = url;
                    photo_info['size'] = [width, height];
        
        return photo_info;
    except:
        
        print 'exception!';
        return None;


def getPhoto(photo_info):
    global g_tags
    #get the photos and store them
    times = photo_info['dates']['posted'];
    file_name = datetime.datetime(1970, 1, 1, 0, 0, 0) + timedelta(days = int(times)/(3600*24), seconds = int(times)%(3600*24));
    dir_name = str(file_name.year) + '_' + str(file_name.month) + '_' + str(file_name.day);
            
    url = photo_info['url'];
    if url != None:
        post_fix = url[(len(url)-4) : len(url)];
        file_name = photo_info['basic1']['id'] + '_' + file_name.strftime('%d_%m_%y_%H:%M');

        #dir_name = './JapanPhoto/tags/' + g_tags[0];
        #dir_name = '/mnt/chevron/kykamath/data/twitter/twitter_pics/japan/JapanPhoto2/' + dir_name;
        dir_name = '/mnt/chevron/yuan/pic/US/' + dir_name;
        if not os.path.exists(dir_name):
            os.makedirs(dir_name);
            
        full_name = dir_name + '/' + file_name + post_fix;
        #urllib.urlretrieve(url, full_name);
        writeToFileAsJson(photo_info, dir_name + '/' + 'PhotoInfo.txt');        
        
        print full_name;
        print photo_info;

def writeToFileAsJson(data, file):
    try:
        f = open('%s'%file, 'a')
        f.write(cjson.encode(data)+'\n')
        f.close()
    except: 
        pass

def crawlByUser():
    user_set = genInitSet("./JapanPhoto/");
    from_date = datetime.datetime(2011, 2, 11, 0, 0, 0);
    to_date = datetime.datetime(2011,4,10, 0, 0, 0);
    crawlPhotosByUser(user_set, from_date, to_date);

#g_tags = ['s-tour'];
#g_tags = ['prayforjapan'];
#g_tags = ['odawara', 'hanshin', 's_tour'rakuteneagles', iazk48', 'prayforjapan', 'nuclear', 'TEPCO', 'cameraplus'];
g_tags = ['tornado', 'hurricane', 'irene'];

#crawlPhotosInPeriod('2011-03-29', '2011-03-30');
crawlPhotosByTag('2011-08-26', '2011-08-30', g_tags);
#crawlByUser();
