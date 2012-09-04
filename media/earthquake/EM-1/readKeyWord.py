'''created by @wei
'''
import re
import sys
sys.path.append('/home/yuan/lab/utility/')
from loadFile import *

#path1 = '/home/yuan/lab/media/earthquake/data/event/3_2011_events/truth_cluster.txt'
path1 = '/home/yuan/lab/media/earthquake/data/event/irene_overall/truth_cluster.txt'
#path1 = '/home/yuan/lab/media/earthquake/data/event/8_2011_events/truth_cluster_4.txt'
#path1 = "home/yuan/lab/media/earthquake/data/US_cluster_truth.txt"
#path1="/home/wei/Downloads/tweets/US_cluster_truth.txt"

def ReadKeyWord():
    return loadToken(path1);

def ReadKeyWord2(path):
    wordList=[]
    f=open(path,'r')
    while 1:
        word=f.readline()
        if word=='\n':
            word=f.readline()
        if not word: break
        word=(re.findall(r'\w+', word))[0]
        wordList.append(word)
    f.close()
    wordList.remove('retweet')
    wordList.remove('jobs')
    return wordList

#print ReadKeyWord(path1)
#print len(ReadKeyWord(path1))
