import os, json, cjson
from Utility import *
import sys
from Utility import *

def filter(fold):
    files = os.listdir(fold)
    dics = {};
    for afile in files:
        path = fold + afile;
        print path;
        tweets = loadSimpleTweetsFromFile(path);
        filter_tweets = [];
        for tweet in tweets:
            id = tweet['id'];
            if id in dics.keys():
                continue;
            dics[id] = 1;
            filter_tweets.append(tweet);

        fold2 = fold + 'filter/'
        outfilename = fold2 + afile;
        outfile = file(outfilename, 'w');
        for tweet in filter_tweets:
            json.dump(tweet, outfile);
            outfile.write('\n');
        outfile.close();

def transformat(filename):
    infile = file(filename);
    outfile = file(filename + 'trans.txt', 'w');
    lines = infile.readlines();
    for line in lines:
        item = line.split('\t');
        if len(item) >= 2:
            outfile.write(item[0] + '\n');
        else:
            outfile.write(line);
    infile.close();
    outfile.close();
        
#filter('./data/event/jpeq_jp/tweet/');
transformat('data/event/NBA/truth_cluster.txt');
