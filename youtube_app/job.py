from config import config
from pymongo import UpdateOne
import time
from datetime import datetime

class Video:
    def __init__(self, response):
        # Youtube api response parser
        self.video_id = response['id']['videoId']
        self.title = response['snippet']['title']
        self.description = response['snippet']['description']
        self.thumbnails = response['snippet']['thumbnails']
        self.channel_title = response['snippet']['channelTitle']

class Crawler:
    def __init__(self, mongo_client, logger):
        # initialising the db with the search_term params and the start_time
        self.logger = logger
        self.__meta_coll = mongo_client[config['mongo_db_name']][config['meta_collection']]
        self.__data_coll = mongo_client[config['mongo_db_name']][config['data_collection']]
        self.init_db()
    
    # initialising the configuration details of the search queries in the db
    def init_db(self):
        self.__meta_coll.drop()
        self.__data_coll.drop()
        docs = []
        for query_string in config['find_videos_for']:  # Allowing multiple queries to be made
            # inserting current time as the first published_time/start_time for all the queries
            docs.append({'_id': query_string, "start_time": int(time.time())})
        # creating bulk updates
        upserts = [UpdateOne({'_id': doc['_id']}, {'$set': doc}, upsert=True) for doc in docs]
        self.__meta_coll.bulk_write(upserts)
