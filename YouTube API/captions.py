# Downloads the enUS, .srt captions of a list of videos from YouTube.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import httplib2
import os
import sys
import csv
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
startTime = time.time()

reload(sys)
sys.setdefaultencoding('utf-8')

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
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube",
  "https://www.googleapis.com/auth/yt-analytics.readonly","https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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


def get_authenticated_services():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)

  return (youtube)



def getFilename(youtube, videoid):
    file_response = youtube.videos().list(
    id=videoid,
    part='fileDetails').execute()
    try:
      filename = file_response["items"][0]["fileDetails"]["fileName"]
    except IndexError:
      return "Video not public."
    return filename  

def list_captions(youtube, video_id):
  results = youtube.captions().list(
    part="snippet",
    videoId=video_id
  ).execute()
  try:
    output = results['items'][0]['id']
  except IndexError:
    output = 'na'  
  return output

def get_captions(youtube, caption_id, video_id):
  if caption_id == 'na':
    return
  subtitle = youtube.captions().download(
    id=caption_id,
    tfmt='srt'
  ).execute()
  title = getFilename(youtube, video_id)
  format_index = title.find('.')
  title = title[0:format_index]
  title = title+'.en_US.srt'
  title = title.replace('/','')
  with open('./subtitles/'+title,'wb') as output:
    output.write(subtitle)
    



if __name__ == '__main__':
  argparser.add_argument("--source", help="Set the channel ID. Default is WatchMojo.com", default='videolist')


  args = argparser.parse_args()
  youtube = get_authenticated_services()

  try:
    with open (args.source+'.csv') as allvids:
      reader = csv.DictReader(allvids)
      videos = []
      for row in reader:
        videos.append(row['ID'])   
    for i in range(0,len(videos)):
      sys.stdout.write('\rCurrently getting information for: %s Progress: %i/%i' % (str(videos[i]), int(i)+1, int(len(videos))))
      sys.stdout.flush()
      try:
        output = list_captions(youtube, videos[i])
        get_captions(youtube, output, videos[i])  
      except HttpError, e:
        continue
    print "\nDone."
    print "It took", time.time()-startTime, 'seconds to get data from', i+1, 'videos.'  
  except KeyboardInterrupt:
    print "User aborted."
    print "You waited,", time.time()-startTime, 'seconds before giving up.'
   
