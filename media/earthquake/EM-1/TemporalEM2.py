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
#keyWordPath=path1
keyWords= ReadKeyWord()
dictionaryFile=()

#load the distionary
dictionaryFile=DocidWordFreqTimeLocationDictFromDir(dir1, keyWords)
#parameter setting
#lambdaB=raw_input('Enter lamda_b which controls the strength of the background model, usually 0.9-0.95')
#lambdaTl=raw_input('Enter lamda_tl which controls the modeling of spatiotemporal theme distributions,usually 0.5-0.7')
#lambdaB = 0.95
#lambdaTl = 0.7
lambdaB = 0.7
lambdaTl = 1
#get the result from dictionaryFile()
wordDict = {}
dict2 = {}
timeStamps = {}
wordDict = dictionaryFile[0] 
dict2 = dictionaryFile[1] 
#calculate the unique words in all documents.
docNum = len(dict2)
#uniqueWordsNum=0
#for docId in dict2.keys():
#    uniqueWordsNum+=len(dict2[docId]['words'])
timeStamps = dictionaryFile[2]
#print timeLocationStamps
#print wordDict.keys()
#count total number of words in the collection
timeStampToDocIdDict = dictionaryFile[3]
timeStampsNum = len(timeStampToDocIdDict) 

distinctWordNum = len(wordDict)
totalWordNum = 0
for word in wordDict.keys():   
    totalWordNum += wordDict[word]
    
print "Average tweets length is:",totalWordNum/docNum    
#P(w|thetaB)
prob_w_thetaB = {}
for word in wordDict.keys():
    prob_w_thetaB[word] = round(wordDict[word] / totalWordNum, 5)
#for value in prob_w_thetaB.values():
#    print round(value, 5)
#initialization of themes each of k themes should be a collection of words distributions 
#such that Sigma(all words in vocabulary) p(w|theta)=1
#set the max number of themes?
kmax = 4
#initialize the global themes as list of words
#===============================================================================
# EM initialization
#===============================================================================
#
prob_Zdw_equalto_J = {}
for docId in dict2.keys():
    prob_Zdw_equalto_J[docId] = {}
    #print dict2[docId]['words']
    for word in dict2[docId]['words'].keys():
        prob_Zdw_equalto_J[docId][word] = {}
#print prob_Zdw_equalto_J
#
prob_Ydwj_equalto_one = {}
for docId in dict2.keys():
    prob_Ydwj_equalto_one[docId] = {}
    for word in dict2[docId]['words'].keys():
        prob_Ydwj_equalto_one[docId][word] = {}
#
prob_theta_doc = {}
for docId in dict2.keys():
    prob_theta_doc[docId] = {}
#
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
log_prob_C_new =-10000000
log_prob_C_old=log_prob_C_new-1
try:
    for docId in dict2.keys():
        sum_prob_theta_doc=0
        for j in range(1, kmax):
            if j not in prob_theta_doc[docId].keys():
                prob_theta_doc[docId][j] = random.random()
                sum_prob_theta_doc+=prob_theta_doc[docId][j]
        for j in range(1, kmax):
            prob_theta_doc[docId][j]/=sum_prob_theta_doc
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

while (log_prob_C_new > log_prob_C_old):
#Expectation part 
    for docId in dict2.keys():
        tempTl = timeStamps[docId]
        for word in dict2[docId]['words'].keys():
            if word in keyWords:
                numeratorZ = {}
                xigmaNumeratorZ = 0
                for j in range(1, kmax):
                    numeratorZ[j] = (1 - lambdaB) * prob_word_theta[j][word] \
                    * ((1 - lambdaTl) * prob_theta_doc[docId][j]+ lambdaTl \
                         * prob_theta_timeloc[tempTl][j])            
                for i in range(1, kmax):
                    xigmaNumeratorZ += numeratorZ[i]
                denominatorZ = lambdaB * prob_w_thetaB[word] + xigmaNumeratorZ
                for i in range(1, kmax):
                    prob_Zdw_equalto_J[docId][word][i] = numeratorZ[i] / denominatorZ  
                    
                for j in range(1, kmax):
                    tempTl = timeStamps[docId]
                    #print prob_theta_timeloc[tempTl][j]
                    denominatorY = (1 - lambdaTl) * prob_theta_doc[docId][j] + lambdaTl * prob_theta_timeloc[tempTl][j]
    #                if denominatorY == 0:
    #                    denominatorY = 0.000001#initialization
                    #print denominatorY
                    if denominatorY==0:
                        denominatorY=0.1
                        
                    prob_Ydwj_equalto_one[docId][word][j] = (lambdaTl * prob_theta_timeloc[tempTl][j])\
                     / denominatorY   
                     
    print 'this is prob_theta_timeloc', prob_theta_timeloc 
#Maximization part
    #(1)
    for docId in dict2.keys():
        xigmaThetaD = 0
        xigmaThetaTL = 0#attention
        #tempTl = timeStamps[docId]
        xigmaThetaJD = {} 
        for j in range(1, kmax): 
            if j not in xigmaThetaJD.keys():
                xigmaThetaJD[j] = 0
            for word in dict2[docId]['words'].keys():
                if word in keyWords:
                    thetaJD = dict2[docId]['words'][word] * prob_Zdw_equalto_J[docId][word][j] \
                    * (1 - prob_Ydwj_equalto_one[docId][word][j])
                    xigmaThetaJD[j] += thetaJD
                    xigmaThetaD += thetaJD 
            #xigmaThetaD += xigmaThetaJD[j]
#        if xigmaThetaD == 0:
#            xigmaThetaD = 0.000001#initialization
        for i in range(1, kmax):
            prob_theta_doc[docId][i] = xigmaThetaJD[i] / xigmaThetaD
    #(2)
    for stamp in timeStampToDocIdDict.keys(): 
        for docId in timeStampToDocIdDict[stamp]:
            xigmaThetaJTL = {} 
            for j in range(1, kmax):
                if j not in xigmaThetaJTL.keys():
                    xigmaThetaJTL[j] = 0
                for word in dict2[docId]['words'].keys():
                    if word in keyWords:
                        thetaTL = dict2[docId]['words'][word] * prob_Zdw_equalto_J[docId][word][j] \
                        * prob_Ydwj_equalto_one[docId][word][j]
                        xigmaThetaJTL[j] += thetaTL
                        xigmaThetaTL += thetaTL
                #xigmaThetaTL += xigmaThetaJTL[j]
    #        if xigmaThetaTL == 0:
    #            xigmaThetaTL = 0.000001#initialization
        for i in range(1, kmax):
            prob_theta_timeloc[stamp][i] = xigmaThetaJTL[i] / xigmaThetaTL          
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
                    tempProbZ = prob_Zdw_equalto_J[docId][word][j]
                wTheta = tempWordCount * tempProbZ
                xigmaWTheta[word] += wTheta
            xigmaTheta += xigmaWTheta[word]
#        if xigmaTheta == 0:
#            xigmaTheta = 0.000001#initialization    
        for word in keyWords:
            prob_word_theta[j][word] = xigmaWTheta[word] / xigmaTheta
# the stop condition 
    log_prob_C = 0
    for docID in dict2.keys():
        tempTl = timeStamps[docId] 
        tempOuter = 0
        for word in dict2[docId]['words'].keys():
            if word in keyWords:
                tempaaa = dict2[docId]['words'][word] * log10(lambdaB * prob_w_thetaB[word])
                tempbbb = 0
                for j in range(1, kmax):
                    tempbbb += prob_word_theta[j][word] * ((1 - lambdaTl) \
                        * prob_theta_doc[docId][j] + lambdaTl * prob_theta_timeloc[tempTl][j])
                tempbbb = tempbbb * (1 - lambdaB)
                temp1 = tempaaa + tempbbb
                tempOuter += temp1
        log_prob_C += tempOuter
    log_prob_C_old = log_prob_C_new
    log_prob_C_new = log_prob_C
    print 'log_prob_C_new',log_prob_C_new
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
f= open('./temproaltheme9.txt','w')
for testTheme in range(1,kmax):
    prob_t_theme = {}
    prob_t_theme_numerator = {}
    prob_t_theme_denominator = 0
    for time in timeStampToDocIdDict.keys():
        prob_t_theme_numerator[time]=prob_theta_timeloc[time][testTheme]
        prob_t_theme_denominator+=prob_t_theme_numerator[time]
    for time in timeStampToDocIdDict.keys():
        prob_t_theme[time]=prob_t_theme_numerator[time]/prob_t_theme_denominator
    print >>f, prob_t_theme, '\n' 
    
for theme in range(1,kmax):
    sorted_x = sorted(prob_word_theta[theme].iteritems(), key=operator.itemgetter(1), reverse=True)
    print>>f, sorted_x, '\n'
f.close()

