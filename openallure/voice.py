"""
voice.py
a component of openallure.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt

TODO: Add standalone tests for text-to-speech modules.
"""

import os
import ConfigParser
import pygame

# only allow useDragonfly if dragonfly module can be imported
allowUseDragonfly = True
try:
    import dragonfly
except ImportError:
    allowUseDragonfly = False

class Voice( object ):
    """Text-to-speech Functionality ( optional )"""
    def __init__( self ):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """
        config = ConfigParser.RawConfigParser()
        config.read( 'openallure.cfg' )
        if allowUseDragonfly:
            self.useDragonfly = eval( config.get( 'Voice', 'useDragonfly' ) )
        else:
            self.useDragonfly = False
            wantedToUseDragonfly = eval( config.get( 'Voice', 'useDragonfly' ) )
            if wantedToUseDragonfly:
                print "Dragonfly module not installed. Download from http://code.google.com/p/dragonfly/"

        self.useEspeak = eval( config.get( 'Voice', 'useEspeak' ) )
        self.useSay    = eval( config.get( 'Voice', 'useSay' ) )
        self.language  = config.get( 'Voice', 'language' )
        if self.language:
            self.language = self.language + " "

    def speak( self, phrase ):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.useDragonfly:
           e = dragonfly.get_engine()
           e.speak( phrase.encode( 'utf-8' ) )
       elif self.useEspeak:
           os.system( 'espeak -s150 "' + self.language + phrase.encode( 'utf-8' ) + '"' )
       elif self.useSay:
           os.system( 'say "' + self.language + phrase.encode( 'utf-8' ) + '"' )
       else:
           print( phrase.encode( 'utf-8' ) )
           # Allow time for user to move hand down
           pygame.time.wait( 500 )

def test_voice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("Hello World")

if __name__ == "__main__":
    test_voice()
