import json
import os

# config file that stores all the search_term paramters and api keys
config = json.load(open('config.json'))
# picking up the mongo config values from the system environment for docker
# mongo_url = "mongodb://{host}:{port}/".format(host=os.environ.get("MONGO_HOST"), port=os.environ.get("MONGO_PORT"))
# To be utilised when running locally 
mongo_url = "mongodb://{host}:{port}/".format(host="127.0.0.1", port="27017")
