'''created by @wei
'''
#This is the implementation of  EM on temporal theme pattern mining
#we ll consider each twitter as a document in the test
#only consider that 35 words
#use random for EM initialization
from __future__ import division
from readDir_temporalonly import DocidWordFreqTimeLocationDictFromDir,dir1
from math import log10
import random
from readKeyWord import ReadKeyWord
import operator
import cjson, json

#parameter setting
#lambdaB=raw_input('Enter lamda_b which controls the strength of the background model, usually 0.9-0.95')
#lambdaTl=raw_input('Enter lamda_tl which controls the modeling of spatiotemporal theme distributions,usually 0.5-0.7')
#lambdaB = 0.95
#lambdaTl = 0.7
lambdaB = 0.2
#get the result from dictionaryFile()
#wordDict = {}
#dict2 = {}
#timeStamps = {}
kmax = 4

#keyWordPath=path1
keyWords= ReadKeyWord()
dictionaryFile=()

#load the distionary
dictionaryFile=DocidWordFreqTimeLocationDictFromDir(dir1, keyWords)

#load the dictionary from the file
#infile = file('dictData.txt');
#wordDict = json.loads(infile.readline()) 
wordDict = dictionaryFile[0]

#dict2 = json.loads(infile.readline())
dict2 = dictionaryFile[1];

#calculate the unique words in all documents.
docNum = len(dict2)

#timeStamps = json.loads(infile.readline())
timeStamps = dictionaryFile[2];

#timeStampToDocIdDict = json.loads(infile.readline())
timeStampToDocIdDict = dictionaryFile[3];
timeStampsNum = len(timeStampToDocIdDict) 
distinctWordNum = len(wordDict)
totalWordNum = 0
for word in wordDict.keys():   
    totalWordNum += wordDict[word]
    
print "Average tweets length is:",totalWordNum/docNum    
#P(w|thetaB)
prob_w_thetaB = {}
factor = 0.1;
for word in wordDict.keys():
    prob_w_thetaB[word] = factor * round(wordDict[word] / totalWordNum, 5)
#for value in prob_w_thetaB.values():
#    print round(value, 5)
#initialization of themes each of k themes should be a collection of words distributions 
#such that Sigma(all words in vocabulary) p(w|theta)=1
#set the max number of themes?
#initialize the global themes as list of words
#===============================================================================
# EM initialization
#===============================================================================
#
####
#prob_Zdw_equalto_J = {};
#for docId in dict2.keys():
#    for word in dict2[docId]['words'].keys():
#        prob_Zdw_equalto_J[word] = {};

prob_Zwt_equalto_J = {};
for word in keyWords:   
    prob_Zwt_equalto_J[word] = {};
    for time in timeStampToDocIdDict.keys():
        prob_Zwt_equalto_J[word][time] = {};
        for j in range(1, kmax):
            prob_Zwt_equalto_J[word][time][j] = 0;

prob_theta_timeloc = {}
for tl in timeStampToDocIdDict.keys():
    prob_theta_timeloc[tl] = {}
    for j in range(1, kmax):
        prob_theta_timeloc[tl][j] = 0

prob_word_theta_time = {}
for theta in range(1, kmax):
    prob_word_theta_time[theta] = {}
    for time in timeStampToDocIdDict.keys():
        prob_word_theta_time[theta][time] = {}
        for word in keyWords:   
            prob_word_theta_time[theta][time][word] = 0

#===============================================================================
# calculate em
#===============================================================================
log_prob_C_new = -10000000
log_prob_C_old = log_prob_C_new-1
try:
    for stamp in timeStampToDocIdDict.keys():
        sum_prob_theta_timeloc = 0
        for j in range(1, kmax):
            #if j not in prob_theta_timeloc[stamp].keys():
            prob_theta_timeloc[stamp][j] = random.random()
            sum_prob_theta_timeloc += prob_theta_timeloc[stamp][j]
        for j in range(1,kmax):
            prob_theta_timeloc[stamp][j]/=sum_prob_theta_timeloc
    
    for j in range(1, kmax):
        for stamp in timeStampToDocIdDict.keys():
            sum_prob_word_theta=0 
            for word in keyWords:
                #if word not in prob_word_theta_time[j].keys():
                prob_word_theta_time[j][stamp][word] = random.random()
                sum_prob_word_theta += prob_word_theta_time[j][stamp][word]
            for word in keyWords:
                prob_word_theta_time[j][stamp][word]/=sum_prob_word_theta
    print 'init'
    print prob_theta_timeloc, '\n', prob_word_theta_time
except:
    print 'exception!'
    pass

iter_count = 0;
while (log_prob_C_new > log_prob_C_old or iter_count < 10):
#Expectation part 
    #for docId in dict2.keys():
    #    tempTl = timeStamps[docId]
    #    for word in dict2[docId]['words'].keys():
         #if word in keyWords:
            #numeratorZ = {}
            #xigmaNumeratorZ = 0
    #        for j in range(1, kmax):
    #            numeratorZ[j] = (1 - lambdaB) * prob_word_theta_time[j][tempTl][word] \
    #                            * prob_theta_timeloc[tempTl][j] 
                #numeratorZ[j] = (1 - lambdaB) * prob_word_theta[j][word] \
                #* ((1 - lambdaTl) * prob_theta_doc[docId][j]+ lambdaTl \
                #     * prob_theta_timeloc[tempTl][j])            
                #xigmaNumeratorZ += numeratorZ[j]
    #            prob_Zwt_equalto_J[word][tempTl][j] += numeratorZ[j] 
    
    #normalize
    #for word in prob_Zdt_equalto_J.keys():
    #    for stamp in prob_Zdt_equalto_J[word].keys():
    #        sum_fre = 0.0;
    #        for theta_j, freq in prob_Zdt_equalto_J[word][stamp].keys():
    #            sum_fre += freq;

    #        denominatorZ = lambdaB * prob_w_thetaB[word] + sum_fre;
    #        for theta_j, freq in prob_Zdt_equalto_J[word][stamp].keys():
    #            prob_Zdt_equalto_J[word][stamp][theta_j] /= denominatorZ
    
    print 'E Step'
    for word in keyWords:
        for stamp in timeStampToDocIdDict.keys():
            numeratorZ = {}
            xigmaNumeratorZ = 0.0
            denominatorZ = 0.0
            for j in range(1, kmax):
                numeratorZ[j] = (1 - lambdaB) * prob_word_theta_time[j][stamp][word] \
                                * prob_theta_timeloc[stamp][j] 
                xigmaNumeratorZ += numeratorZ[j]
            denominatorZ = lambdaB * prob_w_thetaB[word] + xigmaNumeratorZ;
            
            for j in range(1, kmax):
                prob_Zwt_equalto_J[word][stamp][j] = numeratorZ[j] / denominatorZ
                print 'word=', word, 'time=', stamp, 'theta=', j, 'p(w|t,theta)=', prob_Zwt_equalto_J[word][stamp][j]; 

    print 'M Step'
    #(2)
    for stamp in timeStampToDocIdDict.keys(): 
        xigmaThetaTL = 0
        xigmaThetaJTL = {} 
        print 'stamp=', stamp;
        for docId in timeStampToDocIdDict[stamp]:
            for j in range(1, kmax):
                if j not in xigmaThetaJTL.keys():
                    xigmaThetaJTL[j] = 0
                
                for word in dict2[docId]['words'].keys():
                    thetaTL = dict2[docId]['words'][word] * prob_Zwt_equalto_J[word][stamp][j] 
                    xigmaThetaJTL[j] += thetaTL
                    xigmaThetaTL += thetaTL
        for j in range(1, kmax):
            prob_theta_timeloc[stamp][j] = xigmaThetaJTL[j] / xigmaThetaTL          
            print 'theta=', j, 'time=', stamp, 'p(theta|t)=', prob_theta_timeloc[stamp][j]

    #(3)
    for j in range(1, kmax):
        xigmaTheta = 0
        xigmaWTheta = {}
        for docId in dict2.keys():  
            timeTl = timeStamps[docId];
            for word, freq in dict2[docId]['words'].iteritems():
                tempWordCount = dict2[docId]['words'][word]
                tempProbZ = prob_Zwt_equalto_J[word][timeTl][j]
                wTheta = tempWordCount * tempProbZ
                prob_word_theta_time[j][timeTl][word] += wTheta 

    for stamp in timeStampToDocIdDict.keys():
        for j in range(1, kmax):
            sum_fre = 0.0;
            for word in keyWords:
                sum_fre += prob_word_theta_time[j][stamp][word];
            
            for word in keyWords:
                prob_word_theta_time[j][stamp][word] /= sum_fre
            
            print 'word=', word, 'time=', stamp, 'theta=', j, 'p(w|t, theta)', prob_word_theta_time[j][stamp][word] 

# the stop condition 
    log_prob_C = 0
    for docID in dict2.keys():
        tempTl = timeStamps[docId] 
        tempOuter = 0
        for word, freq in dict2[docId]['words'].iteritems():
            #if word in keyWords:
            tempaaa = lambdaB * prob_w_thetaB[word]
            #tempaaa = freq * log10(lambdaB * prob_w_thetaB[word])
            tempbbb = 0
            for j in range(1, kmax):
                tempbbb += prob_word_theta_time[j][tempTl][word] *  prob_theta_timeloc[tempTl][j]\
            
            tempbbb = tempbbb * (1 - lambdaB)
            temp1 = tempaaa + tempbbb
            log_prob_C += freq * log10(temp1)
            #tempOuter += temp1
        #log_prob_C += tempOuter
    log_prob_C_old = log_prob_C_new
    log_prob_C_new = log_prob_C
    print 'log_prob_C_old:log_prob_C_new',log_prob_C_old, log_prob_C_new
    
    iter_count += 1;

    if (log_prob_C_new - log_prob_C_old) / abs(log_prob_C_old) < 0.001 and iter_count >= 10:
        break;


    #print 'prob_theta_timeloc'prob_theta_timeloc
#===============================================================================
# Calculate theme life cycle for a given location "l"
#===============================================================================
#testLocationStamp = "-43.45-22.92"
#testTheme = 1
#prob_t_theme_loc = {}
#prob_t_theme_loc_numerator = {}
#prob_t_theme_loc_denominator = 0
#for time in locationToTimeDict[testLocationStamp]:
#    tempTimeLocationStamp = time + ',' + testLocationStamp
#    pTL = 0
#    for docId in timeLocationStampToDocIdDict[tempTimeLocationStamp]:
#        pTL += (dict2[docId]['docWordCount'] / totalWordNum)
##    print 'prob_theta_timeloc', prob_theta_timeloc[tempTimeLocationStamp]
##    print pTL
#    prob_t_theme_loc_numerator[time] = prob_theta_timeloc[tempTimeLocationStamp][testTheme] * pTL
#    prob_t_theme_loc_denominator += prob_t_theme_loc_numerator[time]
#
#for time in locationToTimeDict[testLocationStamp]:
#    prob_t_theme_loc[time] = prob_t_theme_loc_numerator[time] / prob_t_theme_loc_denominator
#    
#f= open('/home/wei/Downloads/out.txt','w')
#print >>f, prob_t_theme_loc  
#f.close()


#==================calculate the p(t|w,theta)======================#
#==================p(w|theta)
prob_time_word_theta = {}
prob_word_theta = {}
for word in keyWords:
    prob_time_word_theta[word] = {};
    for j in range(1, kmax):
        prob_time_word_theta[word][j] = {};
        for stamp in timeStampToDocIdDict.keys():
            prob_time_word_theta[word][j][stamp] = 0.0;

for j in range(1, kmax):
    prob_word_theta[j] = {};
    for word in keyWords:
        prob_word_theta[j][word] = 0;

for j in range(1, kmax):
    word_temp_sum = 0.0;
    temp_sum = {};
    for word in keyWords:
        temp_sum[word] = 0.0;
        temp = {};
        for stamp in timeStampToDocIdDict.keys():
            temp[stamp] = prob_theta_timeloc[stamp][j] * prob_word_theta_time[j][stamp][word]
            temp_sum[word] += temp[stamp];
            word_temp_sum += temp[stamp];
        
        for stamp in timeStampToDocIdDict.keys():
            prob_time_word_theta[word][j][stamp] = temp[stamp] / temp_sum[word]; 
    
    for word in keyWords:
        prob_word_theta[j][word] =  temp_sum[word]/word_temp_sum;

f = open('output/theme_prob.txt','w')
for testTheme in range(1,kmax):
    prob_t_theme = {}
    prob_t_theme_numerator = {}
    prob_t_theme_denominator = 0
    for time in timeStampToDocIdDict.keys():
        prob_t_theme_numerator[time] = prob_theta_timeloc[time][testTheme]
        prob_t_theme_denominator += prob_t_theme_numerator[time]
    for time in timeStampToDocIdDict.keys():
        prob_t_theme[time] = prob_t_theme_numerator[time]/prob_t_theme_denominator
    #print >>f, prob_t_theme, '\n' 
    json.dump(prob_t_theme, f);
    f.write('\n');

for theme in range(1,kmax):
    #for stamp in prob_word_theta_time[theme].keys():
    sorted_x = sorted(prob_word_theta[theme].iteritems(), key=operator.itemgetter(1), reverse=True)
    print theme, sorted_x;
    json.dump(sorted_x, f);
    f.write('\n')    

json.dump(prob_time_word_theta, f);
f.write('\n')
f.close()
