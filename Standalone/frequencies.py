# This was custom built for to read the output of another script that made use
# of YouTube's live chat API. The output of that script was a .txt file that listed
# a username and that user's message on each line. This script makes use of
# two big list of 'positive' and 'negative' words and breaks down the frequency
# to see if the audience reaction was mostly positive or negative.

import string
import re
import operator

def checkFreq(wordArray):	
    text = ''
    for word in wordArray:
    	text += word
    for ch in '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~':
        text = string.replace(text, ch, ' ')   	
    text1 = open('positive.txt','r').read()
    positive = string.split(text1)

    text2 = open('negative.txt','r').read()
    
    negative = string.split(text2)
    pwords = []
    nwords =[]
    pcount = 0
    ncount = 0
    others = 0
    otherwords =[]
    words = text.split()
    topCount = 0
    topWords=[]
    posCounts ={}
    negCounts ={}

    for word in words:
    	if word == 'top':
    		topCount += 1
    		topWords.append(word)
    	elif word in positive:
    		pcount += 1
    		pwords.append(word)
    	elif word in negative:
    		ncount += 1
    		nwords.append(word)
    	else:
    		others +=1
    		otherwords.append(word)	

    for nay in nwords:
    	negCounts[nay] = negCounts.get(nay,0) + 1

    for yay in pwords:
    	posCounts[yay] = posCounts.get(yay,0) + 1		
 	
 		

	

    print 'Number of positive words:', pcount
    print 'Here are all the positive words:'
    print  posCounts
    print 'Number of negative words:', ncount
    print 'Here are all the negative words:'
    print negCounts
    print 'Number of other words:', others
    #print 'Here are the rest of the words:\n', otherwords        

def countNeg(wordArray):
    for line in wordArray:
        line.translate(None,string.punctuation)
    text1 = open('negative.txt','r').read()
    negative = string.split(text1)
    nlines =[]
    ncount = 0
    ocount = 0
    ndict = {}
    for line in wordArray:
        negBoolean = False
        splitString = string.split(line)
        for word in negative:
            for keyword in splitString:
                if word == keyword:
                    negBoolean = True               
                else:
                    continue
        if negBoolean:
            nlines.append(line)
            ncount += 1
            negBoolean = False
        else:
            ocount += 1                     
    print "Number of negative lines: ", ncount
    #print nlines
                               

def countPos(wordArray):
    for line in wordArray:
        line.translate(None,string.punctuation)
    text1 = open('positive.txt','r').read()
    positive = string.split(text1)
    plines =[]
    pcount = 0
    ocount = 0
    pdict = {}
    for line in wordArray:
        posBoolean = False
        splitString = string.split(line)
        for word in positive:
            for keyword in splitString:
                if word == keyword:
                    posBoolean = True               
                else:
                    continue
        if posBoolean:
            plines.append(line)
            pcount += 1
            posBoolean = False
        else:
            ocount += 1                     
    print "Number of positive lines: ", pcount
    #print plines

def getLines(filename):
	text = open(filename,'r').read()
	text = string.lower(text)
	words = re.split('\n', text)
	newWords =[]
	saysIndex = 0
	for word in words:
		saysIndex = word.find('says:')
		newWord = word[saysIndex+6:]
		newWords.append(newWord.lower())
	return newWords	

def getUsers(filename):
    text = open(filename,'r').read()
    text = string.lower(text)
    words = re.split('\n', text)
    users =[]
    userIndex = 0
    for word in words:
        userIndex = word.find('says:')
        user = word[:userIndex-1]
        users.append(user)
    return users  

def findUniqueUsers(userArray):
    users = {}
    for user in userArray:
        users[user] = users.get(user,0) + 1
    sortedUsers = sorted(users.items(), key=operator.itemgetter(1), reverse=True)
    print 'Total number of unique chat users: ',len(users)
    list_users= []
    for user in sortedUsers:
        list_users.append(user[0])
   # print "Here's a list of unique users, ordered by number of chat messages:\n"
    print list_users
    print users   
    return users    


def countTop10s(wordArray):
    top10Count = 0
    top10Lines=[]
    for line in wordArray:
        if "top 10" in line:
            top10Count += 1
            top10Lines.append(line)
        else:
            continue    
    print "Number of times someone said Top 10: ",top10Count
    return top10Lines        

def countRunningOutOfIdeas(wordArray):
    ideasCount = 0
    ideasLines=[]
    for line in wordArray:
        if "ideas" in line:
            ideasCount +=1
            ideasLines.append(line)
            #print line
        else:
            continue
    print "Number of times someone said we're running out of ideas: ",ideasCount            
    return ideasLines

 			
words = getLines('WMUKLIVECHAT.txt')
users = getUsers('WMUKLIVECHAT.txt')
#checkFreq(words)
findUniqueUsers(users)
countTop10s(words)
countRunningOutOfIdeas(words)

countNeg(words)
countPos(words)

