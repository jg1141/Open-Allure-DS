# -*- coding: utf-8 -*-
"""
SlideSpeech.py

Use browser and local text-to-speech engine
to display and play Wiki-to-Speech scripts

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt

20110818 Changes to enable reading http://aucklandunitarian.pagekite.me/Test20110818b
20110819 Tested on Mac:
http://aucklandunitarian.pagekite.me/Test20110814
http://aucklandunitarian.pagekite.me/Test20110819 which calls another script
http://aucklandunitarian.pagekite.me/Test20110819b which has [path=pathToImageFiles] and
   combined image with question
20110822 Added version number to input form
20110824 Pass __version__ to input form
         Ensure static directory exists
20110825 Add __version__ to title
20110909 Added question number to showQuestion (so going back should work)
20110913 Make symbolic links from static directory to location of script.txt png images
20111126 Titanpad in addition to iEtherpad. Jump to 0.1.26 to sync with odp2wts (SlideSpeech)
20111128 Changed name to SlideSpeech. Revised voice.py to work under Linux.
20111207 Sync version number with SlideSpeech Converter
"""
import cherrypy
import os.path
import Queue
import threading
import webbrowser

import forms
import objects
import scriptParser
import sys
import voice

__version__ = "0.1.31"

if not os.path.exists('static'):
    os.makedirs('static')

class WelcomePage:

    def index(self):
        # Ask for the script name.
        return forms.scriptInputFormWithErrorMessage(__version__,"")
    index.exposed = True
    webbrowser.open_new_tab('http://localhost:8080')

    def SlideSpeech_Exit_Complete(self):
        webbrowser.open_new_tab('http://slidespeech.org')
        sys.exit()
    SlideSpeech_Exit_Complete.exposed = True

    def getScriptName(self, name = None):
        #name = "http://dl.dropbox.com/u/12838403/20110428a.txt"
        if name:
            if name=="exit":
                sys.exit()
            seq.sequence = scriptParser.parseScript(name)
            if seq.sequence:
                seq.onQuestion = 0
                return speakAndReturnForm()
            else:
                return forms.scriptInputFormWithErrorMessage( \
                       __version__,
                       "<i>Could not open "+name+"</i>")
        else:
            # No name was specified
            return forms.scriptInputFormWithErrorMessage( \
                       __version__,
                       "<i>Please enter a file name or link on the web.</i>")
    getScriptName.exposed = True

    def nextSlide(self):
        clearQueue()
        seq.onQuestion += 1
        if seq.onQuestion > len(seq.sequence) - 1:
            return forms.scriptInputFormWithErrorMessage(__version__,"")
        else:
            return speakAndReturnForm()
    nextSlide.exposed = True

    def nextSlideFromAnswer0(self, q):
        return respondToAnswer(0, q)
    nextSlideFromAnswer0.exposed = True

    def nextSlideFromAnswer1(self, q):
        return respondToAnswer(1, q)
    nextSlideFromAnswer1.exposed = True

    def nextSlideFromAnswer2(self, q):
        return respondToAnswer(2, q)
    nextSlideFromAnswer2.exposed = True

    def nextSlideFromAnswer3(self, q):
        return respondToAnswer(3, q)
    nextSlideFromAnswer3.exposed = True

    def nextSlideFromAnswer4(self, q):
        return respondToAnswer(4, q)
    nextSlideFromAnswer4.exposed = True

    def nextSlideFromAnswer5(self, q):
        return respondToAnswer(5, q)
    nextSlideFromAnswer5.exposed = True

    def nextSlideFromAnswer6(self, q):
        return respondToAnswer(6, q)
    nextSlideFromAnswer6.exposed = True

seq = objects.Sequence()
voiceInstance = voice.Voice()

def speakAndReturnForm():
    # Check for visited answers. If found, do not re-read question
    noVisitedAnswers = True
    for a in seq.sequence[seq.onQuestion].answers:
        if a.visited:
            noVisitedAnswers = False
    if noVisitedAnswers:
        speakList(seq.sequence[seq.onQuestion].questionTexts)
        for a in seq.sequence[seq.onQuestion].answers:
            speakList([a.answerText])
    linkToShow = seq.sequence[seq.onQuestion].linkToShow

    if linkToShow.lower().endswith(".pdf"):
        return forms.showPDFSlide(seq.sequence[seq.onQuestion].linkToShow)

    elif linkToShow.lower().endswith(".jpg") or linkToShow.lower().endswith(".png"):
        if linkToShow.startswith("Slide") or linkToShow.startswith("img") or \
           linkToShow.find("\Slide")!=-1 or linkToShow.find("/img")!=-1:
            if len(seq.sequence[seq.onQuestion].pathToImageFiles)>0:
                linkToShow = seq.sequence[seq.onQuestion].pathToImageFiles + linkToShow
            else:
                pass
                #linkToShow = "static/" + linkToShow
        if len(seq.sequence[seq.onQuestion].answers)>0:
            return forms.showJPGSlideWithQuestion(linkToShow, \
                                     seq.sequence[seq.onQuestion] )
        else:
            return forms.showJPGSlide(linkToShow)

    elif linkToShow.lower().endswith(".htm"):
        return forms.showDHTML()
    elif linkToShow.lower().endswith(".swf"):
        return forms.showSWF()
    elif len(linkToShow)>0:
        #return forms.showWebsite(seq.sequence[seq.onQuestion])
        return forms.showQuestionAndWebsite(seq.sequence[seq.onQuestion], seq.onQuestion)
    else: # no match for linkToShow
        return forms.showQuestion(seq.sequence[seq.onQuestion], seq.onQuestion)

def respondToAnswer(n, q):
    clearQueue()
    response = ""
    seq.onQuestion = int(q)
    if n<len(seq.sequence[seq.onQuestion].answers):
        # mark answer as visited
        seq.sequence[seq.onQuestion].answers[n].visited = True
        # say what there is to say
        response = seq.sequence[seq.onQuestion].answers[n].responseText
        if response != "":
            speakList([response])
        # follow any response side link
        responseSideLink = seq.sequence[seq.onQuestion].answers[n].responseSideLink
        if len(responseSideLink)>0:
            seq.sequence = scriptParser.parseScript(responseSideLink)
            if seq.sequence:
                seq.onQuestion = 0
                return speakAndReturnForm()
            #TODO error recovery
        # move to whichever question comes next
        if seq.sequence[seq.onQuestion].answers[n].action != 0:
            nextQ = seq.onQuestion + seq.sequence[seq.onQuestion].answers[n].action
            if 0 <= nextQ <= len(seq.sequence):
                seq.onQuestion = nextQ
    if seq.onQuestion<len(seq.sequence):
        return speakAndReturnForm()
    else:
        # past end of sequence
        speakList(["You have reached the end. Please select another script."])
        return forms.scriptInputFormWithErrorMessage(__version__,"")

def clearQueue():
    while not q.empty():
        q.get()

def worker():
    while True:
        text = q.get()
        voiceInstance.speak(text, "")
        q.task_done()

q = Queue.Queue()
t = threading.Thread(target=worker)
t.daemon = True
t.start()

def speakList(textList):
    for item in textList:
        q.put(item)
    #q.join()       # block until all tasks are done

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                        'server.socket_port': 8080,
                        'server.thread_pool': 10,
                       })
    config = {'/': {'tools.staticdir.root': os.path.abspath(os.curdir)},
              '/static':{'tools.staticdir.on':True,
                         'tools.staticdir.dir':"static"}}
    cherrypy.quickstart(WelcomePage(), config=config)

