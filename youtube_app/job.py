from googleapiclient.discovery import build
from config import config
from pymongo import UpdateOne
import time
from datetime import datetime
import apiclient


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
        # meta_coll.drop()
        # data_coll.drop()
        docs = []
        for query_string in config['find_videos_for']:  # Allowing multiple queries to be made
            # inserting current time as the first published_time/start_time for all the queries
            docs.append({'_id': query_string, "start_time": int(time.time())})
        # creating bulk updates
        upserts = [UpdateOne({'_id': doc['_id']}, {'$set': doc}, upsert=True) for doc in docs]
        self.__meta_coll.bulk_write(upserts)

        # Create text index on title and description fields
        if 'title_description' not in self.__data_coll.index_information().keys():
            self.__data_coll.create_index([('title', 'text'), ('description', 'text')],
                                          weights={'title': 2, 'description': 1},
                                          name='title_description')
        self.logger.info("DB iniitialized successfully")

    # function that is going to update the db with the video details
    def update_data(self):
        # searching on all the
        for search_term in self.__meta_coll.find():
            try:
                key_worked = False  # Flag to track if the key worked or not
                for key in config['DEVELOPER_KEY']:

                    try:
                        # setting up the connection with youtube api
                        youtube = build(config['api_service_name'], config['api_version'], developerKey=key)
                        # setting up the query parameters from the config file

                        request = youtube.search().list(
                            part="snippet",
                            order=config['order_by'],
                            q=search_term['_id'],
                            publishedAfter=datetime.fromtimestamp(int(search_term['start_time'])).isoformat('T') + 'Z',
                            # getting epoch from db and converting it to RFC 3339 formatted date-time value
                            type=config['type'],
                            maxResults=config['max_results']
                            # trying to get as many as results possible in just one call
                        )
                        response = request.execute()
                        key_worked = True
                    except apiclient.errors.HttpError as err:
                        self.logger.warning(f"Failed to list youtube api with key {key[0:5]}...")
                        continue

                    if key_worked:
                        # iterating on all the item/video results
                        videos_arr = []
                        for response_obj in response['items']:

                            video_obj = Video(response_obj)

                            utc_dt = datetime.strptime(response_obj['snippet']['publishTime'], '%Y-%m-%dT%H:%M:%SZ')
                            published_datetime_epoch = int((utc_dt - datetime(1970, 1, 1)).total_seconds())
                            meta = {
                                "_id": video_obj.video_id,
                                "query_string": search_term['_id'],
                                "updated_time": datetime.now().strftime("%Y%m%d_%H%M%S"),
                                "pub_datetime": published_datetime_epoch
                            }
                            videos_arr.append({**video_obj.__dict__, **meta})
                        upserts = [UpdateOne({'_id': video_detail['_id']}, {'$set': video_detail}, upsert=True) for
                                   video_detail
                                   in videos_arr]
                        self.__data_coll.bulk_write(upserts)
                    else:
                        self.logger.error("All the API tokens are exhausted! Please provide new tokens")
                        raise Exception("All the API tokens are exhausted! Please provide new tokens")

                self.__meta_coll.update_one({'_id': search_term['_id']},
                                            {"$set": {
                                                'start_time': int(search_term['start_time']) + config[
                                                    'update_interval']}})
                self.logger.info(f"Updated youtube feed for query : {search_term}")
            except Exception as err:
                self.logger.error(f"Failed to update youtube feed for query : {search_term} due to {str(err)}")
