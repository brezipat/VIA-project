from flask import Flask
from flask_restplus import Api, Resource
import os
from os import listdir
from os.path import isfile, join
import json

"""Define Flask app"""
flask_app = Flask(__name__)
app = Api(app=flask_app,
          version="1.0",
          title="Json app",
          description="App for work with json file")

"""Define namespace"""
movies_name_space = app.namespace("Json", description='Work with json files')

@movies_name_space.route("/")
class ListJsonFiles(Resource):
    @app.doc(responses={200: 'OK'}, description="List all available json files")
    def get(self):
        data_files = [f for f in listdir('./') if isfile(join('./', f))]
        ret = []
        for file in data_files:
            if file.split('.')[-1] == 'json':
                ret.append(file)
        return ret

@movies_name_space.route("/<string:filename>")
class ListJson(Resource):
    @app.doc(responses={200: 'OK'}, description="View whole json file")
    def get(self, filename):
        if not os.path.exists(f"./{filename}"):
            movies_name_space.abort(400, status="File doesn't exist", statusCode="400")
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

@movies_name_space.route("/<string:filename>/<string:path>")
class ListJsonByPath(Resource):
    @app.doc(responses={200: 'OK'}, description="Views section of json file based on the give identifiers path. Seperate identifiers with comma")
    def get(self, filename, path):
        if not os.path.exists(f"./{filename}"):
            movies_name_space.abort(400, status="File doesn't exist", statusCode="400")
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        s = path.split(',')
        current = data
        for identifier in s:
            if identifier in current:
                current = current[identifier]
            else:
                return current
        return current

# @movies_name_space.route("/<string:filename>/replace")
# class AddToJson(Resource):
#     @app.doc(responses={200: 'OK'}, description="Replaces existing json file with new one that arrived in the post request message.")
#     def post(self, filename):
#         if not os.path.exists(f"./{filename}"):
#             movies_name_space.abort(400, status="File doesn't exist", statusCode="400")
#         return "Replaced existing json file with new one"


flask_app.run()
