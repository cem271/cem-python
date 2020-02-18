#By Cem Ertekin. Made for WatchMojo
#Can feed the video_ids either via command line or by editing the videoids variable in the code.
#Saves all comments in a YT video in a .txt file.
#Usage: python getComments4.py --videoid="{id here}"

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from apiclient.discovery import build

import re
import csv
import os
import urllib2
import sys

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "[INSERT YOUR OWN]"


def get_comment_threads(youtube, video_id, comments):
  threads = []
  results = youtube.commentThreads().list(
     part="snippet",
     videoId=video_id,
     textFormat="plainText",
   ).execute()

  #Get the first set of comments
  for item in results["items"]:
    threads.append(item)
    comment = item["snippet"]["topLevelComment"]
    text = comment["snippet"]["textDisplay"]
    username = comment["snippet"]["authorDisplayName"]
    comments.append(username + ' says: \n' + text)

  #Keep getting comments from the following pages
  while ("nextPageToken" in results):
    results = youtube.commentThreads().list(
      part="snippet",
      videoId=video_id,
      pageToken=results["nextPageToken"],
      textFormat="plainText",
    ).execute()
    for item in results["items"]:
      threads.append(item)
      comment = item["snippet"]["topLevelComment"]
      text = comment["snippet"]["textDisplay"]
      username = comment["snippet"]["authorDisplayName"]
      comments.append(username + ' says: \n' + text)

  print "Total threads: %d" % len(threads)

  return threads


def get_comments(youtube, parent_id, comments):
  results = youtube.comments().list(
    part="snippet",
    parentId=parent_id,
    textFormat="plainText"
  ).execute()

  for item in results["items"]:
    text = item["snippet"]["textDisplay"]
    username = item["snippet"]["authorDisplayName"]
    comments.append(username + ' says: \n'+text)

  return results["items"]

if __name__ == "__main__":
  argparser.add_argument("--videoid", help="Required; ID for video for which the comments will be returned.")
  args = argparser.parse_args()
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
  try:
    video = urllib2.urlopen('https://www.youtube.com/watch?v='+args.videoid)
    source = video.read()
    beginning = source.find("<title>")+7
    end = source.find("</title>", beginning)
    title = source[beginning:end]
    title = title.replace(' - YouTube', '')

    output_file = open(title+'.txt', "w")
    comments = []
    video_comment_threads = get_comment_threads(youtube, args.videoid, comments)

    for thread in video_comment_threads:
      get_comments(youtube, thread["id"], comments)

    for comment in comments:
      output_file.write(comment.encode("utf-8") + "\n")

    output_file.close()
    #print "Total comments: %d" % len(comments)
    


  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)