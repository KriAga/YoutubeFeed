import os
import json
import googleapiclient.discovery
import googleapiclient.errors
from apiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pymongo
from video import Video
import time
from datetime import datetime, timedelta

# config file that stores all the query paramters and api keys
config = json.load(open('config.json'))

# connecting to mongodb database
mongo_client = pymongo.MongoClient(config['mongodb_url'])
mongo_config = mongo_client['mongo_db_name']['mongo_coll_config']
mongo_data = mongo_client['mongo_db_name']['mongo_coll_data']


def init_db():
    # inserting current time as the first published time for all the queries
    docs=[]
    for query_string in config['find_videos_for']: # Allowing multiple queries to be made
        docs.append({'query_string':query_string, "start_time": int(time.time())})
    mongo_config.insert_many(docs)


def insert_db():
    print("inserted")
    pass


# function that is going to update the db with the video details
def update_data():
    print('update_data')

    for query in mongo_config.find():
        # setting up the connection with youtube api
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = build(config['api_service_name'], config['api_version'], developerKey=config['DEVELOPER_KEY'])

        # setting up the query parameters from the config file
        request = youtube.search().list(
            part="snippet",
            order=config['order_by'],
            q=query['query_string'],
            publishedAfter=datetime.fromtimestamp(int(query['start_time'])).isoformat('T') +'Z', # getting epoch from db and converting it to RFC 3339 formatted date-time value
            type=config['type'],
            maxResults=config['max_results'] # trying to get as many as results possible in just one call
        )
        response = request.execute()

        # iterating on all the item/video results
        for response_obj in response['items']:
            video_obj = Video(response_obj['snippet']['title'], 
                response_obj['snippet']['description'], 
                response_obj['snippet']['publishTime'], 
                response_obj['snippet']['thumbnails'])
            # print(video_obj.title)
            insert_db()

        mongo_config.update({'query_string':query['query_string']}, {"$set":{'start_time':int(query['start_time'])+10}})


# Schdeuler code to schedule the updation of the db every 10 seconds
sched = BackgroundScheduler(daemon=True)
sched.add_job(update_data,'interval', seconds=10)
sched.start()

app = Flask(__name__)

# dummy api endpoint to run flask along with scheduler
@app.route("/home")
def home():
    """ Function for test purposes. """
    return "Welcome Home :) !"


if __name__ == "__main__":
    init_db() # initialising the db with the query params and the start_time 
    app.run()