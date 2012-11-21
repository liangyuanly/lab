import os, datetime, gzip, cjson
#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
#from matplotlib.dates import epoch2num, date2num
import dateutil.parser
#import numpy as np
import operator
import string
import math
import re

#    #while index1 < len(line):
#    if line[index1] == '{':
#        pa_count += 1;
#    if line[index1] == '}':
#        pa_count -= 1;
#
#    if pa_count == 0:
#        temp_line = line[index2:index1];
#        parsed_lines.append(temp_line);
#        index2 = index1 + 1;


class GetTweets:
    def parseLine(self, line):
        index1 = 0;
        index2 = 0;
        if line[0] != '{':
            return Null;

        pa_count = 0;
        parsed_lines = [];
        for match in re.finditer('}{', line):
            index2 = match.start();
            temp_line = line[index1:index2+1];
            parsed_lines.append(temp_line);        
            index1 = index2 + 1;
        
        return parsed_lines;

    def iterateTweetsFromGzip(self, file):
        for line in gzip.open(file, 'rb'): 
            try:
                #sometimes multiple lines are put together
                if len(line) > 10000:
                    lines = self.parseLine(line);
                    for parsed_line in lines:
                        data = cjson.decode(parsed_line);
                        if 'text' in data:
                            yield data;
                else:
                    data = cjson.decode(line)
                    if 'text' in data: 
                        yield data
            except: 
                print 'json decode exception!!';
                pass
 
    def iterateTweetsFromGzip2(self, file):
        for line in gzip.open(file, 'rb'): 
            try:
                one_line = [];
                #sometimes multiple lines are put together
                if len(line) > 10000:
                    index = 0;
                    index2 = 0;
                    match_string = '"text"';
                    #match_string = line[0:6];
                    while index >= 0 and index2 >= 0:
                        index = string.find(line, match_string, index2+1);
                        if index < 0:
                            break;
                        p = index;
                        while p > index2:
                            if line[p] == '{':
                                break;
                            p = p -1;
                        if p <= index2:
                            break;

                        index2 = string.find(line, match_string, index+1);
                        q = index2;
                        if q < 0:
                            #the last one
                            q = string.rfind(line, '}');
                            if q < 0 or index2 <= index:
                                break;

                        while q > index1:
                            if line[q] == '}':
                                break;
                            q = q -1;
                        
                        if q <= index1:
                            break;

                        one_line = line[p:q];
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
                tweet_info['geo'] = cor['coordinates'];
            else:
                tweet_info['geo'] = None;
                #find the user's position
            tweet_info['id'] = tweet['id'];
            tweet_info['user'] = tweet['user']['id'];

            #tweet_info['reply_to'] = tweet['in_reply_to_status_id']
            #get the retweet's original tweet
            
            #if 'retweeted_status' in tweet.keys():
            #    print 'retweet catch!'
            #    retweeted = tweet['retweeted_status'];
            #    print retweeted
            #    tweet_info['retweeted'] = {}
            #    tweet_info['retweeted']['id'] = retweeted['id'];
            #    tweet_info['retweeted']['count'] =  retweeted['retweet_count'];
            #    tweet_info['retweeted']['create_time'] =  retweeted['user']['created_at']
            #    tweet_info['retweeted']['geo'] = retweeted['coordinates']
            #    tweet_info['retweeted']['user'] = retweeted['user']['id']
            #    tweet_info['retweeted']['text'] = retweeted['text']
            #    tweet_info['retweeted']['url'] = retweeted['entities']['urls']
        except:
            print 'exception';
            pass
        return tweet_info;

