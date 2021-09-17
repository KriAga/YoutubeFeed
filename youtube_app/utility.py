import pymongo
import pymongo.errors
from config import mongo_url
import logging


def get_mongo_client():
    # connecting to mongodb database
    try:
        mongo_client = pymongo.MongoClient(mongo_url)
        return mongo_client
    except pymongo.errors.ServerSelectionTimeoutError as err:
        raise err


def get_logger():
    # Creating file logger
    logger = logging.getLogger("youtube")
    logger.setLevel(level=logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)
    return logger
