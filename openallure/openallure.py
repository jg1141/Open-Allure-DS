"""
openallure.py

Voice-and-vision enabled dialog system

Project home at `Open Allure project`_.

.. _Open Allure project: http://openallureds.org

Copyright (c) 2010 John Graves

MIT License: see LICENSE.txt
"""

__version__='0.1d16dev'

# Standard Python modules
import ConfigParser
import logging
import os
import random
import re
import string
import sys

# 3rd Party modules
# note: nltk is used by chat.py
import pygame

# Import from Open Allure DS modules
from gesture import Gesture
from qsequence import QSequence
from text import OpenAllureText
from video import VideoCapturePlayer, GreenScreen
from voice import Voice
from chat import Chat

# Setup logging
logging.basicConfig( level=logging.DEBUG )

WELCOME_TEXT = """
   Welcome to Open Allure, a voice-and-vision enabled dialog system.

   F4 to recalibrate green screen.
   Escape to quit.

   Enjoy!
"""


class OpenAllure(object):
    def __init__(self):
        self.__version__ = __version__
        self.voiceChoice = -1
        self.question = []
        self.ready = False
        self.stated = False
        self.currentString = ''
        #bring in photo file names
        config = ConfigParser.RawConfigParser()
        config.read( 'openallure.cfg' )
        self.photos = [ config.get( 'Photos', 'smile' ) ,
                        config.get( 'Photos', 'talk' ) ,
                        config.get( 'Photos', 'listen' ) ]


openallure = OpenAllure()

from responses import *

def main():
    """Initialization and event loop"""

    # provide instructions and other useful information (hide by elevating logging level:
    logging.info( "Open Allure Version: %s" % __version__ )
    logging.debug( "Pygame Version: %s" % pygame.__version__ )

    # initialize pyGame screen
    textRect = pygame.rect.Rect( 0, 0, 640, 480 )
    screenRect = pygame.rect.Rect( 0, 0, 752, 600 )
    pygame.init()
    screen = pygame.display.set_mode( screenRect.size )

    # load initial question sequence from url specified in openallure.cfg file
    config = ConfigParser.RawConfigParser()
    config.read( 'openallure.cfg' )
    url = config.get( 'Source', 'url' )
    backgroundColor = eval( config.get( 'Colors', 'background' ) )
    seq = QSequence( filename=url )

    # initial url may override photos
    if seq.sequence[0][7]:
        logging.info( "Taking photo names from %s" % url )
        openallure.photos = seq.sequence[0][7]

    logging.info( "Question sequence Loaded with %s questions" % str( len( seq.sequence ) ) )
    #print seq.sequence

    # read configuration options
    delayTime = int( config.get( 'Options', 'delayTime' ) )
    openallure.allowNext = int( config.get( 'Options', 'allowNext' ) )

    # initialize chatbot
    openallure_chatbot = Chat(responses, reflections)
    logging.info( "Chatbot initialized" )

    # load browser command line strings and select appropriate one
    darwinBrowser = config.get( 'Browser', 'darwinBrowser' )
    windowsBrowser = config.get( 'Browser', 'windowsBrowser' )
    if sys.platform == 'darwin':
        browser = darwinBrowser
    else:
        browser = windowsBrowser

    greenScreen = GreenScreen()
    vcp         = VideoCapturePlayer( processFunction=greenScreen.process,
                                      photos=openallure.photos,
                                      version=openallure.__version__ )
    gesture     = Gesture()
    voice       = Voice()

    margins     = eval( config.get( 'Font', 'margins' ) )
    text        = OpenAllureText( margins )

    # start on first question of sequence
    # TODO: have parameter file track position in sequence at quit and resume there on restart
    openallure.onQuestion = 0

    # initialize mode flags
    # Has new question from sequence been prepared?
    openallure.ready = False
    # Has question been openallure.stated (read aloud)?
    openallure.stated = False
    # What choice (if any) has been highlighted by gesture or keyboard?
    highlight= 0
    # When was choice first highlighted by gesture?
    choiceStartTime = 0
    # When was the statement of the question complete?
    delayStartTime = 0
    # How much of highlight color should be blended with selected color? in how many steps? with how much time (in ticks) per step?
    colorLevel = colorLevels = 12
    colorLevelStepTime = 100
    # Do we have an answer? what number is it (with 0 being first answer)?
    answer = -1
    # What questions have been shown (list)?
    openallure.questions = []
    # What has been typed in so far
    openallure.currentString = ""


    # Greetings
    vcp.talk()
    voice.speak( 'Hello' )
    vcp.smile()

    print WELCOME_TEXT

    while True:

        if not openallure.ready:
            # prepare for question display
            openallure.question = seq.sequence[ openallure.onQuestion ]
            choiceCount, questionText, justQuestionText = text.buildQuestionText( openallure.question )

            textRegions = text.preRender( questionText[ choiceCount ] )

            # initialize pointers - no part of the question text and none of the answers
            # have been read aloud.  Note that question text is numbered from 0
            # while answers are numbered from 1.
            openallure.stated = False
            onText = 0
            onAnswer = 0
            next = 0

            # initialize selections - nothing has been highlighted or previously
            # selected as an answer
            highlight = 0
            colorLevel = colorLevels
            choice = ( - 1, 0 )
            answer = -1
            eliminate = []

            # initialize typed input
            openallure.currentString = ''

            # clear screen of last question
            screen.fill( backgroundColor, rect=textRect )
            greenScreen.calibrated = False
            greenScreen.backgrounds = []
            vcp.processruns = 0
            openallure.ready = True

            # clear any previous response
            nltkResponse = ''

        # check for automatic page turn
        if openallure.stated == True and \
           not openallure.currentString and \
           openallure.question[ 1 ][ choiceCount - 1 ] == u'[next]' and \
           pygame.time.get_ticks() - delayStartTime > delayTime:
            # This takes last response
            answer = choiceCount - 1
            choice = ( choiceCount, 0 )

        # make sure currentString has been added to questionText
        # as new contents may have been added by voice
        if openallure.currentString:
            questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + \
                                          "\n" + openallure.currentString

        # get keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
                return

            # Trap and quit on Ctrl + C
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_c and
                  pygame.key.get_mods() & pygame.KMOD_CTRL):
                return

            # Define toggle keys and capture character by character string inputs
            elif event.type == pygame.KEYDOWN:
               # Keys 1 through 6 select choices 1 through 6
               if event.key in range( pygame.K_1, pygame.K_6 ) and \
                  (not openallure.question[ 6 ][ choiceCount - 1 ] == 1 or
                  (openallure.question[ 6 ][ choiceCount - 1 ] == 1 and
                  openallure.currentString == '' ) ):
                   answer = event.key - pygame.K_1
                   if answer < choiceCount:
                       choice = ( answer + 1, 0 )
                       colorLevel = 0
                       # Update screen to reflect choice
                       text.paintText(screen,
                                      justQuestionText, onText,
                                      questionText,     onAnswer,
                                      highlight,
                                      openallure.stated,
                                      choice,
                                      colorLevel,colorLevels)
                       pygame.display.flip()
                   else:
                       answer = -1

               elif event.key == pygame.K_F4:
                    greenScreen.calibrated = False
               elif event.key == pygame.K_F6:
                    # reveal all the attributes of openallure
                    print( openallure.__dict__ )
                    # drop into interpreter for debugging
                    import code; code.interact(local=locals())

               # Allow space to silence reading of question unless there is an input (which might require a space)
               elif event.key == pygame.K_SPACE and not openallure.question[ 6 ][choiceCount - 1 ] == 1:
                    # Silence reading of question
                    openallure.stated = True
               elif event.key == pygame.K_RIGHT and openallure.allowNext:
                              # Choice is first non-zero entry in openallure.question[3]
                              onChoice = 0
                              for i in openallure.question[3]:
                                  onChoice += 1
                                  if not i == 0:
                                      openallure.voiceChoice = onChoice
                                      break
                              del onChoice

               elif event.key == pygame.K_LEFT:
                              if len(openallure.questions) > 0:
                                  openallure.onQuestion = openallure.questions.pop()
                                  openallure.ready = False
                              else:
                                  openallure.onQuestion = 0
               elif event.key == pygame.K_RETURN:
                   if openallure.currentString:
                          nltkResponse = openallure_chatbot.respond( openallure.currentString )
                          # print openallure.currentString
                          # print nltkResponse

                          # if nltkResponse is one line containing a semicolon, replace the semicolon with \n
                          if nltkResponse.find('\n') == -1:
                              nltkResponse = nltkResponse.replace(';','\n')

                          if nltkResponse:
                              answer = choiceCount - 1
                              choice = ( choiceCount, 0 )
                   else:
                       # This takes last response
                       answer = choiceCount - 1
                       choice = ( choiceCount, 0 )
               elif event.key == pygame.K_BACKSPACE and openallure.question[ 6 ][choiceCount - 1 ] == 1:
                   openallure.currentString = openallure.currentString[0:-1]
                   openallure.question[ 1 ][ choiceCount - 1 ] = openallure.currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + "\n" + openallure.currentString
                   screen.fill( backgroundColor, rect=textRect)
               elif event.key <= 127 and openallure.question[ 6 ][choiceCount - 1 ] == 1:
##                   print event.key
                   mods = pygame.key.get_mods()
                   if mods & pygame.KMOD_SHIFT:
                       if event.key in range( 47, 60 ):
                           openallure.currentString += \
                           ('?',')','!','@','#','$','%','^','&','*','(','',':'
                           )[range( 47, 60 ).index( event.key )]
                       elif event.key == 45:
                           openallure.currentString += "_"
                       elif event.key == 61:
                           openallure.currentString += "+"
                       else:
                           openallure.currentString += chr( event.key ).upper()
                   else:
                       openallure.currentString += chr( event.key )
                   openallure.question[ 1 ][ choiceCount - 1 ] = openallure.currentString
                   questionText[ choiceCount ] = questionText[ choiceCount - 1 ] + \
                                                 "\n" + openallure.currentString
                   screen.fill( backgroundColor, rect=textRect)

        if openallure.voiceChoice > 0:
            openallure.stated = 1
            choice = ( openallure.voiceChoice, 0 )
            # block non-choices
            if choice[ 0 ] < 0 or choice[ 0 ] > len( questionText ) - 1 :
                choice = ( -1, 0 )
            else:
                answer = openallure.voiceChoice - 1
                colorLevel = 0
                openallure.voiceChoice = 0
                # Update screen to reflect choice
                text.paintText(screen,
                               justQuestionText, onText,
                               questionText,     onAnswer,
                               highlight,
                               openallure.stated,
                               choice,
                               colorLevel,colorLevels)
                pygame.display.flip()

#        print openallure.voiceChoice
        if openallure.voiceChoice > 0:
            openallure.stated = 1
            answer = openallure.voiceChoice - 1
            colorLevel = 0
            openallure.voiceChoice = 0
            # Update screen to reflect choice
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText,     onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel,colorLevels)
            pygame.display.flip()


        if answer < 0 and openallure.ready:
            # check webcam
            processedImage = vcp.get_and_flip()

            # show a photo
            if isinstance( vcp.photoSmile,pygame.Surface ) and \
              openallure.currentString == '' and openallure.stated == 1:
               vcp.display.blit( vcp.photoSmile, (650,10))

            if isinstance( vcp.photoTalk,pygame.Surface ) and \
              openallure.currentString == '' and openallure.stated == 0:
               vcp.display.blit( vcp.photoTalk, (650,10))

            if isinstance( vcp.photoListen,pygame.Surface ) and \
              not openallure.currentString == '':
               vcp.display.blit( vcp.photoListen, (650,10))

            # show the raw input
            if isinstance( vcp.snapshotThumbnail,pygame.Surface ):
                vcp.display.blit( vcp.snapshotThumbnail, (10,480) )

            # show the green screen
            if isinstance( vcp.processedShotThumbnail,pygame.Surface ):
                vcp.display.blit( vcp.processedShotThumbnail, (190,480) )

            # obtain choice from processed snapshot
            if isinstance( processedImage,pygame.Surface ):
                choice = gesture.choiceSelected( processedImage, textRegions, margins )
##                if choice[0]> 0:
##                    print choice

            # show selected boxes
            if isinstance( gesture.scaledImageWithPixels,pygame.Surface ):
                vcp.display.blit( gesture.scaledImageWithPixels, (370,480) )

            pygame.display.flip()

            # block non-choices
            if choice[ 0 ] < 0 or choice[ 0 ] > len( questionText ) - 1 :
                choice = ( -1, 0 )
            #print choice, highlight

            # adjust highlight and colorLevel
            if highlight > 0 and highlight == choice[ 0 ]:
                # choice was previously highlighted. Find out how long.
                dwellTime = pygame.time.get_ticks() - choiceStartTime
                #if choice[0] > 0: print choice, highlight, colorLevel, dwellTime
                # print dwellTime
                # lower color level to 0
                colorLevel = colorLevels - int( dwellTime / colorLevelStepTime )
                colorLevel = max( 0, colorLevel )
                #TODO: provide shortcut to go immediately to colorLevel=0
                #if choice[1] (number of selected boxes) is big enough
                if colorLevel == 0:
                    # choice has been highlighted long enough to actually be the desired selection
                    choiceMade = True
                    answer = choice[ 0 ] - 1
    ##                print openallure.question[1]
    ##                print choice[0]
                    voice.speak( "You selected " + openallure.question[ 1 ][ answer ] )
                    highlight = 0
                else:
                    # block a choice that has not been highlighted long enough
                    choice = ( -1, 0 )
            else:
                # new choice or no choice
                highlight      = min( choice[ 0 ], choiceCount )
                if highlight < 0:
                    highlight = 0
                    colorLevel = colorLevels
                else:
                    choiceStartTime = pygame.time.get_ticks()

            screen.fill( backgroundColor, rect=textRect )
            text.paintText(screen,
                           justQuestionText, onText,
                           questionText,     onAnswer,
                           highlight,
                           openallure.stated,
                           choice,
                           colorLevel,colorLevels)

        elif not choice == ( - 1, 0 ):

            openallure.stated = True

            # respond to choice when something has been typed and entered
            if openallure.currentString:
                if len( nltkResponse ) == 0:
                    choice = ( -1, 0 )
                    answer = -1
                    voice.speak("Try again")
                else:
                    voice.speak("You entered " + openallure.currentString )
                # Reset string
                openallure.currentString = ''

            # check whether a link is associated with this answer and, if so, follow it
            if len( openallure.question[ 5 ] ) and openallure.question[ 5 ][ answer ]:
                os.system( browser + " " + openallure.question[ 5 ][ answer ] )

            #check that response exists for answer
            if len( openallure.question[ 2 ] ) and \
               answer < len( openallure.question[ 2 ] ) and \
                (isinstance( openallure.question[ 2 ][ answer ], str ) or \
                 isinstance( openallure.question[ 2 ][ answer ], unicode ) ):
                  #speak response to answer
                  voice.speak(openallure.question[ 2 ][ answer ].strip())

            #check that next sequence exists as integer for answer
            if len( openallure.question[ 3 ] ) and \
               answer < len( openallure.question[ 3 ] ) and \
                 isinstance( openallure.question[ 3 ][ answer ], int ):
              #get new sequence or advance in sequence
              next = openallure.question[ 3 ][ answer ]
              if not openallure.question[ 4 ][ answer ] == '' and \
                 not openallure.question[ 1 ][ answer ] == u'[next]':
                  # speak( "New source of questions" )
                  path = seq.path
                  #print "path is ", path
                  seq = QSequence( filename = openallure.question[ 4 ][ answer ],
                                   path = path,
                                   nltkResponse = nltkResponse )
        		  #bring in (potentially new) photos
                  if seq.sequence[0][7]:
                      logging.info( "Using new photo names" )
                      vcp.photoSmile = pygame.image.load( seq.sequence[0][7][0] ).convert()
                      vcp.photoTalk = pygame.image.load( seq.sequence[0][7][1] ).convert()
                      vcp.photoListen = pygame.image.load( seq.sequence[0][7][2] ).convert()
                  openallure.onQuestion = 0
                  openallure.ready = False
              elif next == 99:
                  voice.speak( "Taking dictation" )
                  #TODO
              else:
                  # Add last question to stack (if not duplicate) and move on
                  if next > 0:
                     if len( openallure.questions ) and \
                        not openallure.questions[-1] == openallure.onQuestion:
                         openallure.questions.append( openallure.onQuestion )
                     else:
                         openallure.questions.append( openallure.onQuestion )

                     openallure.onQuestion = openallure.onQuestion + next

                  # Try to pop question off stack if moving back
                  elif next < 0:
                    for i in range( 1, 1 - next ):
                           if len( openallure.questions ) > 0:
                               openallure.onQuestion = openallure.questions.pop()
                           else:
                               openallure.onQuestion = 0

                  # Quit if advance goes beyond end of sequence
                  if openallure.onQuestion >= len( seq.sequence ):
                      voice.speak( "You have reached the end. Goodbye." )
                      return
                  else:
                      openallure.ready  = False

##            else:
##               # invalid or final choice
##               print "Something is wrong with the question sequence.  Please check it:"
##               print seq.sequence
##               return

        if not openallure.stated:
            # work through statement of question
            # speaking each part of the question and each of the answers
            # (unless the process is cut short by other events)

            # Stop when onAnswer pointer is beyond length of answer list
            if onAnswer > len(openallure.question[1]):
                openallure.stated = True
            else:
                # Speak each answer (but only after speaking the full question below)
                if onAnswer > 0 and onAnswer < len( openallure.question[ 1 ] ) + 1 :
                    answerText = openallure.question[ 1 ][ onAnswer-1 ]
                    if not ( answerText.startswith( '[input]' ) or
                             answerText.startswith( '[next]' ) ):
                        # Check for answer with "A. "
                        if answerText[ 1:3 ] == '. ' :
                           voice.speak( answerText[ 3: ].strip() )
                        else:
                           voice.speak( answerText.strip() )
                        del answerText
                    onAnswer += 1

                # Speak each part of the question using onText pointer
                # to step through parts of question list
                if onText < len( openallure.question[ 0 ] ):
                    # speak the current part of the question
                    voice.speak( openallure.question[ 0 ][ onText ] )
                    # and move on to the next part
                    # (which needs to be displayed before being spoken)
                    onText += 1
                    # once all the parts of the question are done,
                    # start working through answers
                    if onText == len( openallure.question[ 0 ] ):
                       onAnswer = 1
                       # Take note of time for automatic page turns
                       delayStartTime = pygame.time.get_ticks()

# initialize speech recognition before entering main()
config = ConfigParser.RawConfigParser()
config.read( 'openallure.cfg' )
useDragonfly = eval( config.get( 'Voice', 'useDragonfly' ) )
useEspeak    = eval( config.get( 'Voice', 'useEspeak' ) )

_dictation = 0

openallure.voiceChoice = 0

def speak(phrase):
   #print phrase
   if useDragonfly:
	   e = dragonfly.get_engine()
	   e.speak(phrase)
   if useEspeak:
       os.system('espeak -s150 "' + phrase + '"')
   if not (useDragonfly or useEspeak):
       print phrase
       pygame.time.wait(500)

if useDragonfly:
    import dragonfly
    from dragonfly import *

    e = dragonfly.get_engine()
    e.speak("Using dragonfly.")

    grammar = Grammar("openallure")

    class SpeakRule(CompoundRule):
        spec = "<text>"
        extras = [Dictation("text")]

        def _process_recognition(self, node, extras):
##            # stop reading
##            global _silence, choice, _dictation, on_question, question, sequence, _openallure.stated, _quit
##            _silence = 1

            openallure.stated = True

            if openallure.ready:
                # repeat voice recognition
                answer = " ".join(node.words())
                answer1 = node.words()[0]
                speak("You said %s!" % answer)

                if _dictation == 0:
                    # check for valid answer (see if words match)
                    onAnswer = 0
                    match = 0
                    for i in openallure.question[1]:
                        onAnswer += 1
                        #check against available answers - in lower case without punctuation
                        # and allow first part only (eg "Yes." in "Yes. I agree.")
                        # or first word
                        # or last word
                        # or [LINK] version of answer
                        answer = answer.lower().strip('.')
                        # length of i must be tested because it could be blank
                        # after [input] is deleted
                        if len(answer) and len(i) and \
                           ( answer == i.lower().strip('.?!') or
                             answer == i.lower().split('.')[0] or
                             answer == i.lower().split()[0] or
                             answer == i.lower().split()[-1] or
                             "["+answer+"]" == i.lower() ):
                           openallure.voiceChoice = onAnswer
                           match = 1
                    if not match:
                        #check first word against number words
                        onAnswer = 0
                        for i in ["one","two","three","four","five","six"]:
                            onAnswer += 1
                            if answer1 == i or answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against "choice" + number words
                        onAnswer = 0
                        for i in ["choice one","choice two","choice three","choice four","choice five","choice six"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against "answer" + number words
                        onAnswer = 0
                        for i in ["answer one","answer two","answer three","answer four","answer five","answer six"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check first word against words similar to number words
                        onAnswer = 0
                        for i in ["won","to","tree","for","fife","sex"]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words
                        onAnswer = 0
                        for i in ["first","second","third","fourth","fifth","sixth"]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words + "choice"
                        onAnswer = 0
                        for i in ["first choice","second choice","third choice","fourth choice","fifth choice","sixth choice"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against ordinal words + "answer"
                        onAnswer = 0
                        for i in ["first answer","second answer","third answer","fourth answer","fifth answer","sixth answer"]:
                            onAnswer += 1
                            if answer == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match:
                        #check against letter words
                        onAnswer = 0
                        for i in ["A.","B.","C.","D.","E.","F."]:
                            onAnswer += 1
                            if answer1 == i:
                               openallure.voiceChoice = onAnswer
                               match = 1
                    if not match and openallure.allowNext:
                        #check against control words
                        for i in ["next","next question","skip to next question"]:
                           if answer == i:
                              skipResponse = 1

                              # Choice is first non-zero entry in openallure.question[3]
                              onChoice = 0
                              for i in openallure.question[3]:
                                  onChoice += 1
                                  if not i == 0:
                                      openallure.voiceChoice = onChoice
                                      break
                              del onChoice
                              match = 1
                    if not match:
                        for i in ["back","prior","previous","back up","back one",
                                  "prior question","previous question"]:
                           if answer == i:
                              openallure.voiceChoice = -1
                              if len(openallure.questions) > 0:
                                  openallure.onQuestion = openallure.questions.pop()
                                  openallure.ready = False
                              else:
                                  openallure.onQuestion = 0
                              match = 1
                    if not match:
                        for i in ["quit now","exit now","i give up"]:
                           if answer == i:
                               pygame.QUIT = 1
                               match = 1

                    if not match:
                        # Voice recognition can make mistakes but still get
                        # some words correct to make a match
                        # Check if any answers have the correct NUMBER of words
                        # and at least one matching word
                        answerWordCount = len( node.words() )
                        onAnswer = 0
                        for i in openallure.question[1]:
                            onAnswer += 1
                            choiceWordCount = len( i.split() )
                            if answerWordCount == choiceWordCount:
                                choiceWords = i.lower().split()
                                while choiceWordCount:
                                    choiceWordCount -= 1
                                    #print choiceWords[choiceWordCount], node.words()
                                    if choiceWords[choiceWordCount] in node.words():
                                        openallure.voiceChoice = onAnswer
                                        match = 1
                                        choiceWordCount = 0
                            if match:
                                break

                    if match:
                        openallure.currentString = ''

                    if not match and not openallure.currentString:
                        if openallure.question[ 1 ][ - 1 ] == u"[input]" or \
                           openallure.question[ 1 ][ - 1 ] == u"":
                            # try plugging into currentString
                            openallure.currentString = answer
                            openallure.question[ 1 ][ - 1 ] = openallure.currentString
                            match = 1


##                        speak("Try again.")
    ##            else:
    ##                voice.speak("Thank you. Let's move on.")
    ##                on_question = on_question + 1
    ##                # avoid stepping past end of sequence
    ##                on_question = min(on_question,len(sequence)-1)
    ##                openallure.question = sequence[on_question]
    ##                build_question_text(openallure.question)
    ##                openallure.voiceChoice = 0
    ##                _dictation = 0
    ##            if match and verbose: print "dragonfly openallure.voiceChoice " + str(openallure.voiceChoice)
    ##                e.speak("dragonfly voice Choice " + str(openallure.voiceChoice))

    grammar.add_rule(SpeakRule())    # Add the top-level rule.
    grammar.load()                   # Load the grammar.



if __name__ == '__main__':
    main()
