import os
import json
import time
import re

import googleapiclient.discovery
import googleapiclient.errors
import apiclient
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta
from flask import Flask, jsonify, request

import pymongo
from pymongo import UpdateOne

from video import Video


# config file that stores all the search_term paramters and api keys
config = json.load(open('config.json'))

# connecting to mongodb database
mongo_client = pymongo.MongoClient(config['mongodb_url'])
mongo_config = mongo_client[config['mongo_db_name']][config['mongo_coll_config']]
mongo_data = mongo_client[config['mongo_db_name']][config['mongo_coll_data']]

# initialising the configuration details of the search queries in the db
def init_db():
    mongo_config.drop()
    mongo_data.drop()
    docs=[]
    for query_string in config['find_videos_for']: # Allowing multiple queries to be made
        # inserting current time as the first published_time/start_time for all the queries
        docs.append({'_id':query_string, "start_time": int(time.time())})
    # creating bulk updates
    upserts=[ UpdateOne({'_id':doc['_id']}, {'$set':doc}, upsert=True) for doc in docs]
    mongo_config.bulk_write(upserts)
    
# function that is going to update the db with the video details
def update_data():
    searching on all the 
    for search_term in mongo_config.find():
        key_worked = False # Flag to track if the key worked or not
        for key in config['DEVELOPER_KEY']:
            
            try:
                # setting up the connection with youtube api
                youtube = build(config['api_service_name'], config['api_version'], developerKey=key)
                print(search_term['_id'], datetime.fromtimestamp(int(search_term['start_time'])).isoformat('T') +'Z')
                # setting up the query parameters from the config file
                request = youtube.search().list(
                    part="snippet",
                    order=config['order_by'],
                    q=search_term['_id'],
                    publishedAfter=datetime.fromtimestamp(int(search_term['start_time'])).isoformat('T') +'Z', # getting epoch from db and converting it to RFC 3339 formatted date-time value
                    type=config['type'],
                    maxResults=config['max_results'] # trying to get as many as results possible in just one call
                )
                response = request.execute()
                key_worked = True
            except apiclient.errors.HttpError as err:
                print("Error with the key")
                continue

            if key_worked:
                # iterating on all the item/video results
                videos_arr = []
                for response_obj in response['items']:
                    utc_dt = datetime.strptime(response_obj['snippet']['publishTime'], '%Y-%m-%dT%H:%M:%SZ')
                    published_datetime_epoch = int((utc_dt - datetime(1970, 1, 1)).total_seconds())
                    video_obj = Video(response_obj['id']['videoId'],
                        response_obj['snippet']['title'], 
                        response_obj['snippet']['description'], 
                        published_datetime_epoch, 
                        response_obj['snippet']['thumbnails'],
                        response_obj['snippet']['channelTitle'])
                    # print(video_obj.title)
                    video_details = video_obj.__dict__
                    video_details['_id'] = video_details['video_id']
                    video_details['query_string'] = search_term['_id']
                    video_details['updated_time'] = datetime.now().strftime("%Y%m%d_%H%M%S")
                    videos_arr.append(video_details)
                    print("inserted", video_details['video_id'], video_details['pub_datetime'],video_details['updated_time'])
                upserts = [ UpdateOne({'_id':video_detail['_id']}, {'$set':video_detail}, upsert=True) for video_detail in videos_arr]
                mongo_data.bulk_write(upserts)

                if 'title_description' not in mongo_data.index_information().keys():
                    # Create text index on title and description fields
                    mongo_data.create_index([('title', 'text'), ('description', 'text')], weights={'title':2, 'description':1},
                            name='title_description')
                

        mongo_config.update_one({'_id':search_term['_id']}, {"$set":{'start_time':int(search_term['start_time'])+config['update_interval']}})
        

# Schdeuler code to schedule the updation of the db every 10 seconds
sched = BackgroundScheduler(daemon=True)
sched.add_job(update_data,'interval', seconds=config['update_interval'])
sched.start()

app = Flask(__name__)

# dummy api endpoint to run flask along with scheduler
@app.route("/home")
def home():
    """ Function for test purposes. """
    return "Welcome Home :) !"

@app.route("/videos")
def videos():
    search_query = request.args.get("search_query", None)
    videos_per_page = request.args.get("videos_per_page", 10)
    page_number = request.args.get("page_number", 0)
    
    selection_query = {"$or":[
        {"title": {'$regex' : f'.*{search_query}.*', '$options':'$i'}},
        {"description": {'$regex' : f'.*{search_query}.*', '$options':'$i'}}
    ]} if search_query else {} 
    total_videos =  mongo_data.find(selection_query).count() if search_query else mongo_data.count()
    data = list(mongo_data.find(selection_query).sort('pub_datetime', -1).skip(page_number*videos_per_page).limit(videos_per_page))
    
    response = {'total_videos': total_videos, 'current_page': page_number, 'videos_per_page': videos_per_page, 'data':data}
    return jsonify(response)


if __name__ == "__main__":
    init_db() # initialising the db with the search_term params and the start_time 
    app.run()