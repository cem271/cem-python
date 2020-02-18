# This script reads through Final Cut XML files that have made use of Getty content 
# and creates a CSV file, listing every occurance of the Getty content. By default
# it expects that the XML files are placed in a folder called xmls that's placed
# in the same directory as the script.

from bs4 import BeautifulSoup as BS
import os
import csv
import sys
import time
import datetime

def getFilenames(location):
	filenames = []
	for filename in os.listdir(location):
		if filename.startswith("."):
			continue
		filenames.append(filename)
	return filenames		

def getGettyIds(output, filenames, location):
	with open (output, 'wb') as gettyIDs:
		writer = csv.writer(gettyIDs)
		headers = ['FileName','gettyID']
		writer.writerow(headers)		
		for filename in filenames:
			sys.stdout.write('\r \x1b[K Progress: %i/%i Currently parsing: %s' % (filenames.index(filename)+1,len(filenames),str(filename)))
			sys.stdout.flush()
			infile = open(location+filename,"r")
			contents = infile.read()
			soup = BS(contents,'xml')
			titles = soup.find_all('clip') + soup.find_all('video')
			parsed_names = []
			for title in titles:
				name = title.get('name')
			#	print name
				if name != None and "Getty" in name and "Outro" not in name and "Intro" not in name :					
					if name in parsed_names:
						continue
					
					rows = []
					
					if name==None:
						continue			
				#	print name                   #To figure out what's causing the ID to be incorrect.
					index_i = name.find('-')+1
					sub = name[index_i:]
					index_o = sub.find('_')
					
					if "mr" in sub or "wi" in sub:
						index_o = sub.find("_",sub.find("_")+1)				
					
					if "lpi" in sub:
						index_o=len(sub)

					if "sb" in sub:
						index_o=len(sub)	
					
					if index_o == -1:
						index_o=len(sub)

						
					
					getty_ID = sub[:index_o]
					rows.append(filename[:filename.find('.fcpxml')])
					rows.append(getty_ID)
					writer.writerow(rows)

					if name not in parsed_names:
						parsed_names.append(name)

if __name__ == "__main__":
	startTime = time.time()
	try:		
		location = sys.argv[1]+"/"
		output = sys.argv[2]+".csv"
		filenames = getFilenames(location)
		getGettyIds(output, filenames, location)
		print
		print "It took", time.time()-startTime, 'seconds to parse', len(filenames), 'files.'
	except IndexError, e:
		try:
			location = "xmls/"
			filenames = getFilenames(location)
			getGettyIds(filenames, location)
			print
			print "It took", time.time()-startTime, 'seconds to parse', len(filenames), 'files.'
		except OSError, e:
			print
			print "ERROR: XML files should be placed in a separate folder that's in the same director as xmlsparser.py"
			print "By default, the folder name should be xmls. If the folder name is different, you should specify"
			print "using the following format: python xmlparser.py FOLDERNAME OUTPUTNAME"		
			print
	except OSError, e:
		print
		print "ERROR: You specified an incorrect location for your XML files. Please check the name."	
		print
	except NameError:
		print "ERROR: You specified an incorrect location for your XML files. Please check the name."	
	except KeyboardInterrupt:
		print
		print "User aborted."
		print "You waited", time.time()-startTime, 'seconds before giving up.'