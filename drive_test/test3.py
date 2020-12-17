from flask import Flask, redirect, render_template
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)
service = None
creds = None
tree = None

def createServiceFromCreds():
    global service
    global creds
    service = build('drive', 'v3', credentials=creds)

def checkForExistingCredentials():
    global creds
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

def validCredsExist():
    global creds
    checkForExistingCredentials()
    if not creds or not creds.valid:
        return False
    return True

@app.route('/')
def index():
    loggedIn = validCredsExist()
    if loggedIn:
        createServiceFromCreds()
        page_token = None
        files = []
        while True:
            response = service.files().list(q="'root' in parents and trashed=false",
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name, mimeType, webViewLink)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                files.append(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return render_template("homepage.html", loggedIn=loggedIn, files=files)
    return render_template("homepage.html", loggedIn=loggedIn)

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
    return redirect('/')

if __name__ == '__main__':
    app.run()