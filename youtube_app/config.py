import json
import os

# config file that stores all the search_term paramters and api keys
config = json.load(open('config.json'))

mongo_url = "mongodb://{host}:{port}/".format(host=os.environ.get("MONGO_HOST"), port=os.environ.get("MONGO_PORT"))
# mongo_url = "mongodb://{host}:{port}/".format(host="0.0.0.0", port="27017")
