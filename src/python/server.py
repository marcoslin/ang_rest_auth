#!/usr/bin/env python

import os
from flask import Flask, redirect, send_from_directory
import auth_service
import util_service
import json_service

#from routes.auth.cust_auth import route_auth
#from routes.auth.http_basic_auth import BasicAuthRoute




# ========================================
# INITIALIZATION

# Define static path
http_root = os.path.abspath( os.path.join(os.path.dirname(__file__), "../www") )
app = Flask(__name__,static_folder=http_root, static_url_path="/app")


# ========================================
# ROUTE SETUP

# Initialzing BasicAuthRoute also prepare the Authenticator Singleton to be used
# by other Blueprints
#auth_route = BasicAuthRoute()


app.register_blueprint(auth_service.blueprint, url_prefix="/auth")
app.register_blueprint(util_service.blueprint, url_prefix="/util")
app.register_blueprint(json_service.blueprint, url_prefix="/json")

# Define Default Routes
@app.route("/")
def index():
    return redirect("/app/")

@app.route("/app")
@app.route("/app/")
def app_index():
    return send_from_directory(http_root, "index.html")



# ========================================
# START SERVER
if __name__ == "__main__":
    app.run(            
            port = 5000,
            use_reloader=False,
            debug = True
            )
    