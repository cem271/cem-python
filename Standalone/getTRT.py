# Placed inside a folder containing any number of videos, this script will
# create a CSV file that lists the total run time of those videos. Uses moviepy.

from moviepy.editor import VideoFileClip
import os
import sys
import datetime
import csv


def getCreated(filename):
	t = os.path.getmtime(filename)
	return datetime.datetime.fromtimestamp(t)


print
print
print
print
print
with open('output.csv','wb') as output:
	writer = csv.writer(output)
	headers = ['Filename', 'Date Created', 'TRT']
	writer.writerow(headers)
	for filename in os.listdir("."):
		if filename.startswith("."):
			continue
		if filename == 'getTRT.py':
			continue
		if filename == 'output.csv':
			continue
		clip = VideoFileClip(filename)
		seconds = clip.duration
		del clip.reader
		del clip
		minutes = seconds/60
		if minutes < 10:
			created = getCreated(filename)
			row = [filename,str(created.year)+'/'+str(created.month)+'/'+str(created.day),str(minutes)]
			writer.writerow(row)



print
print
print

