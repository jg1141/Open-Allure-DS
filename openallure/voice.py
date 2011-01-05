# -*- coding: utf-8 -*-
"""
voice.py
a component of openallure.py

Function for rendering text-to-speech

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

from configobj import ConfigObj
import os
import subprocess
import sys

class Voice( object ):
    """Text-to-speech class"""
    def __init__( self ):
        """Initialize flags for text-to-speech engines"""
        self.useEspeak = 0
        self.useSay = 0
        self.useSayStatic = 0
        config = ConfigObj("openallure.cfg")
        if sys.platform == 'darwin':
            self.useSay = eval( config['Voice']['useSay'] )
        elif sys.platform == 'win32':
            self.useSayStatic = eval( config['Voice']['useSayStatic' ] )
        else:
            self.useEspeak = eval( config['Voice']['useEspeak'] )
        self.language = config['Voice']['language'] 
        if self.language:
            self.language = self.language + " "
        self.pid_status = 0

    def speak( self, phrase, systemVoice ):
        """Say or print phrase using text-to-speech engine or stdout.
        
        An empty phrase returns without calling the speech engine.
        
        espeak (engine) takes an optional Voice:language parameter from openallure.cfg.
        
        say (engine) takes a systemVoice where selected voice which may come from 
        Options:language in openallure.cfg or [systemVoice=xx] override in a script.
        """
        phrase = phrase.strip()
        if len(phrase) == 0:
            return

        if self.useEspeak:
            subprocess.Popen( ['espeak', " -s150 " + self.language + \
                               phrase + '"' ] )
        elif self.useSay:
            commandLine = 'say -v ' + systemVoice + ' "' + phrase + '"' 
            if self.pid_status == 0:
                self.pid_status = subprocess.Popen(commandLine,shell=True).pid
            else:
                # wait for prior speaking to finish
                try:
                    self.pid_status = os.waitpid(self.pid_status, 0)[1]
                except:
                    pass
                self.pid_status = subprocess.Popen(commandLine,shell=True).pid
                
        elif self.useSayStatic:
            try:
                subprocess.call(["SayStatic ", \
                                 phrase], shell=True)
            except OSError, e:
                print("Call to SayStatic failed:", e)
                
        else:
            print(phrase)

def testVoice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    if sys.platform == 'darwin':
        voice.speak(u"This is a test", u"Alex")
        voice.speak(u"Questa è una prova", u"Chiara")
        voice.speak(u"Este é um teste", u"Marcia")
    else:
        voice.speak("This is a test", u"")

if __name__ == "__main__":
    testVoice()
