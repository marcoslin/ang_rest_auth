#!/usr/bin/env python

'''
Created on 13 Mar 2013

@author: Marcos Lin

JSON Server
'''

import sys, os, json
from flask import Flask, redirect, request, Response, send_from_directory

from restauth import Authenticator
from auth.base import UnauthorizedError

# Configure Static File Server for HTML
script_path=os.path.dirname(os.path.abspath(__file__))
http_root = os.path.join(script_path, "../www")
# print "* HTTP ROOT: %s" % http_root
app = Flask(__name__, static_folder=http_root, static_url_path="/app")

auth = Authenticator(app.logger)

# ========================================
# Static Server: Angular App
@app.route("/")
def index():
    return redirect("/app/")

@app.route("/app/")
def app_index():
    return send_from_directory(http_root, "index.html")

# ========================================
# Authorization
@app.route("/auth/")
def auth_index():
    return "<!DOCTYPE html><H1>This is the AUTH</H1>"

@app.route("/auth/login", methods=['POST'])
def auth_login():
    return auth.login(request.json)

@app.route("/auth/logout", methods=['GET'])
def auth_logout():
    return auth.logout()

# ========================================
# OAuth
@app.route("/auth/oauth_reply/")
@app.route("/auth/oauth_reply/<string:tpid>")
def oauth_authorize_reply(tpid=None):
    app.logger.debug("query_string : %s [%s]" % (request.args,request.method) )
    app.logger.debug("tpid: %s" % tpid )
        
    try:
        return auth.oauth_process_authorized(tpid, request)
    except UnauthorizedError:
        return "Unauthorized", 401

@app.route("/auth/oauth/<string:provider>", methods=['GET'])
def oauth_authorize_url(provider):
    authorize_url = auth.oauth_authorize_url(provider, request)
    return redirect( authorize_url )
    #return authorize_url

@app.route("/show-headers", methods=['GET'])
def test_show_header():
    res = [ '<html><head><title>HTTP Header</title></head><body><table border="1"><tr>' ]

    tbl = []
    for key, val in request.headers.iteritems():
        tbl.append("<th>%s</th><td>%s</td>" % ( key, val ))
        
    res.append('</tr><tr>'.join(tbl))
    res.append('</tr></table></body></html>')
    return '\n'.join(res)

# ========================================
# Protected Data Services

# Mock some data
contact_names = [
    { "_id": 1, "first_name": "Carla", "last_name": "Musselwhite" },
    { "_id": 2, "first_name": "Jona", "last_name": "Dino" },
    { "_id": 3, "first_name": "Shala", "last_name": "Schwartz" },
    { "_id": 4, "first_name": "Susie", "last_name": "Boman" }
]

@app.route("/json/headers", methods=['GET'])
def json_headers():
    headers = []
    for key, val in request.headers.iteritems():
        headers.append({ "name": key, "content": val })
    return Response(json.dumps(headers),mimetype="application/json")
        
@app.route("/json/name", methods=['GET'])
@auth.require_auth
def json_name_all():
    return Response(json.dumps(contact_names),mimetype="application/json")

@app.route("/json/name/<int:id>", methods=['GET'])
@auth.require_auth
def json_name(id):
    for name in contact_names:
        if name["_id"] == id:
            return Response(json.dumps(name),mimetype="application/json")
    else:
        return "NOT FOUND.", 404
    
    

# ========================================
# Start the server
if __name__ == "__main__":
    http_port=8056
    app.run( port=http_port, debug=True, use_reloader=True )
