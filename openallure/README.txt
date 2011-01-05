===========
Open Allure
===========

Open Allure is a text-to-speech dialog system

For the latest version, please check http://openallureds.org

Installation
============

If you have unzipped the archive to read this README.txt file
the application can be run from this same directory without 
further installation.  Just double-click the openallure icon.

Delete it to uninstall.

Usage
=====

       Keys:
           Escape quits
           Ctrl+I force input
           Ctrl+R refresh
           Ctrl+V paste

       Commands:
           exit
           open <filename or url>
           quit
           return (resumes at last question)
           show source 

Getting Started
===============

Enter

   open welcome.txt

and the software should begin talking.

To access a script on a webpage, type

   open <webpage address>
   
You can copy the webpage address from your web browser and paste it with 
Control+V. (This should be Command+V on Mac OSX, but it's not yet.)

The webpage needs to contain an Open Allure script, marked off as
preformatted text with the <pre> </pre> HTML tags.  

Alternatively, the script can be in a NING blog post as in
http://openallureds.ning.com/profiles/blogs/music-1

Or the script can be on an Etherpad as in
http://bit.ly/oa1d27

Script syntax is discussed here
http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax

Dependencies
============

These may vary depending on the platform

StaticSay
http://krolik.net/post/Say-exe-a-simple-command-line-text-to-speech-program-for-Windows.aspx

Pygame
http://www.pygame.org/download.shtml
Version 1.9.1 was used during development of Open Allure

BeautifulSoup
http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.8.tar.gz
Version 3.0.8 was used during development of Open Allure
(easy_install BeautifulSoup)

NLTK
http://www.nltk.org/download
Steven Bird, <sb@csse.unimelb.edu.au>

License
=======

Copyright (c) 2011 John Graves

MIT License.  See LICENSE.txt


Contributors
============
John Graves, <john.graves@aut.ac.nz>
Brian Thorne, <brian.thorne@canterbury.ac.nz>
