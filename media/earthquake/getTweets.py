import os, datetime, gzip, cjson
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import numpy as np
import operator
import string
import math

class GetTweets:
    def iterateTweetsFromGzip(self, file):
        for line in gzip.open(file, 'rb'): 
            try:
                one_line = [];
                #sometimes multiple lines are put together
                if len(line) > 10000:
                    index = 0;
                    index2 = 0;
                    match_string = line[0:6];
                    while index >= 0 and index2 >= 0:
                        match_string = line[index2:index2+6];
                        index = string.find(line, match_string, index2);
                        if index < 0:
                            break;
                        index2 = string.find(line, match_string, index+1);
                        if index2 < 0:
                            index2 = string.rfind(line, '}');
                            if index2 < 0 or index2 <= index:
                                break;
                        
                        one_line = line[index:index2];
                        if len(one_line) < 100:
                            continue;

                        data = cjson.decode(one_line);
                        if 'text' in data:
                            yield data;
                else:
                    data = cjson.decode(line)
                    if 'text' in data: 
                        yield data
            except: 
                print one_line;
                print 'json decode exception!!';
                pass
    
    def calRelevance(self, tweet):
        prob = 0;
        #hash_tags = tweet['hashtag'];
        #if hash_tags != None:
        #    for hash_tag in hash_tags:
        #        if string.find(hash_tag.lower(), 'earthquake') != -1:
        #            prob = prob + 1;
        
        text = tweet['text'];
        if text != None:
            if string.find(text.lower(), 'earthquake') != -1 or string.find(text,'\\u9707') != -1:  #'\\u5730\\u9707'
                #print text.encode("utf-8");
                prob = prob + 1;

        urls = tweet['url'];
        if prob >= 1 and urls != None:
            for url in urls:
                if string.find(url.lower(), 'earthquake') != -1 or string.find(text, '\\u9707') != -1:
                    prob = prob + 1;
                else:
                    prob = prob + 0.5;
        return prob;

    def parseTweet(self, tweet):
        tweet_info = {};
        #extract the text message
        try:
            entities = tweet['entities'];
            hash_tags = entities['hashtags'];
            if hash_tags != None:
                list_tmp = [];
                for hash_tag in hash_tags:
                    list_tmp.append(hash_tag['text']);
                tweet_info['hashtag'] = list_tmp;
            else:
                tweet_info['hashtag'] = None;
        
            urls = entities['urls'];
            if urls != None:
                list_tmp = [];
                for url in urls:
                    list_tmp.append(url['url']);
                tweet_info['url'] = list_tmp;
            else:
                tweet_info['url'] = None;
            #tweet_info['url'] = entities['urls']['url'];
        
            tweet_info['text'] = tweet['text'];
            tweet_info['time'] = tweet['created_at'];
        
            cor = tweet['geo'];
            if cor != None and cor != []:
                tweet_info['corrdinate'] = cor['coordinates'];
            else:
                tweet_info['corrdinate'] = None;
                #find the user's position
            prob = self.calRelevance(tweet_info);
            tweet_info['relevance'] = prob;
            tweet_info['id'] = tweet['id'];
            tweet_info['user'] = tweet['user']['id'];
            #if prob > 1:
                #print tweet_info;
        except:
            print 'exception';
            pass
        return [prob,tweet_info];

    def getTweetsFromGzip(self, file_in, freq_matrix, image_freq_matrix, country):
        tweet_list = [];
        count1 = 0; # the number of tweets in a certain regin
        count2 = 0; # the number of images in a certain regin
        count3 = 0;
        count4 = 0; # the number of global tweets
        count5 = 0; # the number of global image

        # Japan
        if country == 'Japan':
            lati_down = 30.4;
            lati_up = 45.4;
            longi_left = 129.5;
            longi_right = 147.0; 
        
        if country == "NewZealand":
        # New zealand
            lati_down = -47.4;
            lati_up = -34.3;
            longi_left = 166.2;
            longi_right = 178.9; 

        if country == "NewzerlandCenter":
        # New zealand earthquake center
            lati_down = -43.9;
            lati_up = -43.0;
            longi_left = 171.7;
            longi_right = 173.2; 

        if country == "global":
            lati_down = -90.0;
            lati_up = 90.0;
            longi_left = -180.0;
            longi_right = 180; 

        
        step = len(freq_matrix[0]);
        lati_step = (lati_up - lati_down)/step;
        longi_step = (longi_right - longi_left)/step;


        #img_points_file = file('img_points_cor.txt', 'a');
        #tweet_points_file = file('tweet_points_cor.txt', 'a');

        for tweet in self.iterateTweetsFromGzip(file_in):
            [rel, tweet_info] = self.parseTweet(tweet);
            
            #information for global
            if rel == 1:
                count4 = count4 + 1;
            if rel > 1:
                count5 = count5 + 1;
                   
            #information for a certain regin
            #get the tweets from japan area
            corrdi = tweet_info['corrdinate'];
            if corrdi != None and corrdi != []:
                lati = float(corrdi[0]);
                longi = float(corrdi[1]);
                
                # for gloabl, need removed TODO
                #if rel >= 1:
                #    lati_index = math.floor((lati - lati_down)/lati_step);
                #    longi_index = math.floor((longi - longi_left)/longi_step);

                #    freq_matrix[lati_index][longi_index] = freq_matrix[lati_index][longi_index] + 1;
                #if rel > 1:
                #    image_freq_matrix[lati_index][longi_index] = image_freq_matrix[lati_index][longi_index] + 1;
             
                if lati <= lati_up and lati >= lati_down and longi >= longi_left and longi <= longi_right:
                    #text = tweet_info['text'];
                    #record the frequency of tweets talking about the earthquake
                    #and the frequency of the images in the earthquake
                    if rel >= 1:
                        #print lati, longi;
                        #print tweet_info;
                        lati_index = math.floor((lati - lati_down)/lati_step);
                        longi_index = math.floor((longi - longi_left)/longi_step);

                        freq_matrix[lati_index][longi_index] = freq_matrix[lati_index][longi_index] + 1;
                        if rel > 1:
                            image_freq_matrix[lati_index][longi_index] = image_freq_matrix[lati_index][longi_index] + 1;
                    
                        #print tweet_info;
                        count1 = count1 + 1;
                        count3 = count3 + 1;
                        if rel > 1:
                            count2 = count2 + 1;
                            count3 = count3 + 1; #add extra one
                        #append to the tweet list
                        #tweet_list.append(tweet_info);
                        #if count1 >= 30:
                        #    print 'text', tweet_info;
                        #    break;
                        #if count3 >= 30:
                        #    print 'image', tweet_info;
        freq = [];
        freq.append(count1);  # the frequency of the earthquake tweets
        freq.append(count2);  # the frequency of the earthquake image
        freq.append(count4);
        freq.append(count5);

        return [freq, tweet_list];

def dawTimeLine(tweets):
    #extract the time
    time_list = [];
    for tweet in tweets:
        time = tweet['time'];
        time = date2num(dateutil.parser.parse(time));
        time_list.append(time);
        outfile.write(str(time) + '\t');
    #outfile.write('\n');    
    outfile.close();

def getTime(filename):
    index = string.find(filename,'-');
    time_str = filename[0:index];
    f = "%d_%m_%Y_%H:%M";
    time = datetime.datetime.strptime(time_str, f);
    return time;

class TweetStatInfo:
    def __init__(self, time, frequency):
        self.time = time;
        self.frequency = frequency;
    def __repr__(self):
        return repr((self.time, self.frequency));

def listEarthquakeTweet():
    getter = GetTweets();
    main_path='/mnt/chevron/bde/Data/TweetData/GeoTweets/2011/3/';

    outfile_fre_tem = file('tweet_freq_tempo.txt', 'a');
    outfile_img_tem = file('image_freq_tempo.txt', 'a');
    outfile_fre_spa = file('tweet_freq_spatio.txt', 'a');
    outfile_img_spa = file('image_freq_spatio.txt', 'a');

    tweet_fre_tempo = [];
    image_fre_tempo = [];
    tweet_fre_global_tmp = [];
    image_fre_global_tmp = [];
    step = 500;
    tweet_fre_spa = np.zeros([step, step]);
    image_fre_spa = np.zeros([step, step]);

    #for days in range(11, 15): # Japan earthquake
    for days in range(20,30): # NewZerland
        path = main_path+str(days)+'/';
        dirList=os.listdir(path);
        count = 0;
        
        #outfile_fre_tem.write(path + '\n');
        #outfile_img_tem.write(path + '\n');
        outfile_fre_spa.write(path + '\n');
        outfile_img_spa.write(path + '\n');
        
        for fname in dirList:
            print fname
            count = count + 1;
            [freq_tempo, tweet_list] = getter.getTweetsFromGzip(path+fname, tweet_fre_spa, image_fre_spa, 'Japan');
            tweet_fre_tempo.append(TweetStatInfo(getTime(fname), freq_tempo[0]));
            image_fre_tempo.append(TweetStatInfo(getTime(fname), freq_tempo[1]));
            tweet_fre_global_tmp.append(TweetStatInfo(getTime(fname), freq_tempo[2]));
            image_fre_global_tmp.append(TweetStatInfo(getTime(fname), freq_tempo[3]));
            #if count >=3:
            #    break;

        tweet_fre_tempo.sort(key = operator.attrgetter('time'));
        image_fre_tempo.sort(key = operator.attrgetter('time'));
        tweet_fre_global_tmp.sort(key = operator.attrgetter('time'));
        image_fre_global_tmp.sort(key = operator.attrgetter('time'));
        
        for i in range(0, len(tweet_fre_tempo)):
            outfile_fre_tem.write(str(tweet_fre_tempo[i].time)+'\t');
            outfile_fre_tem.write(str(tweet_fre_tempo[i].frequency) + '\t' + \
                str(image_fre_tempo[i].frequency) + '\t' + \
                str(tweet_fre_global_tmp[i].frequency) + '\t' + \
                str(image_fre_global_tmp[i].frequency) + '\n');

            #outfile_img_tem.write(str(image_fre_tempo[i].time)+'\t');
            #outfile_img_tem.write(str(image_fre_tempo[i].frequency));
            outfile_img_tem.write('\n');

    for i in range(0, step):
        for j in range(0, step):
            outfile_fre_spa.write(str(tweet_fre_spa[i][j]) + '\t');
            outfile_img_spa.write(str(image_fre_spa[i][j]) + '\t');
        outfile_fre_spa.write('\n');
        outfile_img_spa.write('\n');

    #outfile_fre_tem.write('\n');
    #outfile_img_tem.write('\n');
    outfile_fre_spa.write('\n');
    outfile_img_spa.write('\n');

    outfile_fre_tem.close();
    outfile_img_tem.close();
    outfile_fre_spa.close();
    outfile_img_spa.close();

def listTweets():
    getter = GetTweets();
    path='/mnt/chevron/bde/Data/TweetData/GeoTweets/2011/3/11/11_3_2011_0:00-Tweets.txt.gz';
    #outfile = file('TweetsIn15Minutes.txt', 'wb')
    for tweet in getter.iterateTweetsFromGzip(path):
        [rel, tweet_info] = getter.parseTweet(tweet);
        if tweet_info['url'] != None and tweet_info['url'] != []:
            print tweet_info;

#main function
#listEarthquakeTweet();
#listTweets();

