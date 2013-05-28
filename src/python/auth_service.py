from flask import Blueprint, Response, request
from restauth import Authenticator
from werkzeug.utils import redirect
from auth.base import UnauthorizedError
import logging

blueprint = Blueprint('auth_service', __name__)


auth = Authenticator()

# ========================================
# Authorization
@blueprint.route("/auth/")
def auth_index():
    return "<!DOCTYPE html><H1>This is the AUTH</H1>"

@blueprint.route("/login", methods=['POST'])
def auth_login():
    return auth.login(request.json)

@blueprint.route("/logout", methods=['GET'])
def auth_logout():
    return auth.logout()

# ========================================
# OAuth
@blueprint.route("/oauth_reply/")
@blueprint.route("/oauth_reply/<string:tpid>")
def oauth_authorize_reply(tpid=None):
    logger = logging.getLogger('logger')
    logger.debug("query_string : %s [%s]" % (request.args,request.method) )
    logger.debug("tpid: %s" % tpid )
        
    try:
        return auth.oauth_process_authorized(tpid, request)
    except UnauthorizedError:
        return "Unauthorized", 401

@blueprint.route("/oauth/<string:provider>", methods=['GET'])
def oauth_authorize_url(provider):
    authorize_url = auth.oauth_authorize_url(provider, request)
    return redirect( authorize_url )
    #return authorize_url