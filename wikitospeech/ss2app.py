#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ss2app.py
# Purpose:     Compile SlideSpeech.py into Mac OSX Application
#
# Author:      John Graves
#
# Created:     24 August 2011
# Modified:    28 November 2011
# Copyright:   (c) John Graves 2011
# License:     MIT License
#-------------------------------------------------------------------------------

from setuptools import setup
import operator
import os
import shutil
import sys


class BuildApp:
    def __init__(self):
        self.APP = ['SlideSpeech.py']
        self.DATA_FILES = ['CHANGES.txt','ethics_notice.txt','README.txt','LICENSE.txt']
        self.OPTIONS = {'argv_emulation': True, 'iconfile': 'slidespeech.icns',}
        #Dist directory
        self.dist_dir ='dist'

    def run(self):
        if os.path.isdir(self.dist_dir): #Erase previous destination dir
            shutil.rmtree(self.dist_dir)

        setup(
            app=self.APP,
            data_files=self.DATA_FILES,
            options={'py2app': self.OPTIONS},
            setup_requires=['py2app'],
        )

        if os.path.isdir('build'): #Clean up build dir
            shutil.rmtree('build')

if __name__ == '__main__':
    if operator.lt(len(sys.argv), 2):
        sys.argv.append('py2app')
    BuildApp().run() #Run generation
    raw_input("Press any key to continue") #Pause to let user see that things ends
