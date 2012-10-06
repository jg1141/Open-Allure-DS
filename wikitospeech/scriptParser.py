#-------------------------------------------------------------------------------
# Name:        scriptParser.py
# Purpose:     extract Wiki-to-Speech sequence from script text
#
# Author:      John Graves
#
# Created:     17 April 2011
# Modified:    13 September 2011
# Copyright:   (c) John 2011
# Licence:     MIT license
#-------------------------------------------------------------------------------
from BeautifulSoup import BeautifulSoup
import htmlentitydefs
import objects
import os
import re
import subprocess
import sys
import urllib
from time import gmtime, strftime

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def parseScript(name):
    if name.startswith("http"):
        if name.find("wikitospeech.pagekite.me")>0:
            sequence = parseForm(name)
        elif name.find("titanpad")>0:
            sequence = parseEtherpad(name)
        else:
            sequence = parseHtml(name)
    else:
        if name.endswith(".txt"):
            sequence = parseTxtFile(name)
        else:
            sequence = None
##            # No parsing of .html
##            # Set up dummy sequence
##            seq = objects.Sequence()
##            seq.sequence = []
##            question = objects.Question()
##            question.questionTexts = []
##            question.questionTexts.append("Opening "+name)
##            question.linkToShow = name
##            seq.sequence.append(question)
##            sequence = seq.sequence
##            dumpSequence(seq, False)
    return sequence

def parseEtherpad(name):
    # download Etherpad and extract script
    # http://ietherpad.com/mieeiphS5# J
    try:
        proxy = os.environ["HTTP_PROXY"]
    except:
        proxy = ''
    if proxy=="http://cache.aut.ac.nz:3128":
        proxies = {'http': 'http://cache.aut.ac.nz:3128'}
        urlOpen = urllib.urlopen( name , proxies=proxies )
    else:
        urlOpen = urllib.urlopen( name, proxies={} )
    soup = BeautifulSoup(urlOpen.read())
    postbody = soup.find("div", { "class" : "postbody" })
    soupString = ""
    try:
        soupString = str(soup)
    except UnicodeDecodeError:
        # no luck here, give up
        return None
    if len(soupString) > 0:
        cleanUnicodeTextStr = \
        soupString[ soupString.find(u'"initialAttributedText":{"text"')+33 : \
                   soupString.find(u',"attribs":')-1 ]
        text = unescape(cleanUnicodeTextStr).split('\\n')
    else:
        return None
    sequence = parseText(text)
    return sequence

def parseForm(name):
    # download and extract script from wikitospeech.pagekite.me page, for example:
    # http://wikitospeech.pagekite.me?tag=Test
    try:
        proxy = os.environ["HTTP_PROXY"]
    except:
        proxy = ''
    if proxy=="http://cache.aut.ac.nz:3128":
        proxies = {'http': 'http://cache.aut.ac.nz:3128'}
        urlOpen = urllib.urlopen( name , proxies=proxies )
    else:
        urlOpen = urllib.urlopen( name, proxies={} )

    # extract text marked with <from> from wikitospeech page
    soup = BeautifulSoup(urlOpen.read())
    taggedPre = soup.form
    img=[i['src'] for i in soup.form.findAll('img')]
    #[u'http://dl.dropbox.com/u/12838403/20120109/img0.png', u'http://dl.dropbox.com/u/12838403/20120109/img1.png']
    text=[i.contents[0].strip() for i in soup.form.findAll('textarea')]
    #[u'Notes on slide 1', u'Notes on slide 2']
    urlText = []
    for i in range(0,len(img)): 
        print i
        urlText.append(img[i])
        textLines = text[i].split("\n")
        for line in textLines:
            urlText.append(line)
        urlText.append("\n")

    f = open('debug.txt','w')
    f.write("test run at " + strftime("%d %b %Y %H:%M", gmtime()) + "\n")
    f.write(str(type(urlText))+ "\n")
    f.write(str(len(urlText))+ "\n")
    for l in urlText:
        f.write(l.strip()+"\n")
    f.close()

    sequence = parseText(urlText)
    return sequence
    
def parseHtml(name):
    # download and extract script from wiki page, for example:
    # http://dl.dropbox.com/u/12838403/dropbox.txt
    try:
        proxy = os.environ["HTTP_PROXY"]
    except:
        proxy = ''
    if proxy=="http://cache.aut.ac.nz:3128":
        proxies = {'http': 'http://cache.aut.ac.nz:3128'}
        urlOpen = urllib.urlopen( name , proxies=proxies )
    else:
        urlOpen = urllib.urlopen( name, proxies={} )
    if name.endswith(".txt"):
        urlText = urlOpen.read().split("\n")
    else:
        # extract text marked with <pre> from wiki or blog page
        soup = BeautifulSoup(urlOpen.read())
        taggedPre = soup.pre
        if taggedPre != None:
            taggedPreStr = str(taggedPre).replace('<br />\n','\n')
            taggedPreStr = taggedPreStr.replace('<br />','\n')
            soup = BeautifulSoup(taggedPreStr)
            urlText = unescape(''.join(soup.pre.findAll(text=True))).splitlines()
        else:
            return None

    f = open('debug.txt','w')
    f.write("test run at " + strftime("%d %b %Y %H:%M", gmtime()) + "\n")
    f.write(str(type(urlText))+ "\n")
    f.write(str(len(urlText))+ "\n")
    for l in urlText:
        f.write(l.strip()+"\n")
    f.close()

    sequence = parseText(urlText)
    return sequence

def parseTxtFile(name):
    # open txt file
    try:
        f = open(name)
    except:
        # No parsing of .txt
        return None
    text = f.readlines()

    if not sys.platform.startswith("win"):
        # find slide images in .txt file and make symbolic links if possible
        pngs = [item.strip() for item in text if item.endswith(".png\n")]
        # script source directory
        scriptDir, scriptFile = os.path.split(name)
        savePath = os.getcwd()
        os.chdir('static')
        staticDir = os.listdir(".")
        pngsInStatic = [file for file in staticDir if file.endswith(".png")]
        for png in pngs:
            if png in pngsInStatic:
                subprocess.Popen(["rm",png])
            subprocess.Popen(["ln","-s",scriptDir+os.sep+png,png])
        os.chdir(savePath)

    sequence = parseText(text)
    return sequence

def parseText(text):
    # guess at questionMode based on first line
    if text[0].lower().endswith(".png") or text[0].startswith("[path="):
        questionMode = False
    else:
        questionMode = True
    seq = objects.Sequence()
    seq.sequence = []
    pathToImageFiles = ""
    question = objects.Question()
    answer = objects.Answer()
    for line in text:
        line = line.strip()
        if not line.startswith("#"): # ignore comment lines
            if (line.startswith("[") and not line.endswith(";")):
                if len(question.questionTexts)>0:
                    seq.sequence.append(question)
                    question = objects.Question()
                    question.pathToImageFiles = pathToImageFiles
                equalsAt = line.find("=")
                if equalsAt>1: # set parameters
                    parameterName = line[1:equalsAt].strip().lower()
                    parameterValue = line[equalsAt+1:line.find("]")].strip().lower()
                    if parameterName == "questions":
                        if parameterValue == "on":
                            questionMode = True
                        if parameterValue == "off":
                            questionMode = False
                        continue
                    elif parameterName == "path":
                        if((not parameterValue.endswith(os.sep) or (not parameterValue.endswith("\\")))):
                            parameterValue += os.sep
                        pathToImageFiles = parameterValue
                        question.pathToImageFiles = pathToImageFiles
                        continue
                else: # question tag
                    question.tag = line[1:line.find("]")]

            else:
                line = line.strip()
                if questionMode == False:
                    # In default mode, expected arrangement of links and text
                    # is
                    #    LINK (ending in http/html/jpg)
                    #    TEXT FOR VOICE OVER
                    #    (optionally several lines long)
                    #
                    if len(line)>0:
                        if (line.startswith("http") or
                            line.endswith(".html") or
                            line.endswith(".jpg") or
                            line.endswith(".JPG") or
                            line.endswith(".png") or
                            line.endswith(".PNG")):
                                if len(question.questionTexts)>0:
                                    seq.sequence.append(question)
                                    question = objects.Question()
                                    question.pathToImageFiles = pathToImageFiles
                                question.linkToShow = line
                        else:
                            question.questionTexts.append(line)
                else:
                    # questionMode == True
                    # In question mode, expected arrangement
                    # is
                    #    (optional image to show)
                    #    QUESTION
                    #    (optionally several lines long)
                    #    ANSWER ;[ACTION] [RESPONSE]
                    #    (optionally repeated)
                    #
                    if len(line)>0:
                        if (line.endswith(".jpg") or
                            line.endswith(".JPG") or
                            line.endswith(".png") or
                            line.endswith(".PNG")):
                                if len(question.questionTexts)>0:
                                    seq.sequence.append(question)
                                    question = objects.Question()
                                    question.pathToImageFiles = pathToImageFiles
                                question.linkToShow = line
                        else:
                            semicolonAt = line.find(";")
                            if -1 == semicolonAt:
                                question.questionTexts.append(line)
                            else: # parse answer
                                answer.answerText = line[0:semicolonAt].strip()
                                responseSide = line[semicolonAt+1:].strip()
                                if len(responseSide)>0:
                                    while responseSide.startswith(";"):
                                        answer.action += 1
                                        responseSide = responseSide[1:].strip()
                                    if responseSide.startswith("["):
                                        rightbracketAt = responseSide.find("]")
                                        answer.responseSideLink = responseSide[1:rightbracketAt]
                                        responseSide = responseSide[rightbracketAt+1:].strip()
                                    answer.responseText = responseSide
                                if answer.answerText == "[next]":
                                    answer.action = 1
                                question.answers.append(answer)
                                answer = objects.Answer()

                    else: # blank line
                        if len(question.questionTexts)>0:
                            seq.sequence.append(question)
                            question = objects.Question()
                            question.pathToImageFiles = pathToImageFiles

    if len(question.questionTexts)>0:
        seq.sequence.append(question)

    # second pass to match responseSideLinks to tags and adjust actions
    tags = [ question.tag.lower() for question in seq.sequence ]
    for qnum, question in enumerate( seq.sequence ):
        for answer in question.answers:
            if answer.responseSideLink != "":
                if answer.responseSideLink.lower() in tags:
                    # remove link
                    answer.action = tags.index(answer.responseSideLink) - qnum
                    answer.responseSideLink = ""

    dumpSequence(seq, questionMode)

    return seq.sequence

def dumpSequence(seq, questionMode):
    if True:
        f = open('debug2.txt','w')
        f.write("test run at " + strftime("%d %b %Y %H:%M", gmtime()))
        f.write("\nquestionMode is "+ str(questionMode))
        for i, q in enumerate(seq.sequence):
            f.write("\nQuestion "+str(i)+"-"*30)
            f.write("\n               tag: "+q.tag)
            f.write("\n        linkToShow: "+q.linkToShow)
            f.write("\n  pathToImageFiles: "+q.pathToImageFiles)
            for l in q.questionTexts:
                f.write("\n      questionText: "+l)
            for j, a in enumerate(q.answers):
                f.write("\n       answerText"+str(j)+": "+a.answerText)
                f.write("\n responseSideLink"+str(j)+": "+a.responseSideLink)
                f.write("\n     responseText"+str(j)+": "+a.responseText)
                f.write("\n           action"+str(j)+": "+str(a.action))
        f.close()

if __name__ == "__main__":
    parseTxtFile("20110819b.txt")