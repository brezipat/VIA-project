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
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    return creds

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
    # results = service.files().list(q=f"'root' in parents and trashed=false",
    #                                spaces='drive',
    #                                fields="files(id, name, mimeType)").execute()
    # items = results.get('files', [])
    # if not items:
    #     return f'No files found in {path}.'
    # else:
    #     for item in items:
    #         # out_str += u'{0} ({1})<br/>'.format(item['name'], item['id'])
    #         ret.append((item['name'], item['id'], item['mimeType']))
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
@app.route('/<path>')
def index(path=''):
    global service
    global creds
    global tree
    if not service:
        creds = checkForExistingCredentials()
        if not creds or not creds.valid:
            # if creds and creds.expired and creds.refresh_token:
            #     creds.refresh(Request())
            # else:
            service = None
            creds = None
            tree = None
            return render_template("index.html")
        createServiceFromCreds()
    if not tree:
        tree = init_tree(service)
    data = findFiles(path)
    return render_template("drive.html", current=data[0], parent=data[1], children=data[2])

app.run(debug=True)