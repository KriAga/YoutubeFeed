from app import config


class Youtube:
    def __init__(self, mongo_client, logger):
        self.logger = logger
        self.__meta_coll = mongo_client[config['mongo_db_name']][config['meta_collection']]
        self.__data_coll = mongo_client[config['mongo_db_name']][config['data_collection']]

    def get_videos(self, search, page=1, videos_per_page=10):
        try:
            selection_query = {"$text": {"$search": search}} if search else {}
            total_videos = self.__data_coll.count_documents(
                selection_query) if search else self.__data_coll.count_documents({})
            data = list(
                self.__data_coll.find(selection_query).sort('pub_datetime', -1).skip(
                    (page - 1) * videos_per_page).limit(
                    videos_per_page))
            return {'total_videos': total_videos,
                    'current_page': page,
                    'videos_per_page': videos_per_page,
                    'data': data}, 200
        except Exception as err:
            self.logger.error(err)
            return {"message": "Oops, something went wrong..."}, 400
