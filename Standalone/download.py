# This is a simple downloader, specifically designed for any list (.csv) of URLs containing
# video files in the MP4 format. 

import requests
import csv
import time
import sys

def read_csv():
	with open ('thing.csv') as allvids:
		reader = csv.DictReader(allvids)
		videos = []
		for row in reader:
			tupple = [row['Title'],row['Address']]
			videos.append(tupple)
		return videos	

def download(videos):	
	log = "download_data"
	for tupple in videos:
		filename = tupple[0]+'.mp4'
		url = tupple[1]
		with open (filename,"wb") as f:	
			response = requests.get(url, stream=True)			
			total_length = response.headers.get('content-length')

			if total_length is None:
				f.write(respnose.content)
			else:
				dl = 0
				total_length = int(total_length)
				for data in response.iter_content(chunk_size=4096):
					dl += len(data)
					f.write(data)
					done = int(50 * dl / total_length)
					sys.stdout.write("\r[%s%s] Progress: %i/%i Downloading: %s " % ('=' * done, ' ' * (50-done),videos.index(tupple)+1,len(videos),str(filename)) )    
	            	sys.stdout.flush()

	print
	print "It took", time.time()-startTime, 'seconds to download', len(videos), 'files.'		
		

startTime = time.time()
videos = read_csv()
download(videos)
