.. OpenAllure documentation master file, created by
   sphinx-quickstart on Fri Feb 12 15:19:58 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Open Allure's documentation!
=======================================

Open Allure is a voice-and-vision enabled dialog system written in Python_.

.. _Python: http://www.python.org/

You might check_ to see if you are reading the most recent documentation--and using the most recent
version of Open Allure for that matter.

.. _check: http://packages.python.org/openallure/

Edit the openallure.cfg file (see the annotated copy in this documentation) to configure the 
location of the initial question/answer/response sequence and other settings as appropriate 
for your system.

Open Allure is part of the output of the `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

`A collection of short videos`_ about the Open Allure project are available and
there is `a Google group you can join`_ for updates and discussion.

.. _A collection of short videos: http://bit.ly/openallure

.. _a Google group you can join: http://bit.ly/openalluregg

Cross-Platform Status
=====================

Open Allure aims to run on Windows, Linux and Mac. The Windows platform
currently tops the feature list with working voice and vision input and pretty
good text-to-speech output running Vista.  Linux has working vision input and
so-so text-to-speech output (eSpeak).  Mac has neither voice nor vision input
but has the best text-to-speech output (say).

Dependencies
============

Open Allure uses pyGame_ and BeautifulSoup_ and NLTK_ (Natural Language Toolkit).

Windows systems use vidcap.py_ to help the pyGame camera module.

Voice recognition depends on the operating system or other software. For Windows, dragonfly_
connects to the Windows Speech API. For Mac, dragonfly_ connects to `MacSpeech Dictate`_. For linux,
we're still looking to connect a voice recognition backend -- please pitch in!

.. _pyGame: http://www.pygame.org/

.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/

.. _NLTK: http://www.nltk.org/download

.. _vidcap.py: http://videocapture.sourceforge.net/

.. _dragonfly: http://code.google.com/p/dragonfly/

.. _MacSpeech Dictate: http://www.macspeech.com

Configuration
=============

.. toctree::

   txt/openallure

Modules
=======

.. toctree::
   :maxdepth: 2

   modules/openallure
   modules/chat
   modules/responses
   modules/qsequence
   modules/gesture
   modules/text
   modules/voice
   modules/video

TXT Documentation
=================

.. toctree::

   txt/CHANGES
   txt/ethics_notice
   txt/LICENSE
   txt/README

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

