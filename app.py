from flask import Flask, redirect, render_template, request, jsonify, url_for
import requests
from googleapiclient.discovery import build
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
import tree as t
import os
from os import listdir
from os.path import isfile, join
import json

app = Flask(__name__)

service = None
creds = None
tree = None


def checkForExistingCredentials():
    global creds
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)


def validCredsExist():
    global creds
    checkForExistingCredentials()
    if not creds or not creds.valid:
        # if creds and creds.expired and creds.refresh_token:
        #     creds.refresh(Request())
        # else:
        return False
    return True


def createServiceFromCreds():
    global service
    global creds
    service = build('drive', 'v3', credentials=creds)


def findFiles(path):
    global service
    global tree
    s = path.split(',')
    current = tree.getRoot()
    for i in range(len(s)):
        child = s[i]
        if child == '':
            break
        if child == "root":
            continue
        current = tree.moveToChild(current, child)
    ret = (current, current.getParent(), [])
    for i in range(len(current.children)):
        child = current.children[i]
        ret[2].append(child)
    return ret


def init_tree(service):
    tree = t.Tree(service)
    tree.expandTree(tree.getRoot())
    return tree


@app.route('/login')
def authorize():
    global creds
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 'https://www.googleapis.com/auth/drive')
    creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    createServiceFromCreds()
    return redirect('/')


@app.route('/logout')
def logout():
    global creds
    global service
    global tree
    creds = None
    service = None
    tree = None
    os.remove('token.pickle')
    # for key in list(session.keys()):
    #     session.pop(key)
    return redirect('/')


@app.route('/')
def index():
    loggedIn = validCredsExist()
    # dictToSend = {'question': 'what is the answer?'}
    # test = requests.put('http://127.0.0.1:5000/Json/markers.json/replace', json=dictToSend)
    # print(test.content)
    return render_template("homepage.html", loggedIn=loggedIn)

def getJsonFiles():
    data_files = [f for f in listdir('./jsonData/') if isfile(join('./jsonData/', f))]
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


@app.route('/Json')
def jsons():
    return constructListOutput(getJsonFiles())


@app.route('/Json/<string:filename>')
@app.route('/Json/<string:filename>/<path>')
def viewFile(filename='', path=''):
    if not os.path.exists(f"./jsonData/{filename}") or os.path.getsize(f"./jsonData/{filename}") <= 2:
        return "Given file doesn't exist or is empty, select one of these:<br/> " + constructListOutput(getJsonFiles())
        # return "Given file doesn't exist, select on of these:<br/> " + constructListOutput(getJsonFiles())
    s = path.split(',')
    with open(f"./jsonData/{filename}", 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    current = data
    for identifier in s:
        if identifier in current:
            current = current[identifier]
        else:
            return current
    return current


@app.route("/Json/<string:filename>/replace", methods=['PUT'])
def replaceJsonFile(filename):
    data = request.get_json()
    # print(data)
    if not os.path.exists(f"./jsonData/"):
        os.makedirs(f"./jsonData/")
    if not os.path.exists(f"./jsonData/{filename}"):
        ret = "Successfully created  new json file"
    else:
        ret = "Successfully replaced existing json file with the new one"
    with open(f"./jsonData/{filename}", 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)
    return ret


def updateJson(filename, new_json):
    data = new_json
    ret = requests.put(f'http://127.0.0.1:5000/Json/{filename}/replace', json=data)
    # print(ret.text)
    return ret.text
    # if not os.path.exists(f"./jsonData/{filename}"):
    #     os.makedirs(f"./jsonData/{filename}")
    # with open(f"./jsonData/{filename}", 'w', encoding='utf-8') as json_file:
    #     json.dump(new_json, json_file)


@app.route('/placeSearch', methods=['POST'])
def placeSearch():
    data = request.get_json()
    resp_dic = {}
    for entry in data:
        d = data[entry]
        d['coords'] = d['coords'].replace("'", "&apos;")
        d['coords'] = d['coords'].replace('"', f'\\"')
        # print(d)
        new_label = '<label onclick=\'' \
                    'document.getElementById("coordinate_search_text").value = "%s";' \
                    'document.getElementById("place_marker_coords").value = "%s"' \
                    '\'>%s, (%s)</label><br/>' % (d['coords'], d['coords'], d['label'], d['coords'])
        resp_dic[d['id']] = new_label
    # resp_dic = {'html': '<label onclick="addNewElement()">I am new paragraph</label>'}
    resp = jsonify(resp_dic)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/processMarkers', methods=['POST'])
def processMarkers():
    data = request.get_json()
    filename = "markers.json"
    updateJson(filename, data)
    # print(data)
    table = "<table>" \
            "<tr>" \
                "<th width='120'>Marker Name</th>" \
                "<th width='250'>Marker Coordinates</th>" \
                "<th width='800'>Marker Information</th>" \
                "<th width='200'>Marker Links</th>" \
            "</tr>"
    for key in data:
        table += "<tr>"
        marker_data = data[key]
        ident = marker_data["id"]
        coords = marker_data["coords"]
        info = marker_data["info"]
        links = ""
        for placeholder in marker_data["links"]:
            link = marker_data["links"][placeholder]
            links += '  ' + link
        table += f"<td>{ident}</td><td>{coords}</td><td>{info}</td><td>{links}</td>"
        table += "</tr>"
    table += "</table>"
    resp_dict = {'table': table}
    resp = jsonify(resp_dict)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    # print(table)
    return resp

@app.route('/map')
def map():
    # data = {}
    loggedIn = validCredsExist()
    data = requests.get('http://127.0.0.1:5000/Json/markers.json').json()
    # print(data)
    # if os.path.exists(f"./jsonData/markers.json"):
    #     if os.path.getsize(f"./jsonData/markers.json") > 2:
    #         with open(f"./jsonData/markers.json", 'r', encoding='utf-8') as json_file:
    #             data = json.load(json_file)
    return render_template("map.html", loggedIn=loggedIn, markersData=data)


@app.route('/fileSystemRefresher')
def refresher():
    global tree
    tree = None
    return redirect('/fileSystem/root')


@app.route('/fileSystem')
@app.route('/fileSystem/<path>')
def fileSystem(path=''):
    global service
    global tree
    if not service:
        if not validCredsExist():
            service = None
            tree = None
            return render_template("fileSystem.html", loggedIn=False)
        createServiceFromCreds()
    if not tree:
        tree = init_tree(service)
    data = findFiles(path)
    markersData = requests.get('http://127.0.0.1:5000/Json/markers.json').json()
    # markersData = {}
    # if os.path.exists(f"./jsonData/markers.json"):
    #     if os.path.getsize(f"./jsonData/markers.json") > 2:
    #         with open(f"./jsonData/markers.json", 'r', encoding='utf-8') as json_file:
    #             markersData = json.load(json_file)
    return render_template("fileSystem.html", loggedIn=True, current=data[0], parent=data[1], children=data[2], markersData=markersData)


if __name__ == "__main__":
    app.run()
