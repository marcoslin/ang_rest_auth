'''
Created on 13 May 2013

@author: Marcos Lin

Authenticator
'''

import time, random, hashlib, base64
from functools import wraps
from flask import request, Response, redirect
from auth.providers import AuthProviders

import json

class AuthDB(object):
    AUTH_DB = {}
    hash_salt = "uwd7)pq*2=s*d=+sdf23"
    hash_pepper ="DH!13yw45&984%3fnd23"
    
    TPID_PREFIX = "PID."
    
    def store(self, key, value):
        self.AUTH_DB[key] = value
                
    def retrieve(self, key):
        try:
            return self.AUTH_DB[key]
        except KeyError:
            return None
    def delete(self, key):
        try:
            del self.AUTH_DB[key]
        except KeyError:
            return None
    def key_exists(self,key):
        if key in self.AUTH_DB:
            return True
        else:
            return False

    def _get_tpid_key(self, tpid):
        tpid_key = self.create_key(self.hash_salt + self.create_key(tpid) + self.hash_pepper)
        return self.TPID_PREFIX + tpid_key
    def store_tpid(self, tpid, content):
        # Generate a unique temporary process identified (tpid) and store the content with pid as key. This pid
        # is meant for temporary and short-term storage of data needed for async processing
        tpid_key = self._get_tpid_key(tpid)
        self.store(tpid_key, { "tpid": tpid_key, "content": content })
        return tpid
    def retrieve_and_clear_tpid(self, tpid):
        # Read the content of tpid and delete the entry immediately
        tpid_key = self._get_tpid_key(tpid)
        data = self.retrieve(tpid_key)
        if data is None:
            return None
        else:
            if tpid_key != data["tpid"]:
                raise ValueError("'%s' pass is not a valid TPID." % tpid)
            self.delete(tpid_key)
            return data["content"]
    
    def create_key(self, auth_key):
        vals = (self.hash_salt, auth_key, self.hash_pepper)
        dgst = hashlib.md5(''.join(vals))
        sres = base64.urlsafe_b64encode(dgst.digest())
        return sres.rstrip("=")
        
    def generate_token(self):
        rand = str(random.getrandbits(32))
        vals = (rand, self.hash_salt, str(time.time()), self.hash_pepper, rand)
        dgst = hashlib.md5(''.join(vals)).digest()
        sres = base64.urlsafe_b64encode(dgst)
        return sres.rstrip("=")
        

class Authenticator(object):
    AUTH_KEY = "Authorization"

    def __init__(self, logger):
        self._logger = logger
        self._db = AuthDB()
        self._ap = AuthProviders()

    @property
    def log(self):
        return self._logger

    def _get_auth_key(self, request):
        # Try to get it from header
        res = request.headers.get(self.AUTH_KEY)
        if res:
            self.log.debug("AUTH TOKEN from HEADER")
            return self._db.create_key(res)
        
        res = request.cookies.get(self.AUTH_KEY)
        if res:
            self.log.debug("AUTH TOKEN from COOKIE")
            return self._db.create_key(res)
        
        self.log.debug("AUTH TOKEN not found")
        return None
        

    def is_authenticated(self, request):
        auth_key = self._get_auth_key(request)
        if auth_key and self._db.key_exists(auth_key):
            return True
        else:
            self.log.debug("auth_key '%s' not found." % (auth_key))
            return False

    def auth_header(self, auth_token):
        return {self.AUTH_KEY: auth_token}
    
    def _create_login_response(self, user_info, response = None):
        '''
        Method to register the logged in user in the system.  The user detail should be provided in the user_info dictionary,
        where 'user_id' is a required entry.  'resp_body' allow for customization of Response Object which defaults to json
        verion of user_info.
        
        Raises ValueError if 'user_id' is not provided.
        '''
        user_id = user_info["user_id"]
        if user_id:
            # Create the auth_token made with user name and a random hash
            randon_hash = self._db.generate_token()
            
            # Default user_name to user_id if not set
            try:
                user_name = user_info["user_name"]
            except:
                user_info["user_name"] = user_id
                user_name = user_id
            
            auth_token = "%s:%s" % (user_name, randon_hash)
            
            # Add auth_token to user_info
            user_info["auth_token"] = auth_token
            
            # A hash is then created on auth_token to be used as key
            auth_key = self._db.create_key(auth_token)
            self.log.debug("auth_key '%s' created." % auth_key)
            self._db.store(auth_key, user_info)
            
            # Auth Token is returned in 2 ways:
            # 1. As json to the caller
            # 2. As cookie
            success_json = json.dumps( user_info )
            if response is None:
                resp = Response(success_json)
            else:
                resp = response
            resp.set_cookie(self.AUTH_KEY, auth_token)
            return resp
        else:
            raise ValueError("Create login response failed due to missing 'user_id'")
        
    
    def login(self, json_body):
        # Expect JSON: { user_name: "", password: ""}
        self.log.debug("login json_body: %s" % json_body)
        
        try:
            user = json_body["user_id"]
            passwd = json_body["password"]
        except (TypeError, KeyError):
            return "Access is denied due to invalid credentials.", 401
        
        if user in ("marcos", "lin", "linm") and passwd in ("secret", "angular", "hello"):
            self.log.info("%s logged in with valid credential." % user)
            user_info = { "user_id": user, "user_name": user }
            return self._create_login_response(user_info)
        else:
            return "Access is denied due to invalid credentials.", 401

    def logout(self):
        resp = Response("logout succeeded.")
        resp.set_cookie(self.AUTH_KEY, expires=0)
        return resp

    def unauthorized(self):
        resp = Response("Unauthorized", status=401)
        resp.set_cookie(self.AUTH_KEY, expires=0)
        return resp

    def require_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not self.is_authenticated(request):
                return self.unauthorized()
            return f(*args, **kwargs)
        return decorated
    
    # OAuth Related
    def oauth_authorize_url(self, provider_name, request):
        
        
        # Generate a temporary PID to store the data
        tpid = self._db.generate_token();
        self.log.debug("auth_request: %s [%s]" % (request.url,tpid) )
        
        provider = self._ap.get(provider_name)
        #self._provider = provider
        #self.log.debug("provider: %s, params: %s" % (self.provider, self.provider._serv_params) )        
        authorize_url = provider.authorize_url(tpid)
        
        # Store data for transaction
        redirect_url = request.args.get("redirect_url")
        self.log.debug("auth_request redirect_url: %s" % (redirect_url) )
        data = { "provider": provider.persit_string() }
        if redirect_url:
            data["redirect_url"] = redirect_url
        self._db.store_tpid(tpid, data)

        return authorize_url 
    
    def oauth_process_authorized(self, tpid, request):
        #oauth_verifier = request.args.get("oauth_verifier")
        self.log.debug("auth_reply: %s [%s]" % (request.url,tpid) )
        
        data = self._db.retrieve_and_clear_tpid(tpid)
        provider = self._ap.regenerate(data["provider"])
        #provider = self._provider
        try:
            redirect_url = data["redirect_url"]
        except:
            redirect_url = None
        
        user_info = provider.process_oauth_reply(request.args)
        self.log.debug("user_info: %s" % user_info)
        #return Response(user_info,mimetype="application/json")
        
        if redirect_url:
            # Log user in and redirect to the url previously provided
            self.log.debug("[END AUTH] tpid: %s, source_url: %s" % (tpid, redirect_url))
            response = self._create_login_response(user_info, redirect(redirect_url))
        else:
            # Return JSON representation of user_info
            response = self._create_login_response(user_info)
            
        return response

        
