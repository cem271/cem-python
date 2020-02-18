# This does a YouTube search and returns all videos and their IDs that match the keyword provided.

#!/usr/bin/python
# -*- coding: utf-8 -*-

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
  "https://www.googleapis.com/auth/yt-analytics-monetary.readonly","https://www.googleapis.com/auth/youtube"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

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


def get_authenticated_services(args):
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
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)


def getTheThings(service, keyword, filename):
  startTime = time.time()
  request = service.search().list(part='snippet',channelId='[INSERT YOUR OWN or DELETE ENTIRELY]', maxResults=50, type='video', q=keyword, publishedAfter="2012-01-01T00:00:00Z")
  with open(filename+".csv", 'wb') as results:
    writer = csv.writer(results)
    headers = ['id','title']
    writer.writerow(headers)
    while request:

      response = request.execute()
      print "New page"
      
      for result in response.get("items",[]):

        pair =[]
        pair.append(result['id']['videoId'])
        pair.append(result['snippet']['title'])
        writer.writerow(pair)
        print result['id']['videoId']

      request = service.search().list_next(request, response)
  print 'Request took', time.time()-startTime,'seconds.'  

argparser.add_argument("--keyword", help="Set keyword.", default="watchmojo")
args = argparser.parse_args()

(youtube, youtube_analytics) = get_authenticated_services(args)

getTheThings(youtube, args.keyword, args.keyword)     