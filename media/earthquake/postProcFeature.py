import json,cjson
import sys
sys.path.append('../../utility/')
from filterNoise import *

def normalize(time_unit):
    for term, bins in time_unit.iteritems():
        sum = 0;
        for time, freq in bins.iteritems():
            sum = sum + freq;
        
        for time, freq in bins.iteritems():
            bins[time] = freq / float(sum);

def noiseFilter(infilename, outfilename):
    infile = file(infilename);
    term_bins = json.load(infile);
    
    normalize(term_bins);
    new_term_bins = {};
    for term, bins in term_bins.iteritems():
        new_bins = filterNoiseByKalman(bins);
        #new_bins = filterNoiseByFreq(bins);
        new_term_bins[term] = new_bins;
    normalize(new_term_bins);

    outfile = file(outfilename, 'w');
    json.dump(new_term_bins, outfile);

def tranFormat(term_times, outfilename):
    outfile = file(outfilename, 'a')
    for term, bins in term_times.iteritems():
        outfile.write(term+'\n');
        for time, freq in bins.iteritems():
            outfile.write(time+':'+str(freq) + '\t');
        outfile.write('\n');
    outfile.write('----\n')
    outfile.close();

def noiseFilterMain():
    infilename = './data/event/8_2011_events/term_time.txt';
    outfilename = './data/event/8_2011_events/term_time_filter.txt';

    noiseFilter(infilename, outfilename);

def transForMain():
    infilename = './data/event/3_2011_events/term_time.txt';
    infilename2 = './data/event/3_2011_events/term_time_filter.txt';
    
    outfilename = './data/event/3_2011_events/term_time_trans.txt';
    outfile = file(outfilename, 'w')
    outfile.close();

    infile = file(infilename);
    term_unit = json.load(infile);
    infile.close();
    normalize(term_unit);
    tranFormat(term_unit, outfilename);
    
    infile = file(infilename2);
    term_unit = json.load(infile);
    infile.close();
    tranFormat(term_unit, outfilename);

noiseFilterMain() 
transForMain();
