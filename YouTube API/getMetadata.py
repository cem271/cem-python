# coding=utf-8
#By Cem Ertekin. Made for WatchMojo.
# Grabs the metadata of any video for all videos in a videolist.csv.

import json
import datetime
import httplib2
import os
import sys
import csv
import time

reload(sys)
sys.setdefaultencoding('utf-8')

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
startTime = time.time()


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data and YouTube Analytics
# APIs for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# These OAuth 2.0 access scopes allow for read-only access to the authenticated
# user's account for both YouTube Data API resources and YouTube Analytics Data.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly","https://www.googleapis.com/auth/yt-analytics-monetary.readonly","https://www.googleapis.com/auth/youtubepartner"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v2"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This function authenticates this script, creating an oauth2 file
# and storing it in the same directory as the script. If the oauth2 file
# already exists, it simply loads it up.
def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("yes-oauth2.json")
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)


# Makes a query to get information of a video with the given video id. Snippet
# includes all kinds of metadata about the video.
def queryVideo(youtube,video_id):
  query_response = youtube.videos().list(
    part="snippet",
    id=video_id
    ).execute()
  return query_response

# This function reads a list of ids from a CSV file and prints out the output into
# a different CSV file. The names of the files are declared when you run
# the script from terminal.
def getMetadata(output, source):
  with open (source+'.csv') as allvids:
    reader = csv.DictReader(allvids)
    videos = []
    for row in reader:
      videos.append(row['ID'])
    #print videos  
  with open (output+'.csv', 'wb') as output:
    writer = csv.writer(output)
    i = 0
    headers = ['ID','title','description','tags']
    writer.writerow(headers)
    while i < len(videos):
      videoid = videos[i]
      # Progress bar.
      sys.stdout.write('\r \x1b[K Currently getting information for: %s Progress: %i/%i' % (str(videoid), int(i)+1, int(len(videos))))
      sys.stdout.flush()
      if len(videoid) < 11:
      	print
      	print "ERROR. Video ID: %s not valid." % str(videoid)
      	quit()
      (youtube, youtube_analytics) = get_authenticated_services(args)
      
      

      result = queryVideo(youtube,videoid)
      title = result['items'][0]['snippet']['title']
      description = result['items'][0]['snippet']['description']
      tags = result['items'][0]['snippet']['tags']
      # Need to convert the tags list/array into a string, otherwise the UNICODE
      # stuff messes the cell up.
      tags_new=''
      for tag in tags:
        tags_new = tags_new+','+tag
      rows = []
      rows.append(videoid)
      rows.append(title.encode("utf-8"))
      rows.append(description.encode("utf-8"))
      rows.append(tags_new)

      writer.writerow(rows)
      i += 1

  print "\nDone."
  # Timer to see if the code is efficient.
  print "It took", time.time()-startTime, 'seconds to get data from', i, 'videos.'


if __name__ == "__main__":
  now = datetime.datetime.now()
  # Vestigial code from the template I took from Google while building this. Could probably be removed.
  argparser.add_argument("--name", help="Set output filename. Default is output.csv", default='output')
  argparser.add_argument("--source", help="Set source of video Ids. Default is videolist.csv", default='videolist')
  argparser.add_argument("--start_date", help="Set start date. YYYY-MM-DD.")
  argparser.add_argument("--end_date", help="Set end date. YYYY-MM-DD")
  args = argparser.parse_args()


  (master_auth, master_aauth) = get_authenticated_services(args)
  try:
    print "Press CTRL+C to quit running the program."
    print
    print
    print "The filenames should be entered without the .csv at the end."
    print

    source = raw_input("Filename of source: ")
    output = raw_input("Filename of output: ")
    getMetadata(output, source)

  except KeyboardInterrupt:
    print
    print "User aborted."
    print "You waited", time.time()-startTime, 'seconds before giving up.'
  except KeyError, e:
  	print
  	print "ERROR: The column where the video IDs are listed should be called ID."    
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)  