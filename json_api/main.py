import json
from flask import Flask
import os
from os import listdir
from os.path import isfile, join

app = Flask(__name__)

def getJsonFiles():
    data_files = [f for f in listdir('./') if isfile(join('./', f))]
    ret = []
    for file in data_files:
        if file.split('.')[-1] == 'json':
            ret.append(file)
    return ret


def constructListOutput(ls):
    ret = ""
    for item in ls:
        ret += f'{item}<br/>'
    return ret


@app.route('/')
def jsons():
    return constructListOutput(getJsonFiles())


@app.route('/<string:filename>')
@app.route('/<string:filename>/<path>')
def viewFile(filename='', path=''):
    if not os.path.exists(f"./{filename}"):
        return "Give file doesn't exist, select on of these:<br/> " + constructListOutput(getJsonFiles())
    s = path.split(',')
    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    current = data
    for identifier in s:
        if identifier in current:
            current = current[identifier]
        else:
            return current
    return current


# @app.route('/<string:filename>/update', methods=["POST"])
# def update(filename):
#     if not os.path.exists(f"./{filename}"):
#         return "Give file doesn't exist, select on of these:<br/> " + constructListOutput(getJsonFiles())
#     with open(filename, 'r', encoding='utf-8') as json_file:
#         data = json.load(json_file)



app.run(debug=True)