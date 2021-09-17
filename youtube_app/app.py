from flask_restx import Api
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from config import config
from utility import get_mongo_client, get_logger
from job import Crawler

app = Flask(__name__)
api = Api(app)

# connecting to mongodb database
app.db = get_mongo_client()

logger = None


def set_logger():
    global logger
    logger = get_logger()


def register_controllers():
    from controller import ns
    api.add_namespace(ns)


# Scheduler code to schedule the updation of the db every 10 seconds
def set_scheduler():
    crawler = Crawler(app.db, logger)
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(crawler.update_data, 'interval', seconds=config['update_interval'])
    sched.start()


if __name__ == "__main__":
    set_logger()
    set_scheduler()
    register_controllers()
    app.run(host="0.0.0.0")
