"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

__version__ = '0.1d33dev'

# Standard Python modules
import itertools
import os
import sys
import time
import webbrowser
import gettext

# 3rd Party modules
# note: nltk is used by chat.py
from configobj import ConfigObj
import pygame
from buzhug import Base

# Import from Open Allure DS modules
from qsequence import QSequence
#from oagraph import oagraph, oaMetaGraph, wrapWords
from voice import Voice
from text import OpenAllureText
from chat import Chat, responses, reflections

QUESTION = 0
ANSWER = 1
RESPONSE = 2
ACTION = 3
DESTINATION = 4
LINK = 5
INPUTFLAG = 6
#PHOTOS = 7
TAG = 8
RULE = 9

class OpenAllure(object):
    def __init__(self):
        self.__version__ = __version__
        self.currentString = u''
        self.question = []
        self.ready = False
        self.stated = False
        self.statedq = -1
        self.voiceChoice = -1
        self.lastQuestionAnswered = 0
        self.systemVoice = ''

openallure = OpenAllure()

def inRegion(region, y):
    if y >= region[1] and y <= region[3]:
        return 1
    else:
        return 0

def main():
    """Initialization and event loop"""

    # provide instructions and other useful information

    # initialize pyGame screen
    textRect = pygame.rect.Rect(0, 0, 640, 480)
    screenRect = pygame.rect.Rect(0, 0, 640, 480)
    pygame.init()
    pygame.display.set_caption(u"Open Allure")
    screen = pygame.display.set_mode(screenRect.size)
    if sys.platform != 'darwin':
        pygame.scrap.init()

    config = ConfigObj('openallure.cfg')

    # determine what language to use for string translations
    # this can be overridden in scripts
    gettext.install(domain='openallure', localedir='locale', unicode=True)
    try:
        language = config['Options']['language']
    except KeyError:
        language = 'en'
    if len(language) > 0 and language != 'en':
        mytrans = gettext.translation(u"openallure",
                                      localedir='locale',
                                      languages=[language], fallback=True)
        mytrans.install(unicode=True) # must set explicitly here for Mac
    # language also determines which default systemVoice to use (Mac only)
    openallure.systemVoice = ''
    try:
        openallure.systemVoice = config['Voice'][language]
    except KeyError:
        pass

    # load initial question sequence from url specified in openallure.cfg file
    url = unicode(config['Source']['url'])
    if len(sys.argv) > 1 and 0 != len(sys.argv[1]):
        url = unicode(sys.argv[1])
    backgroundColor = eval(config['Colors']['background'])
    seq = QSequence(filename = url)
    try:
        openallure.systemVoice = config['Voice'][seq.language]
    except KeyError:
        pass

    # open database to track progress

    oadb = config['Data']['oadb']
    try:
        openallure.db = Base(oadb).open()
    except IOError:
        openallure.db = Base(oadb)
        openallure.db.create(('time',float), ('url',unicode), \
        ('q',int), ('a',int), ('cmd',unicode))

    # read configuration options
    delayTime = int(config['Options']['delayTime'])
    openallure.allowNext = int(config['Options']['allowNext'])

    # initialize chatbot
    openallure_chatbot = Chat(responses, reflections)
    chatHistory = []
    onChatHistory = -1

    # track when Open Allure has gained mouse focus
    openallure.gain = 1
    # mouse focus only matters when stickyBrowser is true (see openallure.cfg)
    openallure.stickBrowser = eval(config['Options']['stickyBrowser'])

    voice = Voice()

    margins = eval(config['Font']['margins'])
    text = OpenAllureText(margins)

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit
    # and resume there on restart
    openallure.onQuestion = 0

    # initialize mode flags
    # Has new question from sequence been prepared?
    openallure.ready = False
    # Has question been openallure.stated (read aloud)?
    openallure.stated = False
    # Which question in sequence has been read aloud (to avoid re-reading it)?
    # Note: -1 indicates no question as valid questions start with 0
    openallure.statedq = -1
    # What choice (if any) has been highlighted by gesture or keyboard?
    highlight = 0
    # When was the statement of the question complete?
    delayStartTime = 0
    # Do we have an answer? what number is it (with 0 being first answer)?
    answer = -1
    # What questions have been shown (list)?
    # Note: This list is also checked to avoid re-stating a question
    openallure.questions = []
    # What has been typed in so far
    openallure.currentString = u""

    # Subprocesses
#    graphViz = None
#    openallure.showResponses = eval(config['GraphViz']['showResponses'])
#    openallure.showText = eval(config['GraphViz']['showText'])
#    openallure.showLabels = eval(config['GraphViz']['showLabels'])
#    graphVizPath = config['GraphViz']['path']
    #if eval(config['GraphViz']['autoStart']):
    #    oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
    #    graphViz = subprocess.Popen([graphVizPath,'oagraph.dot'])

    # Greetings
    #voice.speak('Hello')

    WELCOME_TEXT = ["",
    _(u"       Welcome to the Open Allure Dialog System."),
    "",
    _(u"       Keys:"),
    _(u"           Escape quits"),
    _(u"           Ctrl+I force input"),
    _(u"           Ctrl+R refresh"),
    _(u"           Ctrl+V paste"),
    "",
    _(u"       Commands:"),
    _(u"           exit"),
    _(u"           open <filename or url>"),
    _(u"           quit"),
    _(u"           return (resumes at last question)"),
    _(u"           show source (Mac only)"),
    ""]

    for line in WELCOME_TEXT:
        print line

    runFlag = True;
    while runFlag:

        if not openallure.ready:
            # prepare for question display
            openallure.question = seq.sequence[openallure.onQuestion]
            choiceCount, \
            questionText, \
            justQuestionText = text.buildQuestionText(openallure.question)
#            if graphViz:
#                # Create .dot file for new sequence
#                graphViz.kill()
#                oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
#                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])

            textRegions = text.writewrap(None, text.font, text.boundingRectangle, text.unreadColor, questionText[-1])

            # initialize pointers - no part of the question text
            # and none of the answers have been read aloud.
            # Note that question text is numbered from 0
            # while answers are numbered from 1.
            action = 0
            onAnswer = 0
            onText = 0
            openallure.stated = False
            if openallure.onQuestion in openallure.questions:
                openallure.stated = True

            # initialize selections - nothing has been highlighted
            # or previously selected as an answer
            answer = -1
            choice = (- 1, 0)
            colorLevel = colorLevels = 12
            highlight = 0

            # initialize typed input
            openallure.currentString = u''

            # clear screen of last question
            screen.fill(backgroundColor, rect=textRect)

            # wait for prior speaking to finish
            if voice.pid_status > 0:
                try:
                    os.waitpid(voice.pid_status, 0)[1]
                except:
                    pass
                voice.pid_status = 0
            openallure.ready = True

            # clear any previous response
            nltkResponse = ''

            # start with gain
            openallure.gain = 1

            # arrival record for new question
            record_id = openallure.db.insert(time = time.time(), \
            url = unicode(url), q = openallure.onQuestion)

        # make sure currentString has been added to questionText
        if openallure.currentString:
            questionText[choiceCount] = questionText[choiceCount - 1] + \
                                          "\n" + openallure.currentString

        # get keyboard and mouse input
        mouseButtonDownEvent = False
        mouseButtonDownEventY = 0
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseButtonDownEvent = True
                YCOORDINATE = 1
                mouseButtonDownEventY = event.pos[YCOORDINATE]
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
#               if graphViz:
#                   graphViz.kill()
                runFlag = False

            # Trap and quit on Ctrl + C
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_c and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                return

            # Trap Ctrl + I to force input
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_i and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Note: This kills the entire current sequence.
                # The return command gives a way to back to it.
                seq.inputs = [_(u"Input"),
                         _(u"[input];")]
                seq.sequence = seq.regroup(seq.inputs, \
                               seq.classify(seq.inputs))
                openallure.onQuestion = 0
                url = _(u'[input]')
                # record call to input
                record_id = openallure.db.insert(time = time.time(), \
                            url = unicode(url), q = 0)
                openallure.ready = False

            # Trap and paste clipboard on Ctrl + V for Mac
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_v and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                if sys.platform == 'darwin':
                    os.system('pbpaste > clipboard')
                    clipboard = open('clipboard').readlines()
                    if clipboard[0].startswith(u"http://") or \
                       clipboard[0].find(u"http://"):
                        openallure.currentString += clipboard[0]
                else:
                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clipboard.startswith(u"http://") or \
                       clipboard.find(u"http://"):
                        openallure.currentString += clipboard

            # Trap Ctrl + - (minus) to decrease font size
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_MINUS and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                text.fontSize -= 5
                text.font = pygame.font.SysFont( text.fontName, \
                text.fontSize )

            # Trap Ctrl + + (plus) to increase font size
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_EQUALS and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                text.fontSize += 5
                text.font = pygame.font.SysFont( text.fontName, \
                text.fontSize )

            # Trap Ctrl + R to refresh from url without changing question number
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_r and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                # if url is nltkRespose.txt, look back for something else
                # worth refreshing
                if url == u'nltkResponse.txt':
                    for id in range(record_id - 1,-1,-1):
                        record = openallure.db[id]
                        if not record.url in (url, \
                                              u'nltkResponse.txt', \
                                              _(u'[input]')):
                            url = record.url
                            break
                seq = QSequence(filename = url)
                try:
                    openallure.systemVoice = config['Voice'][seq.language]
                except KeyError:
                    pass
                openallure.ready = False

            # Define toggle keys and capture string inputs
            elif event.type == pygame.KEYDOWN:
                # Keys 1 through 6 select choices 1 through 6
                if event.key in range(pygame.K_1, pygame.K_6) and \
                    (not openallure.question[INPUTFLAG][choiceCount - 1] == 1 or
                    (openallure.question[INPUTFLAG][choiceCount - 1] == 1 and
                    openallure.currentString == u'')):
                        answer = event.key - pygame.K_1
                        if answer < choiceCount:
                            # Record choice along with destination, if any
                            record_id = openallure.db.insert(time = time.time(), \
                            url = unicode(url), q = openallure.onQuestion, \
                            a = answer, cmd = unicode(openallure.question[DESTINATION][answer]))
#                            if graphViz:
#                                graphViz.kill()
#                                oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
#                                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                            choice = (answer + 1, 0)
                            colorLevel = 0
                            # Update screen to reflect choice
                            text.paintText(screen,
                                           justQuestionText, onText,
                                           questionText, onAnswer,
                                           highlight,
                                           openallure.stated,
                                           choice,
                                           colorLevel, colorLevels)
                            pygame.display.flip()
                        else:
                            answer = -1

                elif event.key == pygame.K_F6:
                    # reveal all the attributes of openallure
                    print "\nCurrent values of openallure object variables:\n"
                    for item in openallure.__dict__:
                        print item + ":", openallure.__dict__[item]
                    # drop into interpreter for debugging
                    print "\n   Press Ctrl+D to close console and resume. " + \
                    "Enter exit() to exit.\n"
                    import code
                    code.interact(local=locals())

                # Allow space to silence reading of question
                # unless there is an input (which might require a space)
                elif event.key == pygame.K_SPACE and \
                not openallure.question[INPUTFLAG][choiceCount - 1] == 1:
                    # Silence reading of question
                    openallure.stated = True
                    
                elif event.key == pygame.K_RIGHT and openallure.allowNext:
                    # Choice is first non-zero entry
                    # in openallure.question[ACTION]
                    onChoice = 0
                    for i in openallure.question[ACTION]:
                        onChoice += 1
                        if not i == 0:
                            answer = onChoice - 1
                            record_id = openallure.db.insert(time = time.time(), \
                            url = unicode(url), q = openallure.onQuestion, \
                            a = answer, cmd = unicode(openallure.question[DESTINATION][answer]))
#                            if graphViz:
#                                graphViz.kill()
#                                oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
#                                graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                            choice = (onChoice, 0)
                            break
                    del onChoice

                elif event.key == pygame.K_LEFT:
                    if len(openallure.questions) > 0:
                        openallure.onQuestion = openallure.questions.pop()
                        openallure.ready = False
                    else:
                        openallure.onQuestion = 0

                elif event.key == pygame.K_UP:
                    if len(chatHistory) > 0 and onChatHistory > 0:
                        onChatHistory -= 1
                        openallure.currentString = chatHistory[onChatHistory]
                elif event.key == pygame.K_DOWN:
                    if len(chatHistory) > 0 and \
                    onChatHistory < len(chatHistory) - 1:
                        onChatHistory += 1
                        openallure.currentString = chatHistory[onChatHistory]

                elif event.key == pygame.K_RETURN:
                    if openallure.currentString:
                        # add to history
                        chatHistory.append(openallure.currentString)
                        onChatHistory = len(chatHistory)
                        # record input string
                        record_id = openallure.db.insert(time = time.time(), \
                                    url = unicode(url), q = openallure.onQuestion, \
                                    a = answer, cmd = openallure.currentString)
                        # Check for rules from script at end of question 0
                        if len(seq.sequence[0]) > 9:
                            scriptRules = seq.sequence[0][RULE]
                        else:
                            scriptRules = None
                        nltkResponse, \
                        nltkType, \
                        nltkName = \
                        openallure_chatbot.respond(openallure.currentString, \
                                                   scriptRules)

                        # Act on commands
                        if nltkType == 'goto' or \
                          (nltkType == 'text' and nltkName == 'what now'):
                            # find question with goto tag = ruleName or
                            # currentString (if it didn't match anything else)
                            if openallure.question[QUESTION] == [_(u"Input")]:
                                # Back up to first non-Input, non-Sorry question
                                for id in range(record_id - 1,-1,-1):
                                    try:
                                        record = openallure.db[id]
                                        if not record.url in (url, u'nltkResponse.txt', _(u'[input]')):
                                            seq = QSequence(filename = record.url, \
                                                    path = seq.path, \
                                                    nltkResponse = nltkResponse)
                                            try:
                                                openallure.systemVoice = config['Voice'][seq.language]
                                            except KeyError:
                                                pass
                                            url = record.url
                                            openallure.onQuestion = record.q
                                            openallure.ready = False
                                            break
                                    except:
                                        pass                             
                            tags = [ question[TAG] for question in seq.sequence ]
                            if nltkName in tags:
                                openallure.onQuestion = tags.index(nltkName)
                                openallure.ready = False
                            if nltkName== 'what now' and \
                               openallure.currentString.lower() in tags:
                                if openallure.onQuestion != \
                                        tags.index(openallure.currentString):
                                    openallure.questions.append(openallure.onQuestion) 
                                    openallure.onQuestion = \
                                        tags.index(openallure.currentString)
                                    openallure.ready = False
                            # If still no luck finding a match, use currentString
                            # to search all through the text of all the questions
                            if openallure.ready:
                                for qnum, question in enumerate(seq.sequence):
                                    # search in question text and non-Input answer text
                                    nonInputAnswerText = [answer for answer,input in \
                                                          itertools.izip(question[ANSWER],
                                                                         question[INPUTFLAG]) if not input]
                                    qtext = " ".join(question[QUESTION]) + " " + \
                                            " ".join(nonInputAnswerText)
                                    if qtext.lower().find(openallure.currentString.lower()) > -1:
                                        if openallure.onQuestion != qnum:
                                            openallure.questions.append(openallure.onQuestion)
                                            openallure.onQuestion = qnum
                                            openallure.ready = False
                                            break
                                    

                        if nltkType == 'quit':
                            #TODO: Make this more polite
#                            if graphViz:
#                                graphViz.kill()
                            raise SystemExit

                        if nltkType == 'return':
                            # Find first different sequence in db, walking back
                            for id in range(record_id - 1,-1,-1):
                                try:
                                    record = openallure.db[id]
                                    if not record.url in (url, u'nltkResponse.txt', _(u'[input]')):
                                        seq = QSequence(filename = record.url, \
                                                path = seq.path, \
                                                nltkResponse = nltkResponse)
                                        try:
                                            openallure.systemVoice = config['Voice'][seq.language]
                                        except KeyError:
                                            pass
                                        url = record.url
                                        openallure.onQuestion = record.q
                                        openallure.ready = False
#                                        if graphViz:
#                                            # Fall through into graphing
#                                            nltkType = 'graph'
#                                            nltkName = 'show'
                                        break
                                except:
                                    pass
                            nltkResponse = u''
                            openallure.currentString = u''

                        if nltkType == 'open':
                            # Reset stated question pointer for new sequence
                            openallure.statedq = -1
                            path = seq.path
                            linkStart = nltkResponse.find(u'[')
                            linkEnd = nltkResponse.find(u']', linkStart)
                            url = nltkResponse[linkStart + 1:linkEnd]
                            seq = QSequence(filename = url,
                                            path = path,
                                            nltkResponse = nltkResponse)
                            try:
                                openallure.systemVoice = config['Voice'][seq.language]
                            except KeyError:
                                pass
                            openallure.questions = []
                            openallure.onQuestion = 0
                            openallure.ready = False
#                            if graphViz:
#                                # Fall through into graphing
#                                nltkType = 'graph'
#                                nltkName = 'show'
                            nltkResponse = u''
                            openallure.currentString = u''

                        if nltkType == 'show':
                            # use open (Mac only) to view source
                            if sys.platform == 'darwin':
                                # Find first non-[input] sequence in db, walking back
                                for id in range(record_id - 1,-1,-1):
                                    record = openallure.db[id]
                                    if record.url.find('.txt') > 0 or \
                                       record.url.find('http:') == 0 :
                                        if not record.url == 'nltkResponse.txt':
                                            url = record.url
                                            break
                                os.system("open "+url)

                        # if nltkResponse is one line containing a semicolon,
                        # replace the semicolon with \n
                        if nltkResponse.find('\n') == -1:
                            nltkResponse = nltkResponse.replace(';', '\n')

                        if nltkResponse:
                            answer = choiceCount - 1
                            choice = (choiceCount, 0)
                    else:
                        # This takes last response
                        answer = choiceCount - 1
                        choice = (choiceCount, 0)

                elif event.key == pygame.K_BACKSPACE and \
                openallure.question[INPUTFLAG][choiceCount - 1] == 1:
                    openallure.currentString = openallure.currentString[0:-1]
                    openallure.question[ANSWER][choiceCount - 1] = \
                    openallure.currentString
                    questionText[choiceCount] = \
                    questionText[choiceCount - 1] + \
                    u"\n" + openallure.currentString
                    screen.fill(backgroundColor, rect=textRect)

                elif event.key <= 127 and \
                openallure.question[INPUTFLAG][-1] == 1:
                    # p rint event.key
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        if event.key in range(47, 60):
                            openallure.currentString += \
                            (u'?', u')', u'!', u'@', u'#', u'$', u'%', u'^', \
                            u'&', u'*', u'(', u'', u':')[range(47, 60).index(event.key)]
                        elif event.key == 45:
                            openallure.currentString += u"_"
                        elif event.key == 61:
                            openallure.currentString += u"+"
                        elif event.key == 96:
                            openallure.currentString += u"~"
                        else:
                            openallure.currentString += \
                                unicode(chr(event.key).upper())
                    else:
                        openallure.currentString += unicode(chr(event.key))
#                    openallure.question[ANSWER][choiceCount - 1] = \
#                        openallure.currentString
                    # Add currentString to text being displayed
                    questionText[choiceCount] = \
                        questionText[choiceCount - 1] + \
                        u"\n" + openallure.currentString
                    screen.fill(backgroundColor, rect=textRect)

        # check for automatic page turn
        if openallure.ready and \
           openallure.stated == True and \
           not openallure.currentString and \
           openallure.question[ANSWER][-1] == _(u'[next]') and \
           pygame.time.get_ticks() - delayStartTime > delayTime:
            # This takes last response
            answer = choiceCount - 1
            choice = (choiceCount, 0)

        if openallure.statedq == openallure.onQuestion:
            openallure.stated = True

        if openallure.ready and not openallure.stated:
            # work through statement of question
            # speaking each part of the question and each of the answers
            # (unless the process is cut short by other events)
            if onText == 0:
                screen.fill(backgroundColor, rect=textRect)
                pygame.display.flip()

            # Stop when onAnswer pointer is beyond length of answer list
            if onAnswer > len(openallure.question[ANSWER]):
                openallure.stated = True
                openallure.statedq = openallure.onQuestion

            else:
                # Speak each answer
                #(but only after speaking the full question below)
                if onAnswer > 0 and onAnswer < len(openallure.question[ANSWER]) + 1:
                    answerText = openallure.question[ANSWER][onAnswer - 1]
                    if not (answerText.startswith(_('[input]')) or
                             answerText.startswith(_('[next]')) or
                             answerText.endswith( '...]' ) or
                             answerText.endswith( '...' )):
                        if len(answerText) > 0:
                            # Check for answer with "A. "
                            if answerText[1:3] == '. ':
                                voice.speak(answerText[3:].strip(),openallure.systemVoice)
                            else:
                                voice.speak(answerText.strip(),openallure.systemVoice)
                        del answerText

                # Speak each part of the question using onText pointer
                # to step through parts of question list
                if onText < len(openallure.question[QUESTION]):
                    if not (openallure.question[QUESTION][onText].endswith( '...' )):
                        if len(openallure.question[QUESTION][onText]) > 0:
                            # speak the current part of the question
                            voice.speak(openallure.question[QUESTION][onText],openallure.systemVoice)

        if answer < 0 and openallure.ready:

            # Trap mouse click on text region
            textRegions = text.writewrap(None, \
                                         text.font, \
                                         text.boundingRectangle, \
                                         text.unreadColor, \
                                         questionText[-1])

            # Create list where each element indicates with 1 or 0
            # whether Y coordinate is in the region
            regions = [inRegion(region, mouseButtonDownEventY) for region in textRegions]

            # Find which region has a 1, if any
            if 1 in regions:
                onRegion = regions.index(1)
            else:
                onRegion = 0

            if onRegion > 0:
                if mouseButtonDownEvent:
                    answer = onRegion - 1
                    if answer < choiceCount:
                        # record selection of answer
                        record_id = openallure.db.insert(time = time.time(), \
                        url = unicode(url), q = openallure.onQuestion, \
                        a = answer)
#                        if graphViz and openallure.question[ACTION][answer] == 0:
#                            # Create .dot file for one sequence in response to answer in place
#                            graphViz.kill()
#                            oagraph(seq,openallure.db,url,openallure.showText,openallure.showResponses,openallure.showLabels)
#                            graphViz = subprocess.Popen([graphVizPath, 'oagraph.dot'])
                        choice = (answer + 1, 0)
                        colorLevel = 0
                        # Update screen to reflect choice
#                         text.paintText(screen,
#                                        justQuestionText, onText,
#                                        questionText, onAnswer,
#                                        highlight,
#                                        openallure.stated,
#                                        choice,
#                                        colorLevel, colorLevels)
#                         pygame.display.flip()
                    else:
                        answer = -1
                else:
                    highlight = onRegion
                    # Update screen to reflect highlight
#                     text.paintText(screen,
#                                    justQuestionText, onText,
#                                    questionText, onAnswer,
#                                    highlight,
#                                    openallure.stated,
#                                    choice,
#                                    colorLevel, colorLevels)
#                     pygame.display.flip()
                    colorLevel -= 1
                    colorLevel = max(colorLevel, 0)
            else:
                highlight = 0
                colorLevel = colorLevels

            # block non-choices
            if choice[0] < 0 or choice[0] > len(questionText) - 1:
                choice = (-1, 0)

            screen.fill(backgroundColor, rect=textRect)
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText, onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel, colorLevels)
            # and move on to the next part
            # (which needs to be displayed while being spoken)
            onText += 1
            # once all the parts of the question are done,
            # start working through answers
            if onAnswer > 0:
                onAnswer += 1
            if onText == len(openallure.question[QUESTION]):
                onAnswer = 1
                # Take note of time for automatic page turns
                delayStartTime = pygame.time.get_ticks()

            pygame.display.flip()

        elif not choice == (- 1, 0) and openallure.ready:

            openallure.stated = True

            # respond to choice when something has been typed and entered
            if openallure.currentString:
                if len(nltkResponse) == 0:
                    choice = (-1, 0)
                    answer = -1
                    voice.speak(_("Try again"),openallure.systemVoice)
                else:
                    voice.speak(_(u"You entered ") + openallure.currentString,openallure.systemVoice)
                # Reset string
                openallure.currentString = u''

            # check whether a link is associated with this answer and,
            # if so, follow it
            if len(openallure.question[LINK]) and openallure.question[LINK][answer]:
                webbrowser.open_new_tab(openallure.question[LINK][answer])
                # wait in loop until window (re)gains focus
                if openallure.stickBrowser:
                    openallure.gain = 0
                    while not openallure.gain:
                        for event in pygame.event.get():
                            if event.type == pygame.ACTIVEEVENT:
                                openallure.gain = event.gain

            #check that response exists for answer
            if len(openallure.question[RESPONSE]) and \
               answer < len(openallure.question[RESPONSE]) and \
                (isinstance(openallure.question[RESPONSE][answer], str) or \
                isinstance(openallure.question[RESPONSE][answer], unicode)):
                    #speak response to answer
                    voice.speak(openallure.question[RESPONSE][answer].strip(),openallure.systemVoice)

            #check that next sequence exists as integer for answer
            if len(openallure.question[ACTION]) and \
            answer < len(openallure.question[ACTION]) and \
            isinstance(openallure.question[ACTION][answer], int):
                #get new sequence or advance in sequence
                action = openallure.question[ACTION][answer]
                if len(openallure.question[DESTINATION][answer]) > 0 and \
                not openallure.question[ANSWER][answer] == _(u'[next]'):
                    # speak("New source of questions")
                    # Reset stated question pointer for new sequence
                    openallure.statedq = -1
                    path = seq.path
                    url = openallure.question[DESTINATION][answer]
                    seq = QSequence(filename = url,
                                    path = path,
                                    nltkResponse = nltkResponse)
                    try:
                        openallure.systemVoice = config['Voice'][seq.language]
                    except KeyError:
                        pass
                    openallure.onQuestion = 0
                    openallure.questions = []
                else:
                    # Add last question to stack (if not duplicate) and move on
                    if action > 0:
                        openallure.questions.append(openallure.onQuestion)
                        openallure.onQuestion = openallure.onQuestion + action

                    elif action < 0:
                        openallure.onQuestion = max( 0, openallure.onQuestion + action )

                    # Quit if advance goes beyond end of sequence
                    if openallure.onQuestion >= len(seq.sequence):
                        voice.speak(_("You have reached the end. Goodbye."),openallure.systemVoice)
                        return

                openallure.ready = False

if __name__ == '__main__':
    main()
