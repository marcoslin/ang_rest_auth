from flask import Blueprint, request, Response
import json
from restauth import Authenticator


blueprint = Blueprint('json_service', __name__)

auth = Authenticator()

# Mock some data
contact_names = [
    { "_id": 1, "first_name": "Carla", "last_name": "Musselwhite" },
    { "_id": 2, "first_name": "Jona", "last_name": "Dino" },
    { "_id": 3, "first_name": "Shala", "last_name": "Schwartz" },
    { "_id": 4, "first_name": "Susie", "last_name": "Boman" }
]

@blueprint.route("/headers", methods=['GET'])
def json_headers():
    headers = []
    for key, val in request.headers.iteritems():
        headers.append({ "name": key, "content": val })
    return Response(json.dumps(headers),mimetype="application/json")
        
@blueprint.route("/name", methods=['GET'])
@auth.require_auth
def json_name_all():
    return Response(json.dumps(contact_names),mimetype="application/json")

@blueprint.route("/name/<int:id>", methods=['GET'])
@auth.require_auth
def json_name(id):
    for name in contact_names:
        if name["_id"] == id:
            return Response(json.dumps(name),mimetype="application/json")
    else:
        return "NOT FOUND.", 404