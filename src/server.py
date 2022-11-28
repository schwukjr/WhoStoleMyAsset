from flask import Flask, render_template, request
import sqlite3
import datetime


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/newproject", methods=['POST'])
def newProject():
    projectName = request.args.get('projectname', '')
    updateNightly = request.args.get('updatenightly', '')
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (projectName, updateNightly)
        cursor.execute('INSERT INTO Projects VALUES (NULL, ?, ?)', params)
    return '', 200

@app.route("/newconfig", methods=['POST'])
def newconfig():
    configName = request.args.get('configname', '')
    projectName = request.args.get('projectname', '')
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (configName, projectName)
        cursor.execute('INSERT INTO Configurations VALUES (NULL, ?, (SELECT ProjectID FROM Projects WHERE ProjectName = ?))', params)
    return '', 200

@app.route("/newasset", methods=['POST']) #TODO: Add check to ensure no duplicates are allowed in single config.
def newasset():
    seconds_since_epoch = datetime.datetime.now().timestamp()
    assetName = request.args.get('assetname', '')
    configName = request.args.get('configname', '')
    projectName = request.args.get('projectname', '')
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (assetName, configName, projectName, seconds_since_epoch)
        cursor.execute('INSERT INTO Assets VALUES (NULL, ?, (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)), 0, NULL, ?)', params)
    return '', 200

@app.route("/takeorreturnasset", methods=['POST'])
def takeorreturnasset():
    assetName = request.args.get('assetname', '')
    configName = request.args.get('configname', '')
    projectName = request.args.get('projectname', '')
    takenBy = request.args.get('takenby', '')
    
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (assetName, configName, projectName)
        cursor.execute('SELECT Taken FROM Assets WHERE (assetName = ? AND configID = (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)))', params)
        rows = cursor.fetchall()

        seconds_since_epoch = datetime.datetime.now().timestamp()
        for row in rows:
            if row[0] == 0:
                params = (1, takenBy, seconds_since_epoch, assetName, configName, projectName)   
            else:
                params = (0, 'NULL', seconds_since_epoch, assetName, configName, projectName)   

        cursor.execute('UPDATE Assets SET Taken = ?, TakenBy = ?, LastUpdated = ? WHERE (assetName = ? AND configID = (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)))', params)


    return '', 200

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection