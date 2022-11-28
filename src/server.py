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

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection