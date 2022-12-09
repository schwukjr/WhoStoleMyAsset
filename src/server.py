from flask import Flask, render_template, request
import sqlite3
import datetime
import time


app = Flask(__name__)


@app.route("/")
def index():

    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Projects')
        projects = cursor.fetchall()

        html = render_template('index.html')
        html += f"""<form action="/getprojectdashboard" method="get">
                        <label for="projectName">Project:</label>
                        <select name="projectName" id="projectName" style="text-transform:uppercase">"""
        for project in projects:
            ProjectName = project[1]
            html += f"""<option value="{ProjectName}">{ProjectName}</option>"""
        html += f"</select>"
        html += f"""<input type="submit" value="Submit"/>"""
        html += f"</form>"
    return html

@app.route("/getprojectdashboard", methods=['GET'])
def getProject(projectNameParam=""):
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()

        if(projectNameParam == ""):
            projectName = request.args.get('projectName', '')
        else:
            projectName = projectNameParam

        params = (projectName,)
        cursor.execute('SELECT * FROM Projects WHERE ProjectName = ?', params)
        projects = cursor.fetchall()

        html = render_template('dashboard.html')

        for project in projects:
            ProjectID = project[0]
            ProjectName = project[1]
            html += f"<h2 style=\"text-transform:uppercase\">{ProjectName}<h2>"

            params = (ProjectID,)
            cursor.execute(
                'SELECT * FROM Configurations WHERE ProjectID = ?', params)
            configs = cursor.fetchall()
            for config in configs:
                ConfigID = config[0]
                ConfigName = config[1]
                html += f"<h3 style=\"text-transform:capitalize\">{ConfigName}</h3>"

                params = (ConfigID,)
                cursor.execute(
                    'SELECT * FROM Assets WHERE ConfigID = ? ORDER BY Taken DESC, LastUpdated DESC', params)
                assets = cursor.fetchall()
                html += "<div class=\"card-columns\" style=\"margin: 20px\">"
                for asset in assets:
                    AssetID = asset[0]
                    AssetName = asset[1]
                    Taken = asset[3]
                    TakenBool = (Taken == 1)
                    if TakenBool:
                        colour = "solid red"
                        buttonText = "Check In"
                    else:
                        colour = "solid green"
                        buttonText = "Check Out"

                    TakenBy = asset[4]
                    LastUpdated = asset[5]
                    lastUpdatedFormatted = time.strftime(
                        '%Y-%m-%d %H:%M:%S', time.localtime(LastUpdated))

                    html += f"""
                    <div class="card text-center">
                        <div class="card-header"><h3>{AssetName}</h3></div>
                        <div class="card-body">
                            <div class="card-text">
                                Checked Out? {TakenBool}<br/>
                                Checked out by: {TakenBy}<br/>
                                Last Updated: {lastUpdatedFormatted}<br/>
                            </div>
                        </div>
                        <div class="card-footer">
                            <form action="/takeorreturnasset" method="post">
                                <input type="text" name= "assetname" value="{AssetName}" hidden/>
                                <input type="text" name= "configname" value="{ConfigName}" hidden/>
                                <input type="text" name= "projectname" value="{ProjectName}" hidden/>
                                <input type="text" name= "takenby" value="test" hidden/>
                                <input type="submit" style="padding: 10px; border: 2px {colour}; text-align: center" value="{buttonText}" />
                            </form>
                        </div>
                    </div>
                    """
                html += "</div>"
    return html


@app.route("/newproject", methods=['POST'])
def newProject():
    projectName = request.form.get('projectName', '')
    updateNightly = request.form.get('updateNightly', '')
    connection = create_connection('db.sqlite')
    try:
        with connection:
            cursor = connection.cursor()
            params = (projectName, updateNightly)
            cursor.execute('INSERT INTO Projects VALUES (NULL, ?, ?)', params)
        return getProject(projectName), 200
    except:
        return 'That input is not allowed. Please re-load and try again.', 400


@app.route("/newconfig", methods=['POST'])
def newconfig():
    configName = request.form.get('configName', '')
    projectName = request.form.get('projectName', '')
    connection = create_connection('db.sqlite')
    try:
        with connection:
            cursor = connection.cursor()
            params = (configName, projectName)
            cursor.execute(
                'INSERT INTO Configurations VALUES (NULL, ?, (SELECT ProjectID FROM Projects WHERE ProjectName = ?))', params)
        return getProject(projectName), 200
    except:
        return 'That input is not allowed. Please re-load and try again.', 400


# TODO: Add check to ensure no duplicates are allowed in single config.
@app.route("/newlogin", methods=['POST'])
def newasset():
    seconds_since_epoch = datetime.datetime.now().timestamp()
    assetName = request.form.get('loginName', '')
    configName = request.form.get('configName', '')
    projectName = request.form.get('projectName', '')
    connection = create_connection('db.sqlite')
    try:
        with connection:
            cursor = connection.cursor()
            params = (assetName, configName, projectName, seconds_since_epoch)
            cursor.execute('INSERT INTO Assets VALUES (NULL, ?, (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)), 0, NULL, ?)', params)
        return getProject(projectName), 200
    except:
        return 'That input is not allowed. Please re-load and try again.', 400


@app.route("/takeorreturnasset", methods=['POST'])
def takeorreturnasset():
    assetName = request.form.get('assetname', '')
    configName = request.form.get('configname', '')
    projectName = request.form.get('projectname', '')
    takenBy = request.form.get('takenby', '')

    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (assetName, configName, projectName)
        cursor.execute('SELECT Taken FROM Assets WHERE (assetName = ? AND configID = (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)))', params)
        rows = cursor.fetchall()

        seconds_since_epoch = datetime.datetime.now().timestamp()
        for row in rows:
            if row[0] == 0:
                params = (1, takenBy, seconds_since_epoch,
                          assetName, configName, projectName)
            else:
                params = (0, 'NULL', seconds_since_epoch,
                          assetName, configName, projectName)

        cursor.execute('UPDATE Assets SET Taken = ?, TakenBy = ?, LastUpdated = ? WHERE (assetName = ? AND configID = (SELECT ConfigID FROM Configurations WHERE ConfigName = ? AND ProjectID = (SELECT ProjectID FROM Projects WHERE ProjectName = ?)))', params)

    return getProject(projectName), 200


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
