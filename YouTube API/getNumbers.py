#By Cem Ertekin. Made for WatchMojo.
#Returns the first few day revenues of a list of given videos as a CSV file.
#Usage: python getNumbers.py --count="{X, where X is first X days}" --name="{name of output file}" --source="{name of input list of videoids}"

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
  "https://www.googleapis.com/auth/yt-analytics.readonly","https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]
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
def get_authenticated_services(args, channel):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % channel)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)

def getName(youtube,videoid):
  videoname=''
  response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  videoname = response["items"][0]["snippet"]["title"]
  return videoname


# Makes a query to get analytics information of a video with the given video id.
def queryVideo(youtube_analytics,channel_id,videoid,start_date,end_date,metrics):
  analytics_query_response = youtube_analytics.reports().query(
    ids="channel==%s" % channel_id,
    metrics=metrics,
    dimensions='video',
    startDate=start_date,
    endDate=end_date,
    maxResults=10,
    filters='video==%s' % videoid
    ).execute()
  # print analytics_query_response
  return analytics_query_response  

def getChannel(youtube,videoid):
    channel=''
    response=youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
    try:
      channel = response["items"][0]["snippet"]["channelId"]
    except IndexError:
      return "na"
    return channel

def getChannelName(youtube,channelid):
	channel=''
	response=youtube.channels().list(
	id=channelid,
	part='snippet'
	).execute()
	try:
		channel = response["items"][0]["snippet"]["title"]
	except IndexError:
		return "na"
	return channel		

def getAnalytics(youtube_analytics, start_date, end_date, output, source, metrics):
  if metrics == 'all':
    metrics = "views,likes,dislikes,shares,comments,estimatedMinutesWatched,averageViewPercentage,estimatedRevenue"

  with open (source+'.csv') as allvids:
    reader = csv.DictReader(allvids)
    videos = []
    for row in reader:
      videos.append(row['ID'])
  with open (output+'.csv', 'wb') as output:
    writer = csv.writer(output)
    i = 0
    headers = ['Title','ID']
    metrics_array = metrics.split(",")
    for metric in metrics_array:
      headers.append(metric)
    writer.writerow(headers)
    while i < len(videos):
      videoid = videos[i]
      
      channel_id = getChannel(master_auth,videoid)
      channel_name = getChannelName(master_auth,channel_id)
      sys.stdout.write('\r \x1b[K Currently getting information for: %s Progress: %i/%i Channel: %s' % (str(videoid), int(i)+1, int(len(videos)), str(channel_name)))
      sys.stdout.flush()
      if len(videoid) < 11:
      	print
      	print "ERROR. Video ID: %s not valid." % str(videoid)
      	quit()
      (youtube, youtube_analytics) = get_authenticated_services(args, channel_id)
      title = getName(youtube,videoid)
      

      result = queryVideo(youtube_analytics,channel_id,videoid,start_date,end_date,metrics)
      if result.get("rows") == []:
        rows = ['n/a',videoid]
        rows.append(0)
        writer.writerow(rows) 
      else:
        for row in result.get("rows",[]):
          rows = [title]
          for value in row:
            rows.append(value)      
          writer.writerow(rows)

           
      i += 1


  print "\nDone."
  print "It took", time.time()-startTime, 'seconds to get data from', i, 'videos.'


if __name__ == "__main__":
  now = datetime.datetime.now()

  argparser.add_argument("--name", help="Set output filename. Default is output.csv", default='output')
  argparser.add_argument("--source", help="Set source of video Ids. Default is videolist.csv", default='videolist')
  argparser.add_argument("--start_date", help="Set start date. YYYY-MM-DD.")
  argparser.add_argument("--end_date", help="Set end date. YYYY-MM-DD")
  args = argparser.parse_args()


  (master_auth, youtube_analytics) = get_authenticated_services(args, "master_auth")
  try:
    print "Press CTRL+C to quit running the program."
    print
    print "Some example metrics you can return: estimatedRevenue, views, likes, "
    print "dislikes, shares, comments, estimatedMinutesWatched, averageViewPercentage" 
    print
    print "The filenames should be entered without the .csv at the end."
    print "Dates should be in the following format: YYYY-MM-DD"
    print "Each metric should be separated by commas, as in the example above."
    print

    source = raw_input("Filename of source: ")
    output = raw_input("Filename of output: ")
    start_date = raw_input("Enter the first date: ")
    end_date = raw_input("Enter the last date: ")
    metrics = raw_input("Enter metrics: ")
    

    getAnalytics(youtube_analytics, start_date, end_date, output, source, metrics)

  except KeyboardInterrupt:
    print
    print "User aborted."
    print "You waited", time.time()-startTime, 'seconds before giving up.'
  except KeyError, e:
  	print
  	print "ERROR: The column where the video IDs are listed should be called ID."    
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)  