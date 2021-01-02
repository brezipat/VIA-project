from flask import Flask
from flask import Blueprint
from flask_restplus import Api, Resource, reqparse
import werkzeug
import os
from os import listdir
from os.path import isfile, join
import json

blueprint = Blueprint("api", __name__)

api = Api(blueprint,
          version="1.0",
          title="Json",
          description="App for managing json database.")

api_name_space = api.namespace("Json", description='Work with json files')

text_input = reqparse.RequestParser()
text_input.add_argument('entry', required=True)

file_upload = reqparse.RequestParser()
file_upload.add_argument('file', location='files',
                           type=werkzeug.datastructures.FileStorage, required=True)

@api_name_space.route("/")
class ListJsonFiles(Resource):
    @api.doc(responses={200: 'OK'}, description="List all available json files")
    def get(self):
        data_files = [f for f in listdir('./jsonData') if isfile(join('./jsonData', f))]
        ret = []
        for file in data_files:
            if file.split('.')[-1] == 'json':
                ret.append(file)
        return ret

@api_name_space.route("/<string:filename>")
class ListJson(Resource):
    @api.doc(responses={200: 'OK'}, description="View whole json file")
    def get(self, filename):
        if not os.path.exists(f"./jsonData/{filename}.json") or os.path.getsize(f"./jsonData/{filename}.json") <= 2:
            api_name_space.abort(400, status="File doesn't exist or it is empty", statusCode="400")
        with open(f"./jsonData/{filename}.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

@api_name_space.route("/<string:filename>/<string:path>")
class ListJsonByPath(Resource):
    @api.doc(responses={200: 'OK'}, description="Views section of json file based on the give identifiers path. Seperate identifiers with comma")
    def get(self, filename, path):
        if not os.path.exists(f"./jsonData/{filename}.json"):
            api_name_space.abort(400, status="File doesn't exist", statusCode="400")
        with open(f"./jsonData/{filename}.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        s = path.split(',')
        current = data
        for identifier in s:
            if identifier in current:
                current = current[identifier]
            else:
                return current
        return current

@api_name_space.route("/<string:filename>/<string:path>/add")
class AddEntryToPath(Resource):
    @api.expect(text_input)
    @api.doc(responses={200: 'OK'}, description="Add new entry to the given json file to the given path. If the path doesn't exist it is generated. Existing entry is overwritten.")
    def put(self, filename, path):
        args = text_input.parse_args()
        if not os.path.exists(f"./jsonData/{filename}.json"):
            api_name_space.abort(400, status="File doesn't exist", statusCode="400")
        with open(f"./jsonData/{filename}.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        s = path.split(',')
        entry_key = s[-1]
        del s[-1]
        current = data
        for identifier in s:
            if identifier in current:
                current = current[identifier]
            else:
                current[identifier] = {}
        current[entry_key] = args['entry']
        with open(f"./jsonData/{filename}.json", 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
        return "Success"

@api_name_space.route("/<string:filename>/<string:path>/delete")
class DeleteEntryOnPath(Resource):
    @api.doc(responses={200: 'OK'}, description="Delete existing entry in given json file on the given path")
    def delete(self, filename, path):
        if not os.path.exists(f"./jsonData/{filename}.json"):
            api_name_space.abort(400, status="File doesn't exist", statusCode="400")
        with open(f"./jsonData/{filename}.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        s = path.split(',')
        entry_key = s[-1]
        del s[-1]
        current = data
        for identifier in s:
            if identifier in current:
                current = current[identifier]
            else:
                api_name_space.abort(401, status="Specified path doesn't exist, delete is not executed.", statusCode="401")
        if entry_key in current:
            del current[entry_key]
        else:
            api_name_space.abort(401, status="Specified path doesn't exist, delete is not executed.", statusCode="401")
        with open(f"./jsonData/{filename}.json", 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
        return "Delete successful"

@api_name_space.route("/<string:filename>/upload")
class UploadJson(Resource):
    @api.expect(file_upload)
    @api.doc(responses={200: 'OK'}, description="Creates new json file or replaces en existing json file with the new one that arrived in the post request message.")
    def put(self, filename):
        args = file_upload.parse_args()
        if args['file'].mimetype != 'application/json':
            api_name_space.abort(400, status="Provided file isn't json!!", statusCode="400")
        if not os.path.exists(f"./jsonData/"):
            os.makedirs(f"./jsonData/")
        if not os.path.exists(f"./jsonData/{filename}.json"):
            ret = "Successfully created  new json file"
            # movies_name_space.abort(400, status="File doesn't exist", statusCode="400")
        else:
            ret = "Successfully replaced existing json file with the new one"
        # destination = os.path.join(app.root_path, 'jsonData/')
        file = '%s%s' % (f"./jsonData/", f'{filename}.json')
        args['file'].save(file)
        return ret

app = Flask(__name__)
app.register_blueprint(blueprint)
if __name__ == '__main__':
    app.run()
# app.run()
