# The script running on a third-party server. Ideal for small, entire games.

import flask
import json
import os
import secrets
import time

master_token = "CHANGE_ME"
token_lifetime = (60 * 10) # in seconds. 10 minutes

# IF YOU ARE HAVING TROUBLE RELOADING THIS SITE, THAT MEANS IT'S STILL BEING
# USED BY A ROBLOX SERVER OR PYTHON SCRIPT WHILE TRYING TO RELOAD.

app = flask.Flask(__name__)
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

auth_keys = os.path.join(THIS_FOLDER, 'auth_keys.json')
allowedAuths = json.loads(open(auth_keys,"r").read())

poses = {} # key: "username" value: "dictionary containing pose data"
temp_keys = [] # list of temporary keys {value: "", expiry: ""}

def remove_old_keys():
    for i,token in enumerate(temp_keys):
        if time.time() > token["expiry"]:
            temp_keys.pop(i)

@app.route('/download_poses/', methods = ['GET']) # download all poses for all players
def download_poses():
    headers = {}
    status = 200
    data = json.dumps(poses)

    resp = flask.Response(status=status,headers=headers)
    resp.data = data
    return resp

@app.route('/download_pose/<string:username>', methods = ['GET'])
def download_pose(username): # download pose for only a single player
    status = 404
    headers = {}
    data = 'Username not found. Come back later.'

    if username in poses:
        status = 200
        data = json.dumps(poses[username])
    else:
        print(username)
        print(poses)

    resp = flask.Response(status=status,headers=headers)
    resp.data = data
    return resp

@app.route('/upload_pose/<string:username>', methods = ['POST'])
def upload_pose(username):
    pose = flask.request.json
    given_headers = flask.request.headers
    status_code = 400
    response_data = ""

    remove_old_keys()

    if pose is None:
        status_code = 400
        response_data = 'No json.'
    elif 'authorization' in given_headers:
        status_code = 401 # default status before finding token
        response_data = "Invalid temporary token (expired, server restarted, or not yours)."

        for token in temp_keys: # overrides the 401 status
            if token["value"] == given_headers["authorization"] and username == token["username"]: # same person that requested token
                    poses[username] = pose
                    status_code = 200
                    response_data = "Updated user's pose."
                    break
    else:
        status_code = 403
        response_data = "No temporary token given."

    resp = flask.Response(status=status_code)
    resp.data = response_data
    return resp

@app.route('/get_temp_keys/<string:username>', methods = ['GET']) # all poses
def get_temporary_keys(username):
    given_headers = flask.request.headers
    status_code = 400

    if "authorization" in given_headers: # if authorization header exists
        if given_headers["authorization"] == master_token: # if this is the master token
            key = secrets.token_urlsafe(8) # generate random token
            status_code = 200 # set status code
            key_table = {
                "value":  key,
                "expiry": round(time.time() + token_lifetime),
                "username": username,
            }
            temp_keys.append(key_table)
            data = json.dumps(key_table) # turn data into json string
        else:
            status_code = 401
            data = "Incorrect master token."
    else:
        status_code = 403
        data = "No master token given."

    resp = flask.Response(status=status_code)
    resp.data = data
    return resp

if __name__ == '__main__': 
    from waitress import serve
    print("Production server is ready - connections are now being accepted. (Press CTRL+C to quit)")
    serve(app, host="0.0.0.0", port=3000)
