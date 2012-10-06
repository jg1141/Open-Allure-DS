# -*- coding: utf-8 -*-
"""
exeMaker.py
a component of SlideSpeech.py

Creates SlideSpeech.exe for Windows

python ss2exe.py py2exe

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""
from distutils.core import setup
import py2exe

setup(console=['SlideSpeech.py'],
      options = {"py2exe": { "dll_excludes": ["POWRPROF.dll",
                                              "tk85.dll",
                                              "tcl85.dll"],
                             "bundle_files" : 1,
                           }
                },
      data_files=[(".",['CHANGES.txt',
                       'ethics_notice.txt',
                       'README.txt',
                       'LICENSE.txt',
                       'script.txt',
                       'SayStatic.exe']),
                  ("static/test",["static/test/Slide1.PNG",
                                  "static/test/Slide2.PNG"])],
      zipfile=None,
     )
