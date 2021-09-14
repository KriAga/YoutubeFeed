import os
import json
import googleapiclient.discovery
import googleapiclient.errors
from apiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# config file that stores all the query paramters and api keys
config = json.load(open('config.json'))

# function that is going to update the db with the video details
def update_database():
    # setting up the connection with youtube api
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = build(config['api_service_name'], config['api_version'], developerKey=config['DEVELOPER_KEY'])

    # setting up the query parameters from the config file
    request = youtube.search().list(
        part="snippet",
        order=config['order_by'],
        q=config['find_videos_for'],
        publishedAfter=config['start_time'],
        type=config['type']
    )
    response = request.execute()
    print(response)

# Schdeuler code to schedule the updation of the db every 10 seconds
sched = BackgroundScheduler(daemon=True)
sched.add_job(update_database,'interval', seconds=10)
sched.start()

app = Flask(__name__)

# dummy api endpoint to run flask along with scheduler
@app.route("/home")
def home():
    """ Function for test purposes. """
    return "Welcome Home :) !"


if __name__ == "__main__":
    app.run()