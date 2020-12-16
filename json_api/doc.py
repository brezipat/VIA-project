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
        data_files = [f for f in listdir('./jsonData/') if isfile(join('./jsonData', f))]
        ret = []
        for file in data_files:
            if file.split('.')[-1] == 'json':
                ret.append(file)
        return ret

@movies_name_space.route("/<string:filename>")
class ListJson(Resource):
    @app.doc(responses={200: 'OK'}, description="View whole json file")
    def get(self, filename):
        if not os.path.exists(f"./jsonData/{filename}") or os.path.getsize(f"./jsonData/{filename}") <= 2:
            movies_name_space.abort(400, status="File doesn't exist or it is empty", statusCode="400")
        with open(f"./jsonData/{filename}", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

@movies_name_space.route("/<string:filename>/<string:path>")
class ListJsonByPath(Resource):
    @app.doc(responses={200: 'OK'}, description="Views section of json file based on the give identifiers path. Seperate identifiers with comma")
    def get(self, filename, path):
        if not os.path.exists(f"./jsonData/{filename}"):
            movies_name_space.abort(400, status="File doesn't exist or it is empty", statusCode="400")
        with open(f"./jsonData/{filename}", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        s = path.split(',')
        current = data
        for identifier in s:
            if identifier in current:
                current = current[identifier]
            else:
                return current
        return current

@movies_name_space.route("/<string:filename>/replace")
class AddToJson(Resource):
    @app.doc(responses={200: 'OK'}, description="Creates new json file or replaces en existing json file with the new one that arrived in the post request message.")
    def put(self, filename):
        if not os.path.exists(f"./jsonData/"):
            os.makedirs(f"./jsonData/")
        if not os.path.exists(f"./jsonData/{filename}"):
            ret = "Successfully created  new json file"
            # movies_name_space.abort(400, status="File doesn't exist", statusCode="400")
        else:
            ret = "Successfully replaced existing json file with the new one"
        return ret


flask_app.run()
