from flask import Flask, render_template, request
import sqlite3
import datetime
import time


app = Flask(__name__)


@app.route("/")
def index():
    html = render_template('index.html')
    html += renderProjectSelect()
    html += render_template('footer.html')
    return html

def renderProjectSelect():
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Projects')
        projects = cursor.fetchall()

        html = f"""<form action="/getprojectdashboard" method="get" style="margin: 20px;">
                        <label for="projectName">Project:</label>
                        <select name="projectName" id="projectName" style="text-transform:uppercase">"""
        for project in projects:
            ProjectName = project[1]
            html += f"""<option value="{ProjectName}">{ProjectName}</option>"""
        html += f"</select>"
        html += f"""<input type="submit" value="Submit" style="margin: 10px;"/>"""
        html += f"</form>"
    return html

def renderConfigButton(projectName):
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (projectName,)
        cursor.execute('SELECT * FROM Projects WHERE ProjectName = ?', params)
        projects = cursor.fetchall()
        
        
        
        for project in projects:
            ProjectName = project[1]

            html = f"""
            <div id="newConfigForm" class="modal fade">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title">Add Config</h1>
                    </div>
                    <div class="modal-body">
                        <form role="form" method="POST" action="/newconfig">
                        <div class="form-group">
                            <label class="control-label">Config Name</label>
                            <div>
                            <input type="text" class="form-control input-lg" name="configName" value="" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="control-label">Project Name</label>
                            <div>
                            <input type="text" class="form-control input-lg" name="projectName" value="{ProjectName}" />
                            </div>
                        </div>
                        <div class="form-group">
                            <div>
                            <button type="submit" class="btn btn-success">Submit</button>
                            </div>
                        </div>
                        </form>
                    </div>
                    </div>
                </div>
            </div>

            <button type="button" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#newConfigForm">Add Config</button><p/>"""
    return html

def renderLoginButton(loginButtonCount, configName, projectName):
    html = f"""
        <div id="newLoginForm{loginButtonCount}" class="modal fade">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title">Add Login</h1>
                </div>
                <div class="modal-body">
                    <form role="form" method="POST" action="/newlogin">
                    <div class="form-group">
                        <label class="control-label">Login Name</label>
                        <div>
                        <input type="text" class="form-control input-lg" name="loginName" value="" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="control-label">Config Name</label>
                        <div>
                        <input type="text" class="form-control input-lg" name="configName" value="{configName}" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="control-label">Project Name</label>
                        <div>
                        <input type="text" class="form-control input-lg" name="projectName" value="{projectName}" />
                        </div>
                    </div>
                    <div class="form-group">
                        <div>
                        <button type="submit" class="btn btn-success">Submit</button>
                        </div>
                    </div>
                    </form>
                </div>
                </div>
            </div>
        </div>

        <button type="button" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#newLoginForm{loginButtonCount}">Add Login</button>"""
    return html

def renderContent(projectName):
    connection = create_connection('db.sqlite')
    with connection:
        cursor = connection.cursor()
        params = (projectName,)
        cursor.execute('SELECT * FROM Projects WHERE ProjectName = ?', params)
        projects = cursor.fetchall()
        
        i = 0
        for project in projects:
                ProjectID = project[0]
                ProjectName = project[1]
                html = f"<h2 style=\"text-transform:uppercase\">Project: {ProjectName}<h2>"
                html += renderConfigButton(projectName)

                params = (ProjectID,)
                cursor.execute(
                    'SELECT * FROM Configurations WHERE ProjectID = ?', params)
                configs = cursor.fetchall()
                for config in configs:
                    ConfigID = config[0]
                    ConfigName = config[1]
                    html += f"<h3 style=\"text-transform:capitalize\">Config: {ConfigName}</h3>"
                    print(ConfigName)
                    html += renderLoginButton(i, ConfigName, ProjectName)
                    i += 1

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
                        else:
                            colour = "solid green"

                        TakenBy = asset[4]
                        LastUpdated = asset[5]
                        lastUpdatedFormatted = time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.localtime(LastUpdated))

                        html += f"""
                        <div id="newProjectForm{AssetName}{ConfigName}{ProjectName}" class="modal fade">
                            <div class="modal-dialog" role="document">
                                <div class="modal-content">
                                <div class="modal-header">
                                    <h1 class="modal-title">Add Project</h1>
                                </div>
                                <div class="modal-body">
                                    <form role="form" method="POST" action="/takeorreturnasset">
                                    <input type="text" name= "assetname" value="{AssetName}" hidden/>
                                    <input type="text" name= "configname" value="{ConfigName}" hidden/>
                                    <input type="text" name= "projectname" value="{ProjectName}" hidden/>
                                    <div class="form-group">
                                        <label class="control-label">Taken By:</label>
                                        <div>
                                            <input type="text" class="form-control input-lg" name="takenby" value="" />
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div>
                                            <button type="submit" class="btn btn-success">Confirm</button>
                                        </div>
                                    </div>
                                    </form>
                                </div>
                                </div>
                            </div>
                        </div>"""

                        html += f"""
                        <div class="card text-center">
                            <div class="card-header"><h3>{AssetName}</h3></div>
                            <div class="card-body">
                                <div class="card-text">
                                    Checked Out? {TakenBool}<br/>"""
                        if(TakenBool):
                            html += f"""Checked out by: {TakenBy}<br/>"""
                        else: html += "<br/>"
                        html += f"""Last Updated: {lastUpdatedFormatted}<br/>
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="text-center">"""
                        if (TakenBool == False):
                            html += f"""
                                    <button type="button" style="padding: 10px; border: 2px {colour}; text-align: center" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#newProjectForm{AssetName}{ConfigName}{ProjectName}">Check Out</button>"""
                        else:
                            html += f"""
                                    <form action="/takeorreturnasset" method="post">
                                        <input type="text" name= "assetname" value="{AssetName}" hidden/>
                                        <input type="text" name= "configname" value="{ConfigName}" hidden/>
                                        <input type="text" name= "projectname" value="{ProjectName}" hidden/>
                                        <input type="text" name= "takenby" value="null" hidden/>
                                        <input type="submit" class="btn btn-secondary btn-lg" style="padding: 10px; border: 2px {colour}; text-align: center" value="Check In" />
                                    </form> """     
                        html += f"""</div>
                            </div>
                        </div>
                        """
                    html += "</div>"
    return html

@app.route("/getprojectdashboard", methods=['GET'])
def getProject(projectNameParam=""):
    if(projectNameParam == ""):
        projectName = request.args.get('projectName', '')
    else:
        projectName = projectNameParam

    html = render_template('dashboard.html')
    html += renderProjectSelect()
    html += renderContent(projectName)
    html += render_template('footer.html')
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
