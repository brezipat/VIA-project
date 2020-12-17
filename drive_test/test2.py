from flask import Flask, redirect
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

app = Flask(__name__)

drive = None

@app.route('/login')
def login():
    global drive
    gauth = GoogleAuth()
    # gauth.CommandLineAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return redirect('/')

# View all folders and file in your Google Drive
@app.route('/')
def index():
    global drive
    if drive:
        fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
          print('Title: %s, ID: %s' % (file['title'], file['id']))
          # Get the folder ID that you want
          if(file['title'] == "To Share"):
              fileID = file['id']
        return str(fileList)
    else:
        return '<a href="/login"><button>Login</button></a>'

@app.route('/makeFile')
def makeFile():
    file1 = drive.CreateFile({"mimeType": "text/csv", "parents": [{"kind": "drive#fileLink", "id": fileID}]})
    file1.SetContentFile("small_file.csv")
    file1.Upload() # Upload the file.
    print('Created file %s with mimeType %s' % (file1['title'], file1['mimeType']))

if __name__ == '__main__':
    app.run()
