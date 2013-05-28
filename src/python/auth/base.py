'''
Created on 21 May 2013

@author: Marcos Lin

Base Classes for OAuth Providers
'''

from rauth.service import OAuth1Service, OAuth2Service
import cPickle

# ========================
# Exception Classes
class AuthorizationProviderError(Exception):
    pass

class UnauthorizedError(AuthorizationProviderError):
    pass

# ========================
# Base Class for all Authentication Providers
class BaseProvider(object):
    # Define Required Base Service properties for both OAuth2 and OAuth2
    REQ_SERV_PARAMS = ("name", "access_token_url", "authorize_url", "base_url")
    _serv_params = None
    
    # Define the properties needed by user_info
    REQ_USER_INFO_KEYS = ("user_id", "user_name", "user_fullname")
    _user_info = None
    
    # ToDo: figure out how to remove this hard coding bit
    OAUTH_REPLY_URL_BASE = "http://kindalikeme.com:5000/auth/oauth_reply/"
    _oauth_reply_url = None
    
    '''
    CONSTRUCTOR: capture the needed argument for _serv_params
    '''
    def __init__(self, *args, **kwargs):
        self._populate_service_param(kwargs, BaseProvider.REQ_SERV_PARAMS)

    def _populate_service_param(self, kwargs, req_params):
        '''
        Set the self._serv_params by copying entries as defined in req_params from kwargs into
        self._serv_params, but without replacing if entry already exists.
        
        Raises ValueError if entry needed is not found in kwargs
        '''
        if self._serv_params is None:
            self._serv_params = {}    

        for key in req_params:
            if key not in self._serv_params:
                try:
                    self._serv_params[key] = kwargs[key]
                except KeyError:
                    raise ValueError("'%s' is a required paramenter for '%s'." % (key, self.__class__.__name__))

    '''
    Create read/write user_info property
    '''
    @property
    def user_info(self):
        return self._user_info
    def set_user_info(self, user_id, user_name=None, user_fullname=None):
        '''Set the user_info property where only user_id is required'''
        if user_name is None:
            user_name = user_id
        self._user_info = { "user_id": user_id, "user_name": user_name }
        if user_fullname is not None:
            self._user_info["user_fullname"] = user_fullname

    '''
    Create name property from the service parameter
    '''
    @property
    def name(self):
        '''Return name params from the service'''
        try:
            return self._serv_params["name"]
        except:
            return None

    '''
    Return callback url with tpid
    '''
    @property
    def oauth_reply_url(self):
        return self._oauth_reply_url
    def set_oauth_reply_url(self, tpid):
        self._oauth_reply_url = "%s%s" % (self.OAUTH_REPLY_URL_BASE, tpid)

    '''
    Create a string allowing for reconstruction of the object
    '''
    def persit_string(self):
        return cPickle.dumps(self, protocol=cPickle.HIGHEST_PROTOCOL)

# ========================
# Base Class for OAuth
class OAuth1Provider(BaseProvider):
    # Define required parameters specific to OAuth1
    REQ_SERV_PARAMS = ("consumer_key", "consumer_secret", "request_token_url")

    '''
    CONSTRUCTOR: capture the needed argument for _serv_params so that service can be created
    '''
    def __init__(self, *args, **kwargs):
        # Set the required service param
        super(OAuth1Provider, self).__init__(*args, **kwargs)
        self._populate_service_param(kwargs, OAuth1Provider.REQ_SERV_PARAMS)
    
    def initialize(self):
        '''
        Initialze the service and tokens.  This is kept outside of contructor as instantiation of
        provider should be kept as lightweight as possible.
        '''
        # Initialize the service
        try:
            self.__create_service()
        except Exception as e:
            raise AuthorizationProviderError("Create Service Error: %s" % e)

    '''
    Create and return service
    '''
    _service = None
    def __create_service(self):
        '''Create a OAuth1 Service from the _serv_params populate by constructore'''
        self._service = OAuth1Service(**self._serv_params)
    @property
    def service(self):
        '''Return read-only service'''
        return self._service

    '''
    Create and set tokens
    '''
    _request_token = None
    _request_token_secret = None
    def __create_request_token(self, params=None):
        request_token, request_token_secret = self.service.get_request_token(params=params) 
        self._request_token = request_token
        self._request_token_secret = request_token_secret

    '''
    OAuth1's implmentation of authorize_url and authorized_session
    '''
    _oauth_verifier = None
    def authorize_url(self, tpid):
        '''Generate the authorization_url where the callback should add tpid as parameter'''
        
        # Set the reply URL
        self.set_oauth_reply_url(tpid)
        params = { "oauth_callback": self.oauth_reply_url }
        if self._request_token is None:
            self.__create_request_token(params)
        return self.service.get_authorize_url(self._request_token, **params)
    
    def authorized_session(self, oauth_verifier):
        # Must set self._oauth_verifier before calling this
        if oauth_verifier:
            self._oauth_verifier = oauth_verifier
            return self.service.get_auth_session(
                self._request_token,
                self._request_token_secret,
                method="POST",
                data={ 'oauth_verifier': self._oauth_verifier }
            )
        else:
            raise ValueError("oauth_verifier is required to get a authorized_session")

class OAuth2Provider(BaseProvider):
    # Define required parameters specific to OAuth1
    REQ_SERV_PARAMS = ("client_id", "client_secret")

    # Define property used
    _service = None

    '''
    CONSTRUCTOR: capture the needed argument for _serv_params so that service can be created
    '''
    def __init__(self, *args, **kwargs):
        # Set the required service param
        super(OAuth2Provider, self).__init__(*args, **kwargs)
        self._populate_service_param(kwargs, OAuth2Provider.REQ_SERV_PARAMS)

    def initialize(self):
        '''
        Initialze the service and tokens.  This is kept outside of contructor as instantiation of
        provider should be kept as lightweight as possible.
        '''
        # Initialize the service
        try:
            self.__create_service()
        except Exception as e:
            raise AuthorizationProviderError("Create Service Error: %s" % e)
        
    '''
    Create and return service
    '''
    _service = None
    def __create_service(self):
        '''Create a OAuth2 Service from the _serv_params populate by constructore'''
        self._service = OAuth2Service(**self._serv_params)
    @property
    def service(self):
        '''Return read-only'''
        return self._service

    '''
    Create and set tokens
    '''
    _access_token = None
    _access_token_secret = None
    def __create_access_token(self):
        access_token, access_token_secret = self.service.get_access_token()
        self._access_token = access_token 
        self._access_token_secret = access_token_secret
    @property
    def oauth_login_token(self):
        '''Return the token used when loggin in'''
        return self._access_token
    
    '''
    OAuth2's implmentation of authorize_url and authorized_session
    '''
    def authorize_url(self, tpid):
        self.set_oauth_reply_url(tpid)
        params = { "redirect_uri": self.oauth_reply_url }
        return self.service.get_authorize_url(**params)
    
    def authorized_session(self, **kwargs):
        # Must set self._oauth_verifier before calling this
        return self.service.get_auth_session(data=kwargs)
