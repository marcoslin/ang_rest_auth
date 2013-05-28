'''
Created on 20 May 2013

@author: Marcos Lin

Wrapper for OAuth Providers
'''

import cPickle
from auth.base import OAuth1Provider, OAuth2Provider, AuthorizationProviderError, UnauthorizedError

# Base Class for OAuth
class GoogleOAuthProvider(OAuth1Provider):
    def __init__(self):
        super(GoogleOAuthProvider, self).__init__(
            name="google-oauth",
            consumer_key="AngRestAuth",
            consumer_secret="Jdbisf732sdsdf/623rn",
            request_token_url='https://www.google.com/accounts/OAuthGetRequestToken',
            authorize_url='https://www.google.com/accounts/OAuthAuthorizeToken',
            access_token_url='https://www.google.com/accounts/OAuthGetAccessToken',
            base_url='https://www.google.com'
        )

class TwitterOAuthProvider(OAuth1Provider):
    def __init__(self):
        super(TwitterOAuthProvider, self).__init__(
            name='twitter-oauth',
            consumer_key='SKJ1AO0jTc0SlniK868w',
            consumer_secret='pROCsoUl0LbVF6t05t25KaF9J7lAFgmrOvjhT1ojc',
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            base_url='https://api.twitter.com/1.1/'
        )

    def process_oauth_reply(self, request_args):
        '''
        Read the user detail from the oauth's provider's reply
        request_args an werkzeug.datastructures.ImmutableMultiDict and basically
        represent the query string from the reply 
        '''
        if request_args.get('denied'):
            raise UnauthorizedError("TwitterOAuthProvider returned 'denied'")
        
        oauth_verifier = request_args.get("oauth_verifier")
        self._session = self.authorized_session(oauth_verifier)
        resp = self._session.get("account/verify_credentials.json", params={'format': 'json'})
        resp_json = resp.json()
        
        self.set_user_info(
            user_id = resp_json["id_str"],
            user_name = resp_json["screen_name"],
            user_fullname = resp_json["name"]
        )
        return self.user_info

class FacebookProvider(OAuth2Provider):
    def __init__(self):
        super(FacebookProvider, self).__init__(
            name='facebook-oauth2',
            client_id='377093625673791',
            client_secret='3bd84d944b41ac80156420889408c34d',
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def process_oauth_reply(self, request_args):
        code = request_args.get("code")
        if not code:
            raise UnauthorizedError("FacebookProvider returned Unauthorized")
        
        session = self.authorized_session(code=code, redirect_uri=self.oauth_reply_url)
        facebook_user = session.get('me').json()
        
        self.set_user_info(
            user_id = facebook_user["id"],
            user_name = facebook_user["username"],
            user_fullname = facebook_user["name"]
        )
        
        return self.user_info


class AuthProviders(object):
    '''
    Return instance of authentication provider by name
    '''
    # Add all provider classes to the _provider_classes tuple below
    _provider_classes = (
                GoogleOAuthProvider, TwitterOAuthProvider, FacebookProvider
                )
    
    def __init__(self):
        '''Instantiate all providers and retrieve the name.  Any provider configured incorrectly will raiser error here'''
        prov = {}
        for cls in self._provider_classes:
            provider = cls()
            prov[provider.name] = provider
        self._providers = prov
    
    def get(self, provider_name):
        '''Return an instance of the provider requested and call the provider's initialize method.  If provider_name not found, raise ValueError'''
        try:
            inst = self._providers[provider_name]
            inst.initialize()
            return inst
        except KeyError:
            raise ValueError("Requested AuthProvider '%s' does not exists." % provider_name)
        except AuthorizationProviderError as e:
            raise e

    def regenerate(self, persist_string):
        return cPickle.loads(persist_string)
