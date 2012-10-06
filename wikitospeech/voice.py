# -*- coding: utf-8 -*-
"""
voice.py
a component of openallure.py

Function for rendering text-to-speech

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

import os
import subprocess
import sys
from time import gmtime, strftime

class Voice( object ):
    """Text-to-speech class"""
    def __init__( self ):
        self.pid_status = 0

    def speak( self, phrase, systemVoice ):
        """Say or print phrase using text-to-speech engine or stdout.

        An empty phrase returns without calling the speech engine.

        espeak (engine) could take an optional Voice:language parameter

        say (engine) could take a systemVoice
        """
        phrase = phrase.strip()
        phrase = phrase.replace('http://www.','')

        if len(phrase) == 0:
            return
        if phrase == "[next]":
            return

        if sys.platform == 'darwin':
            #systemVoice = "Rachel"
            systemVoice = "Alex"
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

        elif sys.platform == 'win32':
            try:
                proc = subprocess.Popen(["SayStatic ", phrase ], shell=True)
            except OSError:
                print("Call to SayStatic failed")
            proc.wait()
            return

        else:
            f = open('debug3.txt','w')
            f.write("test run at " + strftime("%d %b %Y %H:%M", gmtime()) + "\n"+phrase)
            f.close()

            proc = subprocess.Popen( ['espeak', '"' + phrase + '"' ] )
            proc.wait()


def testVoice():
    '''
    Create a Voice instance and check that it works
    '''
    voice = Voice()
    voice.speak("This is a test","")

if __name__ == "__main__":
    testVoice()
