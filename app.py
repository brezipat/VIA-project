from flask import Flask, redirect, render_template, request, jsonify
from googleapiclient.discovery import build
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import tree as t

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
    return render_template("homepage.html", loggedIn=loggedIn)


# function () {
#     document.getElementById("coordinate_search_text").value = "Random";
#     document.getElementById('place_marker_text').value = "Random";
# }

# <label onclick='document.getElementById("coordinate_search_text").value = "50°29&apos;24.882\"N, 15°8&apos;12.353\"E"; document.getElementById("place_marker_text").value = "50°29&apos;24.882\"N, 15°8&apos;12.353\"E"'>Libošovice, Podkost, hrad Kost, Libošovice, Česko, (50°29'24.882"N, 15°8'12.353"E)</label><br/>

@app.route('/placeSearch', methods=['POST'])
def placeSearch():
    data = request.get_json()
    resp_dic = {}
    for entry in data:
        d = data[entry]
        d['coords'] = d['coords'].replace("'", "&apos;")
        d['coords'] = d['coords'].replace('"', f'\\"')
        print(d)
        new_label = '<label onclick=\'' \
                    'document.getElementById("coordinate_search_text").value = "%s";' \
                    'document.getElementById("place_marker_text").value = "%s"' \
                    '\'>%s, (%s)</label><br/>' % (d['coords'], d['coords'], d['label'], d['coords'])
        resp_dic[d['id']] = new_label
    # resp_dic = {'html': '<label onclick="addNewElement()">I am new paragraph</label>'}
    resp = jsonify(resp_dic)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/map', methods=['POST', 'GET'])
def map():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        loggedIn = validCredsExist()
        return render_template("map.html", loggedIn=loggedIn)
    if request.method == 'GET':
        loggedIn = validCredsExist()
        return render_template("map.html", loggedIn=loggedIn)


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
    return render_template("fileSystem.html", loggedIn=True, current=data[0], parent=data[1], children=data[2])


app.run(debug=True)
