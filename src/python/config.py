import os
basedir = os.path.abspath(os.path.dirname(__file__))




class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
    SECRET_KEY = 'you-will-never-guess'
    USE_RELOADER = False
    


class DevelopmentConfig(Config):
    DEBUG = True        
    PORT = 5000
    
    
class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    USE_RELOADER = True