from flask import Flask, redirect, render_template
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

@app.route('/map')
def map():
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