# Meant to be used with the output of keywords.py, this script
# picks two random keywords from that list. This was used as a
# random VS generator on a live show.

import random


def getRandom(keywords):
	text = open(keywords+'.txt','r').read()
	source = text.splitlines()
	num1 = random.randint(0,len(source))
	num2 = random.randint(0,len(source))
	print source[num1]
	print source[num2]

getRandom('keywords')	


