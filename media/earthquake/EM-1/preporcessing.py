from twitter import TweetFiles
from readKeyWord import ReadKeyWord,path1
#import cjson, gzip
import re
import os
import json
keyWordPath=path1

#dir1 = '/home/yuan/lab/duration/data/8_2011_tweets/'
#dir1 = '/home/wei/Downloads/tweets/2011/'
#file1='/home/wei/Downloads/tweets/2011_8_24.txt.gz'

#path1="/home/wei/Downloads/geo.2011-10-02_23-49.txt.gz"
#monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
keyWords=ReadKeyWord(keyWordPath)
print keyWords
#first check each tweet to see if it contain words in the high freq list. if not, wont consider that tweet. 
class preprocessingTemp:
    def __init__(self):
        self.filecount=0
        self.curfilename=''
    @staticmethod
    def PreprocessingFile(files):
        newfilename=(files.split('.txt.gz'))[0]+'.txt'
        newfile=open(newfilename,'w')
        for tweet in TweetFiles.iterateTweetsFromGzip(files):
            try:
                if tweet['corrdinate']!= None:
                    tempLoc1='%d'% tweet['corrdinate'][0]
                    tempLoc2='%d'% tweet['corrdinate'][1]
                    #print 'aaaaaa'
                #print tempLoc1,tempLoc2
                if int(tempLoc1)>=30 and int(tempLoc1)<50 and int(tempLoc2)<=-75 and int(tempLoc2)>-125:
                    if isinstance(tweet['text'], unicode):   
                        tweetlist=tweet['text'].split()
                        for checkword in keyWords:
                            if checkword in tweetlist:
                                s=json.dump(tweet, newfile)
                                newfile.write(s+"\n")
                                break
                                
                    else:
                        tweetlist=re.findall(r'\w+', tweet['text'])
                        #print tweetlist
                        for checkword in keyWords:
                            if checkword in tweetlist:
                                print tweetlist
                                s=json.dumps(tweet,newfile)
                                newfile.write(s+"\n")
                                break
            except:pass
        newfile.close()
          
    @staticmethod                          
    def PreprocessingDirectory(directory):
        listing = os.listdir(directory)
        for path in listing:
            print "current file is: " + path
            path = directory + path
            print path
            preprocessingTemp.PreprocessingFile(path)

#a=preprocessingTemp()
#a.PreprocessingFile(file1) 
#a.PreprocessingDirectory(dir1)

        
