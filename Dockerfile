FROM python:3.8-slim-buster

WORKDIR /app
ENV TZ="Asia/Kolkata"
RUN date
COPY youtube_app/ .
RUN pip3 install -r requirements.txt
CMD [ "python", "app.py"]
