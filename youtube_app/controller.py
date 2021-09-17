from flask_restx import Api, Resource, fields, reqparse
from flask import jsonify, request, Response
from handler import Youtube
from app import api, app, logger
import json

ns = api.namespace('', description='Youtube search')

search_arguments = reqparse.RequestParser()
search_arguments.add_argument('search', type=str, location='args', required=False)
search_arguments.add_argument('videos_per_page', type=int, location='args', required=False, default=10)
search_arguments.add_argument('page', type=int, location='args', required=False, default=1)

youtube_handler = Youtube(app.db, logger)


@ns.route('/videos')
class Youtube(Resource):
    @ns.expect(search_arguments, validate=True)
    def get(self):
        search = request.args.get("search", None)
        videos_per_page = int(request.args.get("videos_per_page"))
        page = int(request.args.get("page"))

        data, status_code = youtube_handler.get_videos(search, page, videos_per_page)
        return Response(response=json.dumps(data), status=status_code)

