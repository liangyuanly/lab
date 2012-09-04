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
lambdaB = 0.05
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
####yuan
#prob_Zdw_equalto_J = {}
#for docId in dict2.keys():
#    prob_Zdw_equalto_J[docId] = {}
#    #print dict2[docId]['words']
#    for word in dict2[docId]['words'].keys():
#        prob_Zdw_equalto_J[docId][word] = {}
#yuan
####
prob_Zdw_equalto_J = {};
for docId in dict2.keys():
    for word in dict2[docId]['words'].keys():
        prob_Zdw_equalto_J[word] = {};

####yuan
#prob_Ydwj_equalto_one = {}
#for docId in dict2.keys():
#    prob_Ydwj_equalto_one[docId] = {}
#    for word in dict2[docId]['words'].keys():
#        prob_Ydwj_equalto_one[docId][word] = {}
####

###yuan
#prob_theta_doc = {}
#for docId in dict2.keys():
#    prob_theta_doc[docId] = {}
###


prob_theta_timeloc = {}
for tl in timeStampToDocIdDict.keys():
    prob_theta_timeloc[tl] = {}
#    print prob_theta_timeloc
#

prob_word_theta = {}
for theta in range(1, kmax):
    prob_word_theta[theta] = {}

#===============================================================================
# calculate em
#===============================================================================
log_prob_C_new = -10000000
log_prob_C_old = log_prob_C_new-1
try:
    ####yuan
    #for docId in dict2.keys():
    #    sum_prob_theta_doc=0
    #    for j in range(1, kmax):
    #        if j not in prob_theta_doc[docId].keys():
    #            prob_theta_doc[docId][j] = random.random()
    #            sum_prob_theta_doc+=prob_theta_doc[docId][j]
    #    for j in range(1, kmax):
    #        prob_theta_doc[docId][j]/=sum_prob_theta_doc
    
    for stamp in timeStampToDocIdDict.keys():
        sum_prob_theta_timeloc=0
        for j in range(1, kmax):
            if j not in prob_theta_timeloc[stamp].keys():
                prob_theta_timeloc[stamp][j] = random.random()
                sum_prob_theta_timeloc+=prob_theta_timeloc[stamp][j]
        for j in range(1,kmax):
            prob_theta_timeloc[stamp][j]/=sum_prob_theta_timeloc
    
    for j in range(1, kmax):
        sum_prob_word_theta=0
        for word in keyWords:
            if word not in prob_word_theta[j].keys():
                prob_word_theta[j][word] = random.random()
                sum_prob_word_theta+=prob_word_theta[j][word]
        for word in keyWords:
            prob_word_theta[j][word]/=sum_prob_word_theta
except:
    print 'exception!'
    pass

iter_count = 0;
while (log_prob_C_new > log_prob_C_old or iter_count < 10):
#Expectation part 
#    for docId in dict2.keys():
#        tempTl = timeStamps[docId]
#        for word in dict2[docId]['words'].keys():
#            if word in keyWords:
#                numeratorZ = {}
#                xigmaNumeratorZ = 0
#                for j in range(1, kmax):
#                    numeratorZ[j] = (1 - lambdaB) * prob_word_theta[j][word] \
#                                    * prob_theta_timeloc[tempTl][j] 
#                    #numeratorZ[j] = (1 - lambdaB) * prob_word_theta[j][word] \
#                    #* ((1 - lambdaTl) * prob_theta_doc[docId][j]+ lambdaTl \
#                    #     * prob_theta_timeloc[tempTl][j])            
#                
#                for i in range(1, kmax):
#                    xigmaNumeratorZ += numeratorZ[i]
#                denominatorZ = lambdaB * prob_w_thetaB[word] + xigmaNumeratorZ
#                for i in range(1, kmax):
#                    #prob_Zdw_equalto_J[docId][word][i] = numeratorZ[i] / denominatorZ  
#                    prob_Zdw_equalto_J[word][i] = numeratorZ[i] / denominatorZ  

    for word in keyWords:
        numeratorZ = {}
        for j in range(1, kmax):
            numeratorZ[j] = 0.0
        xigmaNumeratorZ = 0.0  

        for j in range(1, kmax):
            for tempTl in timeStampToDocIdDict.keys():
                temp = prob_word_theta[j][word] * prob_theta_timeloc[tempTl][j] 
                numeratorZ[j] += temp;
                xigmaNumeratorZ +=  temp;
        denominatorZ = xigmaNumeratorZ; 
        #denominatorZ = lambdaB * prob_w_thetaB[word] + xigmaNumeratorZ
        for j in range(1, kmax):
            prob_Zdw_equalto_J[word][j] = numeratorZ[j] / denominatorZ  
    
    print 'E Step over', prob_Zdw_equalto_J;

#Maximization part
    #(1)
####    for docId in dict2.keys():
####        xigmaThetaD = 0
####        xigmaThetaTL = 0#attention
####        #tempTl = timeStamps[docId]
####        xigmaThetaJD = {} 
####        for j in range(1, kmax): 
####            if j not in xigmaThetaJD.keys():
####                xigmaThetaJD[j] = 0
####            for word in dict2[docId]['words'].keys():
####                if word in keyWords:
####                    thetaJD = dict2[docId]['words'][word] * prob_Zdw_equalto_J[docId][word][j] \
####                    * (1 - prob_Ydwj_equalto_one[docId][word][j])
####                    xigmaThetaJD[j] += thetaJD
####            xigmaThetaD += xigmaThetaJD[j]
#####        if xigmaThetaD == 0:
#####            xigmaThetaD = 0.000001#initialization
####        for i in range(1, kmax):
####            prob_theta_doc[docId][i] = xigmaThetaJD[i] / xigmaThetaD
    
    #(2)
    for stamp in timeStampToDocIdDict.keys(): 
        xigmaThetaTL = 0
        xigmaThetaJTL = {} 
        for docId in timeStampToDocIdDict[stamp]:
            for j in range(1, kmax):
                if j not in xigmaThetaJTL.keys():
                    xigmaThetaJTL[j] = 0
                
                for word in dict2[docId]['words'].keys():
                    #if word in keyWords:
                    thetaTL = dict2[docId]['words'][word] * prob_Zdw_equalto_J[word][j] \
                    ####thetaTL = dict2[docId]['words'][word] * prob_Zdw_equalto_J[docId][word][j] \
                    ####yuan * prob_Ydwj_equalto_one[docId][word][j]
                    xigmaThetaJTL[j] += thetaTL
                    xigmaThetaTL += thetaTL
                #xigmaThetaTL += xigmaThetaJTL[j]
        for i in range(1, kmax):
            prob_theta_timeloc[stamp][i] = xigmaThetaJTL[i] / xigmaThetaTL          
        
            print 'time=', stamp, 'theta=', i, 'p(theta|t)=', prob_theta_timeloc[stamp][i];

    #(3)
    for j in range(1, kmax):
        xigmaTheta = 0
        xigmaWTheta = {}
        for word in keyWords:
            if word not in xigmaWTheta.keys():
                xigmaWTheta[word] = 0
            for docId in dict2.keys():   
                if word not in dict2[docId]['words'].keys():
                    tempWordCount = 0
                    tempProbZ = 0
                else:
                    tempWordCount = dict2[docId]['words'][word]
                    tempProbZ = prob_Zdw_equalto_J[word][j]
                    ##tempProbZ = prob_Zdw_equalto_J[docId][word][j]
                wTheta = tempWordCount * tempProbZ
                xigmaWTheta[word] += wTheta
                xigmaTheta += wTheta
            #xigmaTheta += xigmaWTheta[word]
#        if xigmaTheta == 0:
#            xigmaTheta = 0.000001#initialization    
        for word in keyWords:
            prob_word_theta[j][word] = xigmaWTheta[word] / xigmaTheta

            print 'theta=', j, 'word=', word, 'p(w|theta)=', prob_word_theta[j][word];

# the stop condition 
    log_prob_C = 0
    for docID in dict2.keys():
        tempTl = timeStamps[docId] 
        tempOuter = 0
        for word, freq in dict2[docId]['words'].iteritems():
            #if word in keyWords:
            #tempaaa = lambdaB * prob_w_thetaB[word]
            #tempaaa = dict2[docId]['words'][word] * log10(lambdaB * prob_w_thetaB[word])
            tempbbb = 0
            for j in range(1, kmax):
                ####tempbbb += prob_word_theta[j][word] * ((1 - lambdaTl) \
                ####    * prob_theta_doc[docId][j] + lambdaTl * prob_theta_timeloc[tempTl][j])
                tempbbb += prob_word_theta[j][word] *  prob_theta_timeloc[tempTl][j]
            
            #tempbbb = tempbbb * (1 - lambdaB)
            #temp1 = tempaaa + tempbbb
            temp1 = freq * log10(tempbbb)
            log_prob_C += temp1
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


#prob_t=1/len(timeStampToDocIdDict)
f = open('output/theme_3_2011.txt','w')
for testTheme in range(1,kmax):
    prob_t_theme = {}
    prob_t_theme_numerator = {}
    prob_t_theme_denominator = 0
    for time in timeStampToDocIdDict.keys():
        prob_t_theme_numerator[time]=prob_theta_timeloc[time][testTheme]
        prob_t_theme_denominator+=prob_t_theme_numerator[time]
    for time in timeStampToDocIdDict.keys():
        prob_t_theme[time]=prob_t_theme_numerator[time]/prob_t_theme_denominator
    #print >>f, prob_t_theme, '\n' 
    json.dump(prob_t_theme, f);
    f.write('\n');

for theme in range(1,kmax):
    sorted_x = sorted(prob_word_theta[theme].iteritems(), key=operator.itemgetter(1), reverse=True)
    #print>>f, sorted_x, '\n'
    json.dump(sorted_x, f);
    f.write('\n');
f.close()

