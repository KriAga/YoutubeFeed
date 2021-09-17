# Youtube Feed
An API to fetch latest videos from youtube sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.
This API utilises the [YouTube Search: list](https://developers.google.com/youtube/v3/docs/search/list) api, and creates a feed for all the set topics. The api keeps refreshing the database after ever set time interval. You can also control the cut off time for the videos that are published after a certain date and time. One can also search for the videos using a search api to fetch from the database.


## Tech Stack
The project is created using Python Language and has primarily implemented the following packages for the respective tasks.
- [FlaskX](https://pypi.org/project/flask-restx/) - Used primarily for the REST APIs.
- [APScheduler](https://pypi.org/project/APScheduler/) - To schedule the database updation at a set interval of time
- [PyMongo](https://pypi.org/project/pymongo/) - To connect to the MongoDB
- [Google APIs Client Library](https://pypi.org/project/google-api-python-client/) - To connect to the Google's YouTube Search:list API 
Please find the list of all the packages in the requirements.txt file

Besides Python the project also uses MongoDb for database and the project has also been dockerised. 

## How to run
- Clone the project
- You need to have Python 3.x and MongoDb installed in your system
- In the project root directory create a virtualenvironment using the command `virtualenv venv` and then activate it. [This document might help](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) 
- To install the dependencies use `pip install -r requirements.txt`
- There are a bunch of configs that need to set in the `config.json` file viz., `DEVELOPER_KEY`, `find_videos_for`, `update_interval` 
- To create your own Google Youtube API follow this [link](https://developers.google.com/youtube/v3/getting-started)
- Run the server using `python app.py`

## Use Docker
- Command to build the docker image `docker build -t YoutubeFeed:v1 .`
- Command to run docker `docker run -it --env-file env_file YoutubeFeed:v1`
