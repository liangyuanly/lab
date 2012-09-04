#-*- coding: utf-8 -*-
from twitter import TweetFiles
#import cjson, gzip
import re
import os
import sys
import json
sys.path.append('/home/yuan/lab/utility/')
from tokenization import *

#dir1 = '/home/yuan/lab/duration/data/3_2011_tweets/'
dir1 = '/home/yuan/lab/media/earthquake/data/event/irene_overall/tweet/'
#dir1 = '/home/yuan/lab/duration/data/8_2011_tweets/'
#dir1 = '/home/wei/Downloads/tweets/2012/'
#dir1='/home/wei/spacialTemporal/testdata/testdata2/'
#path1="/home/wei/Downloads/geo.2011-10-02_23-49.txt.gz"
monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
#===============================================================================
# build a full dictionary with all necessary dimensions included
#===============================================================================
#another way to read dir
#import os
#import glob

#path = 'sequences/'
#for infile in glob.glob( os.path.join(path, '*.fasta') ):
#    print "current file is: " + infile
def DocidWordFreqTimeLocationDictFromDir(directory, keywords):
    #---------------------- use each tweet as a doc. here may not be appropriate
    #---------------------------------------------------------------- initialize
    collectionWordDict = {}#word:frequency
    dict2 = {}
    timeStamps = {}# docID:"time+location"
    timeStampToDocIdDict = {}#time+location:[DocIds]
    #timeToLocationDict = {}#time:[locations]
    #locationToTimeDict = {}#location:[times]
    docId = 0
    listing = os.listdir(directory)
    for path in listing:
        print "current file is: " + path
        path = directory + path
        for tweet in TweetFiles.iterateTweetsFromGzip(path):
            if 1:
            #try:
                docId = tweet['id'];
                dict2[docId] = {};

                #get words
                dict2[docId]['words'] = {}
                dict2[docId]['docWordCount'] = 0
                
                simi_flag = 0;
                for token in keywords:
                #for puretweet in re.findall(r'\w+', tweet['text']):    
                    #-------------------------- for puretweet in tweet['text'].split('\W+'):
                    #---------------------------------------------print pure text tweets
                    #------------------------------ if (dict2[docNum][puretweet]!=None):
                    #puretweet=str(puretweet)
                    if similarityCal(token, tweet['text']) <= 0:
                        continue

                    simi_flag = 1;
                    dict2[docId]['docWordCount'] += 1 
                    if(token in dict2[docId]['words'].keys()):
                        dict2[docId]['words'][token] += 1 
                    else:
                        dict2[docId]['words'][token] = 1
                    if(token in collectionWordDict.keys()):
                        collectionWordDict[token] += 1
                    else:
                        collectionWordDict[token] = 1

                if simi_flag <= 0:
                    del dict2[docId]
                    continue;

                #docId += 1
                #dict2[docId] = {}       
                
                #get time stamp
                tempTime = []
                tempTime=re.split(r' ',tweet['time'])
                dict2[docId]['time'] = {}
                dict2[docId]['time']['year'] = int(tempTime[5])
                #dict2[docId]['time']['month']={}#seems this is useless
                year='%04d' % int(tempTime[5])
                tempMonth = tempTime[1]
                dict2[docId]['time']['month'] = monthDict[tempMonth]
                month='%02d' % monthDict[tempMonth]
                dict2[docId]['time']['day'] = int(tempTime[2])
                day='%02d' % int(tempTime[2])
                dict2[docId]['time']['hour'] = int(re.split(r':', tempTime[3])[0])
                hour='%02d' % int(re.split(r':', tempTime[3])[0])
                dict2[docId]['time']['minute'] = int(re.split(r':', tempTime[3])[1])
                if dict2[docId]['time']['minute'] < 30:
                    minuteStamp = 0  
                else:
                    minuteStamp = 1                     
                timeStamp = year+month+day
                #locationStamp = tempLoc1 + tempLoc2
                timeStamps[docId] = (timeStamp)    
                #print timeLocationStamps
                #creat the other three dictionary for later use
                if timeStamps[docId] not in timeStampToDocIdDict.keys():
                    timeStampToDocIdDict[timeStamps[docId]] = []
                timeStampToDocIdDict[timeStamps[docId]].append(docId)    
            #except: 
            #    print 'exception!'
            #    pass

#    print collectionWordDict
#    print dict2
    
#    outfile = file('dictData.txt', 'w');
#    json.dump(collectionWordDict, outfile);
#    outfile.write('\n');
#    json.dump(dict2, outfile);
#    outfile.write('\n');
#    json.dump(timeStamps, outfile);
#    outfile.write('\n');
#    json.dump(timeStampToDocIdDict, outfile);
#    outfile.write('\n');
#    outfile.close();

    return (collectionWordDict, dict2, timeStamps, timeStampToDocIdDict)
#print DocidWordFreqTimeLocationDict(path1)   

#f= open('./out1.txt','w')
#print >>f, DocidWordFreqTimeLocationDictFromDir(dir1)   
#f.close()

#DocidWordFreqTimeLocationDictFromDir(dir1)    
