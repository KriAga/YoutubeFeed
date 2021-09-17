class Video:
    def __init__(self, response):
        # Youtube api response parser
        self.video_id = response['id']['videoId']
        self.title = response['snippet']['title']
        self.description = response['snippet']['description']
        self.thumbnails = response['snippet']['thumbnails']
        self.channel_title = response['snippet']['channelTitle']
