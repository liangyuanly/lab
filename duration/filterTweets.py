import cjson
from operator import itemgetter
from tagCount import TagCount
from library.mrjobwrapper import ModifiedMRJob, runMRJob
from datetime import datetime
from dateutil.relativedelta import relativedelta
from settings import hdfsInputFolder, hashtagsWithoutEndingWindowFile,\
        hashtagsWithEndingWindowFile, timeUnitWithOccurrencesFile, \
        hashtagsWithoutEndingWindowFile, hashtagsAllOccurrencesWithinWindowFile,\
        hashtagsWithoutEndingWindowWithoutLatticeApproximationFile, latticeGraphFile

def getInputFiles(startTime, endTime, folderType='world'):
    current=startTime
    while current<=endTime:
        yield hdfsInputFolder%folderType+'%s_%s'%(current.year, current.month)
        current+=relativedelta(months=1) 

def iterateTweets(filename):
    for line in file(filename, 'rb'):
        data = cjson.decode(line)
        yield data

def filterTweetsByTT(infiles, sel_tags, outfile):
    out = file(outfile, 'w');
    for filename in infiles:
        for data in iterateTweets(filename):
            tweet_tag = tweet_info['h'];
            for tag in tweet_tag:
                if tag in sel_tags:
                    cjson.dump(data);
                    out.write('\n');

    out.close();

def loadTopTags(filename):
    infile = file(filename);
    lines = infile.readlines();
    all_tags = [];
    for line in lines:
        data = cjson.decode(line);
        all_tags.append((data[0], int(data[1])));

    sort_tags = sorted(all_tags, key=itemgetter(1), reverse = True);
    sort_tags = sort_tags[0:1000];
    sel_tags = [];
    for tags in sort_tags:
        sel_tags.append(tags[0]);
    print sel_tags >> output.txt
    return sel_tags;

def filterTweetMain():
    inputFilesStartTime, inputFilesEndTime = datetime(2011, 3, 1), datetime(2012, 3, 31)
    tagfile = 'data/testTag'
    tags = loadTopTags(tagfile)

    inputfiles = getInputFiles(inputFilesStartTime, inputFilesEndTime)
    outfile = 'output/2011_3_filter_tweets'
    filterTweetsByTT(inputfiles, tags, outfile)

if __name__ == '__main__':
    filterTweetMain();
