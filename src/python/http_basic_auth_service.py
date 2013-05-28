from flask import Blueprint, request, Response
import json, base64
import logging
from restauth import Authenticator

class BasicVerifier():    
    _logger = logging.getLogger('logger')
    AUTH_HEADER = 'Authentication'
    AUTH_REALM = 'AngRestAuth App'
    
    '''Verifier for HTTP Basic Authenticator'''
    def __init__(self):        
        self._logger.debug("Init BasicVerifier.")
        
    def login(self, request):
        json_body = request.json
        try:
            user = json_body["user_id"]
            passwd = json_body["password"]
        except (TypeError, KeyError):
            self.logger.debug("Failed to read user from request.")
            return self.unauthorized()
        
        #if self.db.is_valid_local_user(passwd, user_name=user):
        if user in ("marcos", "lin", "linm") and passwd in ("secret", "angular", "hello"):
            basic_enc = base64.b64encode("%s:%s" % (user, passwd))
            auth_token = "Basic %s" % basic_enc
            user_info = {
                "user_id": user,
                "user_name": user,
                "auth_token": auth_token
            }
    
            resp = Response(json.dumps(user_info))
            resp.set_cookie(self.AUTH_HEADER, auth_token)
            return resp
        else:
            self._logger.debug("Username password not authenticated.")
            return self.unauthorized()
    
    def logout(self):
        resp = Response("logout succeeded.")
        resp.set_cookie(self.AUTH_HEADER, expires=0)
        return resp
    
    
    def is_authenticated(self, request):
        '''Check if user is authenticated'''
        auth = request.authorization
        if auth:
            self._logger.info("request.authorization found.")
            if self.db.is_valid_local_user(auth.password, user_name=auth.username):
                return True
        else:
            self._logger.info("request.authorization NOT FOUND.")
        return False
    
    def authentication_needed(self):
        '''Sends a 401 response that enables basic auth'''
        auth_challenge_header = {'WWW-Authenticate': 'Basic realm="%s"' % self.AUTH_REALM}
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            auth_challenge_header
        )

auth = Authenticator()
blueprint = Blueprint('http_basic_auth', __name__)
verifier = BasicVerifier()
        
@blueprint.route("/")
def index():
    return "<!DOCTYPE html><H1>This is the AUTH</H1>"

@blueprint.route("/login", methods=['POST'])
def login():
    return verifier.login(request)

@blueprint.route("/logout")
def logout():
    return verifier.logout()

@blueprint.route("/authorize")
@auth.require_auth
def authorize():
    return "Authorized"


