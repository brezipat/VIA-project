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
from apiclient import discovery
import httplib2
from oauth2client import client

app = Flask(__name__)

users_tools = {}
# service = None
# creds = None
# tree = None
# user = None


# def checkForExistingCredentials(user):
#     global users_tools
#     # global creds
#     # global user
#     # if os.path.exists('token.pickle') and os.path.exists('user.pickle'):
#     users_tools[user] = {"creds:": None, "service": None, "tree": None}
#     if os.path.exists(f'token_{user}.pickle'):
#         with open(f'token_{user}.pickle', 'rb') as token:
#             # users_tools[user] = {"creds": None, "service": None, "tree": None}
#             users_tools[user]["creds"] = pickle.load(token)
#             users_tools[user]["service"] = createServiceFromCreds(users_tools[user]["creds"])
#             users_tools[user]["tree"] = None
#         return True
#     return False
#             # creds = pickle.load(token)
#         # with open('user.pickle', 'rb') as user_file:
#         #     user = pickle.load(user_file)


# def validCredsExist(user):
#     # global creds
#     global users_tools
#     if not checkForExistingCredentials(user):
#         return False
#     # if not creds:
#     # if not creds or not creds.valid:
#     # if not creds or creds.expired:
#     # if not creds:
#     if not users_tools[user]["creds"]:
#         # if creds and creds.expired and creds.refresh_token:
#         #     creds.refresh(Request())
#         # else:
#         return False
#     return True


def createServiceFromCreds(creds):
    # global service
    # global creds
    service = build('drive', 'v3', credentials=creds)
    return service


def findFiles(user, path):
    global users_tools
    # global service
    # global tree
    # service = users_tools[user]["service"]
    tree = users_tools[user]["tree"]
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


# @app.route('/login')
# def authorize():
#     global creds
#     flow = InstalledAppFlow.from_client_secrets_file(
#         'credentials_old.json', 'https://www.googleapis.com/auth/drive')
#     creds = flow.run_local_server(port=0)
#     with open('token.pickle', 'wb') as token:
#         pickle.dump(creds, token)
#     createServiceFromCreds()
#     return redirect('/')

@app.route('/authCallback')
def callback():
    print("accessed callback")
    return "called"


@app.route('/storeauthcode', methods=['POST'])
def storeauthcode():
    global users_tools
    # global creds
    CLIENT_SECRET_FILE = 'client_secret.json'
    auth_code = request.data
    creds = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive', 'profile', 'email'],
        auth_code)
    user = creds.id_token['sub']
    with open(f'token_{user}.pickle', 'wb') as token:
        pickle.dump(creds, token)
    service = createServiceFromCreds(creds)
    users_tools[user] = {"creds": creds, "service": service, "tree": None}
    print('_______________________________________________________________________________________________________________')
    print(users_tools)
    # user = creds.id_token['email'].split("@")[0]
    # with open('user.pickle', 'wb') as user_file:
    #     pickle.dump(user, user_file)
    # email = creds.id_token['email']
    # print(email)
    # print(userid)
    return user


@app.route('/logout/<user>')
def logout(user):
    global users_tools
    print(
        '_______________________________________________________________________________________________________________')
    print(users_tools)
    # global creds
    # global service
    # global tree
    # global user
    # creds = None
    # service = None
    # tree = None
    # user = None
    del users_tools[user]
    os.remove(f'token_{user}.pickle')
    # os.remove('user.pickle')
    return redirect('/')


@app.route('/')
@app.route('/<user>')
def index(user=''):
    # loggedIn = False
    if user:
        # if not validCredsExist(user):
        #     return redirect('/')
        return render_template("homepage.html", loggedIn=True, user=user)
    return render_template("homepage.html", loggedIn=False, user=user)

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
        return "Given file doesn't exist or is empty, select one of these:<br/> " + constructListOutput(getJsonFiles()), 400
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
    ret = requests.put(f'http://localhost:5000/Json/{filename}/replace', json=data)
    # ret = requests.put(f'https://brezipat-via-app.herokuapp.com/Json/{filename}/replace', json=data)
    return ret.text


@app.route('/placeSearch', methods=['POST'])
def placeSearch():
    data = request.get_json()
    resp_dic = {}
    for entry in data:
        d = data[entry]
        d['coords'] = d['coords'].replace("'", "&apos;")
        d['coords'] = d['coords'].replace('"', f'\\"')
        new_label = '<label onclick=\'' \
                    'document.getElementById("coordinate_search_text").value = "%s";' \
                    'document.getElementById("place_marker_coords").value = "%s"' \
                    '\'>%s, (%s)</label><br/>' % (d['coords'], d['coords'], d['label'], d['coords'])
        resp_dic[d['id']] = new_label
    resp = jsonify(resp_dic)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/processMarkers/<user>', methods=['POST'])
def processMarkers(user=''):
    data = request.get_json()
    filename = f"{user}_markers.json"
    updateJson(filename, data)
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
    return resp

@app.route('/map')
@app.route('/map/<user>')
def map(user=''):
    global users_tools
    # global user
    # if loggedIn:
    print(
        '_______________________________________________________________________________________________________________')
    print(users_tools)
    if user:
        # if not validCredsExist(user):
        #     return redirect('/map')
        filename = f"{user}_markers.json"
        resp = requests.get(f'http://localhost:5000/Json/{filename}')
        # resp = requests.get(f'https://brezipat-via-app.herokuapp.com/Json/{filename}')
        if resp.status_code != 400:
            data = resp.json()
            return render_template("map.html", loggedIn=True, markersData=data, user=user)
        return render_template("map.html", loggedIn=True, markersData=None, user=user)
    return render_template("map.html", loggedIn=False, markersData=None, user=user)


@app.route('/fileSystemRefresher/<user>')
def refresher(user=''):
    global users_tools
    # global tree
    # tree = None
    users_tools[user]["tree"] = None
    return redirect(f'/fileSystem/{user}/root')

@app.route('/fileSystem')
@app.route('/fileSystem/<user>')
@app.route('/fileSystem/<user>/<path>')
def fileSystem(user='', path=''):
    global users_tools
    # global service
    # global tree
    # global user
    # if not service or not user:
    print(
        '_______________________________________________________________________________________________________________')
    print(users_tools)
    if not user:
        # if not validCredsExist() or not user:
        #     service = None
        #     tree = None
        return render_template("fileSystem.html", loggedIn=False)
        # createServiceFromCreds()
    # if not validCredsExist(user):
    #     return redirect('fileSystem/')
    if not users_tools[user]["tree"]:
        # tree = init_tree(service)
        users_tools[user]["tree"] = init_tree(users_tools[user]["service"])
    data = findFiles(user, path)
    filename = f"{user}_markers.json"
    resp = requests.get(f'http://localhost:5000/Json/{filename}')
    # resp = requests.get(f'https://brezipat-via-app.herokuapp.com/Json/{filename}')
    if resp.status_code != 400:
        markersData = resp.json()
        return render_template("fileSystem.html", loggedIn=True, current=data[0], parent=data[1], children=data[2], markersData=markersData, user=user)
    return render_template("fileSystem.html", loggedIn=True, current=data[0], parent=data[1], children=data[2], markersData=None, user=user)


if __name__ == "__main__":
    app.run(debug=True)
    # print(os.getcwd())
