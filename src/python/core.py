'''
Created on 21 May 2013

@author: Marcos Lin

Provide core utilities objects for the app.
'''

import os, sys, inspect

# ==============================================================================
# code debug print statement
def trace(*args):
    '''
    core.trace is light weight debug statement to be used for code that imports this package.
    To minimize unnecessary processing, make sure to pass a tuple of string to be joined upon
    trace output instead of creating the final string on the caller side.

    For trace statement in a heavily used code and/or loop, make sure to precede the trace
    statement with a 'if __debug__:' check allowing entire trace statement to be compiled out.
    In fact, if this module is compiled with optimization, trace will stop working.
    '''
    if __debug__:
        if ( sys.flags.debug ):
            filename = os.path.basename(inspect.stack()[1][1])
            caller = inspect.stack()[1][3]
            # Convert all args into string
            msgs = []
            for arg in args:
                if isinstance(arg, basestring):
                    msgs.append(arg)
                else:
                    msgs.append(str(arg))
            print "T.%s: %s (%s)" % (caller, ''.join(msgs), filename)

# ==============================================================================
# Singletons
class Singleton(type):
    '''Meta Class used to create a singleton'''
    def __init__(cls, name, bases, dct):
        #print "### Singleton called for class %s" % name
        super(Singleton, cls).__init__(name, bases, dct)
        cls.instance = None 

    def __call__(cls, *args, **kwargs): #@NoSelf
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        #print "### Returning Singleton instance %s" % cls.instance
        return cls.instance
