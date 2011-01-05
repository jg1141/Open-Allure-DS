"""
qsequence.py
a component of openallure.py

Parses separate content file into question sequence object

**Usage**

QSequence( *filename* ) returns a question sequence object

*filename* can be either a local file or a URL containing preformatted text

An input file is a plain text file with the format::

   [ tag ]
   [ configuration overrides ]
   Question part1
   { optional Question part2 }
   { optional blank line }
   Answer 1 <separator> Response 1
   Answer 2 <separator> Response 2
    etc ...
   up to 6 answers
   { blank line }
   Next question ...

where configuration overrides can be::

   smile            image to use for smiling avatar
   talk             image to use for talking avatar
   listen           image to use for listening avatar

where Answer can be::

   [link label]     to open link in separate browser when label is selected
   [input]          to enable user input
   [next]           to enable user input, but only until an automatic "page turn"

where <separator> can be::

   ;                no action
   ;; or ;1 or ;+1  advance to next question
   ;-1              return to prior question ( in order exposed in sequence )
   ;;; or ;2 or ;+2 advance two questions
   ;[tag]           advance to question marked with tag
   ;[filename]      advance to first question found in filename
   ;[url]           advance to first question found in text marked <pre> </pre> at URL (webpage)

In addition, an input file can specify string matching rules of the form::

   [type of rule]
   [[name of rule]]
   re=
   example=
   reply=

where::

   #     [Section: type of rule]
   #        The type of rule determines which block of code in chat.py
   #        will be used to process the parsed string.  All the rules of
   #        a given type can be listed in a section.
   #
   #     [[Sub-section: name of rule]]
   #         Each rule should have a unique name.  This name can be
   #         posted to the log so it can be worked out which rule fired
   #         and led to the observed behaviour of Open Allure.
   #
   #     example =
   #         (optional)
   #         NOTE: If left out, there must be a regular expression (below)
   #         Example question from which Open Allure derives a regular expression.
   #         Strings which must be matched are enclosed in brackets.
   #         For instance,
   #
   #         example = "Who is alan [turing]?"
   #
   #         should be converted to the regular expression
   #
   #         re = '(.*)(turing)(.*)'
   #
   #         which would lead to matches on all sorts of inputs, including
   #         "Tell me about Turing."
   #         "What is the Turing Test?"
   #         "Was Turing gay?"
   #
   #         This brings up the issue of rule ORDER.
   #         More specific matches need to come first, so if you want
   #         something special in response to
   #         "What is the [Turing Test]?"
   #         that rule must come BEFORE the response to
   #         "Who is Alan [Turing]?"
   #         or else the Turing Test rule will never fire.
   #
   #     re =
   #         (optional)
   #         NOTE: If an example (above) exists, this overrides it.
   #         Regular expression used to match against input string
   #         For instance,
   #
   #         re = '(.*)(turing|loebner)(.*)'
   #
   #         where the vertical bar indicates OR
   #
   #     reply =
   #         Reply from Open Allure
   #         Triple quoted strings allow for multi-line scripts here.
   #
   #         In other words, the reply can include an entire
   #         question sequence, not merely a direct answer.
   #
   #         Open Allure stands out from other chatbots with this capability.
   #         Scripts allow Open Allure to take some of the initiative and
   #         guide the conversation in a particular direction or offer alternatives.
   #

See `Open Allure wiki Rule File Syntax`_ for details and examples.

.. _Open Allure wiki Rule File Syntax: http://code.google.com/p/open-allure-ds/wiki/RuleFileSyntax


**Output**

List of lists::

   #   [   The whole sequence of questions is outermost list,
   #                             so seq[ 0 ] is everything about the first question
   #    [  The parts of the a question including the question set, answer set, response set and action/destination sets are the next level list,
   #                             so seq[ ][ 0 ] is the question set
   #                                seq[ ][ 1 ] is the answer set
   #                                seq[ ][ 2 ] is the response set
   #                                seq[ ][ 3 ] is the action set
   #                                seq[ ][ 4 ] is the action set destinations (Response-side filenames or URLs for new questions)
   #                                seq[ ][ 5 ] is the links set (Answer-side filenames or URLs to open in browser)
   #                                seq[ ][ 6 ] is the input set
   #     [ The parts of the question are the next level list,
   #                             so seq[ ][ 0 ][ 0 ] is the first part of the question, for example "What color"
   #                            and seq[ ][ 0 ][ 1 ] is the next  part of the question, for example "is the sky?" ],
   #     [ The answers are the next list,
   #                             so seq[ ][ 1 ][ 0 ] is the first  answer, for example "Black"
   #                            and seq[ ][ 1 ][ 1 ] is the second answer, for example "Blue" ],
   #     [ The response are the next list,
   #                             so seq[ ][ 2 ][ 0 ] is the first  response, for example "Yes, at night."
   #                            and seq[ ][ 2 ][ 1 ] is the second response, for example "Yes, during the day." ],
   #     [ The actions are the next list,
   #                             so seq[ ][ 3 ][ 0 ] is the first  action, for example 0 ( meaning take no action )
   #                            and seq[ ][ 3 ][ 1 ] is the second action, for example 1 ( meaning advance one question ) ],
   #     [ The destinations are the next list,
   #                             so seq[ ][ 4 ][ 0 ] is the first  destination, for example 'secondSetOfQuestions.txt'
   #                            and seq[ ][ 4 ][ 1 ] is the second destination, for example 'http://bit.ly/openalluretest' ]]]
   #     [ The links are the next list,
   #                             so seq[ ][ 5 ][ 0 ] is the first  link, for example 'http://movieToWatch'
   #                            and seq[ ][ 5 ][ 1 ] is the second link, for example 'slidecastToWatch' ]]]
   #     [ The inputs are the next list,
   #                             so seq[ ][ 6 ][ 0 ] is the first  input, for example 0 (indicating no input on this answer)
   #                            and seq[ ][ 6 ][ 1 ] is the second link, for example 1 (indicating input allowed on this answer)
   #     Special case for photos    seq[0][ 7 ] is list of smile/talk/listen photo names
   #     [ The tag strings are next,
   #                             so seq[ ][ 8 ] is a unicode string tag for the question, for example u'skip to here'
   #     Special case for rules     seq[0][ 9 ] is a tuple with any script-specific rules

See `Open Allure wiki Separate Content File Syntax`_ for details and examples.

.. _Open Allure wiki Separate Content File Syntax: http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

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

import gettext
import htmlentitydefs
import os
import re
import sys
import urllib2

from BeautifulSoup import BeautifulSoup          # For processing HTML
from configobj import ConfigObj


##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
#
# From Fredrik Lundh, http://effbot.org/zone/re-sub.htm#unescape-html

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

class QSequence( object ):
    """A Question Sequence contains (multiple) question blocks consisting of a question with answers/responses/actions"""

    def __init__( self, filename=u"openallure.txt", path='', nltkResponse=None ):
        """
        Read either a local plain text file or text tagged <pre> </pre> from a webpage or body of an Etherpad
        """
        config = ConfigObj("openallure.cfg")

        # configure language for this question sequence
        # start with default from openallure.cfg (may be overridden by script)
        gettext.install(domain='openallure', localedir='locale',unicode=True)
        self.language = 'en'
        try:
            self.language = config['Options']['language']
        except KeyError:
            pass
        if len(self.language) > 0 and self.language != 'en':
            mytrans = gettext.translation(u"openallure",
                                          localedir='locale',
                                          languages=[self.language], fallback=True)
            mytrans.install(unicode=True) # must set explicitly here for Mac
        self.defaultAnswer = config['Options']['defaultAnswer']
        responsesConfig = ConfigObj("responses.cfg")
        self.ruleTypes = responsesConfig.sections
        self.cleanUnicodeTextStr = ''
        self.inputs = []

        # attribute storing path to sequence (excludes name)
        self.path = path

        if filename.startswith(u"http://"):
            # read text tagged with <pre> </pre> from website or body of an Etherpad
            try:
                urlOpen = urllib2.urlopen( filename )
            except:
                print( u"Could not open %s" % filename )

            # parse out text marked with <pre> </pre>
#            links = SoupStrainer('pre')
#            taggedPreText = [tag for tag in BeautifulSoup(urlOpen, parseOnlyThese=links)]
#          print 'taggedPreText', taggedPreText

            soup = BeautifulSoup(urlOpen)
            taggedPre = soup.pre
            if not str(taggedPre) == 'None':
                self.inputs = unescape(''.join(soup.pre.findAll(text=True))).splitlines()
            else:
                # If no taggedPreText, try postbody (NING)
                postbody = soup.find("div", { "class" : "postbody" })
                if not str(postbody) == 'None':
                    # restore blank lines
                    postbodyStr = str(postbody).replace('<br /><br />','\n')
                    postbody = BeautifulSoup(postbodyStr)
                    self.inputs = unescape('\n'.join(postbody.findAll(text=True))).splitlines()
                    # strip off leading spaces
                    self.inputs = [line.lstrip() for line in self.inputs]
                else:
                    # If no taggedPreText, try Etherpad body
                    self.cleanUnicodeTextStr = \
                    str(soup)[ str(soup).find('"initialAttributedText":{"text"')+33 : \
                               str(soup).find(',"attribs":')-1 ]
                    self.inputs = unescape(self.cleanUnicodeTextStr).split('\\n')


            if len(self.inputs) == 0:
                self.inputs = [_(u"Hmmm. It seems ") + filename, _(u"does not have a script"),
                           _(u"marked with <pre> </pre>."),
                           _(u"What now?"),
                           _(u"[input];;")]
            else:
                # set path attribute to be everything up to through last slash in url
                slashAt = filename.rfind( '/' ) + 1
                self.path = filename[0:slashAt]

        elif filename.startswith("nltkResponse.txt"):
            self.inputs = nltkResponse.split("\n")

        else:
            if filename.startswith('~/'):
                filename = os.environ['HOME'] + filename[1:]
            # read file and decode with utf-8
            try:
                raw = open( filename ).readlines()
                self.inputs = []
                for line in raw:
                    self.inputs.append( unicode( line, 'utf-8' ) )
            except IOError:
                self.inputs = [_(u"Well ... It seems ") + filename, _(u"could not be opened."),
                           _(u"What now?"),
                           _(u"[input];;")]

        # parse into sequence
        self.sequence = self.regroup( self.inputs, self.classify( self.inputs ) )


    def classify( self, strings ):
        """
Create list of string types::

    Identify strings which contain new line only   ( type N )
    #             or start with a hash # comment   ( type C )
    #             or which contain ; or ;; markers ( type indicated by offset of separator
    #                                                     between Answer ; Response )
    #             or start with rule indicators    ( type R )
    #                [ rule type ]
    #                [[ rule name ]]
    #                re= or re =
    #                example= or example =
    #                reply= or reply =
    #             or start with http://            ( type L )
    #             or else mark as question         ( type Q )

        """
        string_types = []
        inRule = False
        inQuote = False
        priorQString = ""
        for i in strings:
            if inQuote:
                # mark as type R until closing triple quotes are found
                string_types.append( "R" )
                tripleQuoteAt = i.find('"""')
                if not tripleQuoteAt == -1:
                    inQuote = False
                    inRule = False
            else:
                if i.strip() in ["","\n","\\n"]:
                    string_types.append( "N" )
                    priorQString = ""
                elif i.startswith( "#" ):
                    string_types.append( "C" )

                elif i.startswith( "re=" ) or i.startswith( "re =" ):
                    string_types.append( "R" )
                elif i.startswith( "example=" ) or i.startswith( "example =" ):
                    string_types.append( "R" )
                elif i.startswith( "reply=" ) or i.startswith( "reply =" ):
                    string_types.append( "R" )
                    # test for triple quotes on this line
                    tripleQuoteAt = i.find('"""')
                    if tripleQuoteAt == -1:
                        # reply marks last line of rule
                        inRule = False
                    else:
                        # closing triple quotes will mark last line of rule
                        inQuote = True
                        # test for SECOND (closing) triple quotes on this line
                        if not i[tripleQuoteAt+2:].find('"""') == -1:
                            inQuote = False
                            inRule = False
                elif i.startswith( "http://" ):
                    semicolonAt = i.find( ";" )
                    if semicolonAt > 0:
                        string_types.append( str( semicolonAt ) )
                    else:
                        # An answer-side link with no square bracket
                        string_types.append( "L" )

                elif i.startswith( "[" ):
                    # This could be a rule type, rule name, question tag or answer-side link
                    if inRule:
                        # It's a rule name
                        string_types.append( "R" )
                    elif i.startswith("[["):
                        # It's a second rule name
                        string_types.append( "R" )
                    else:
                        # Check content against list of rule types
                        bracketAt = i.find( ']' )
                        maybeRuleType = i[ 1 : bracketAt ].strip()
                        if maybeRuleType in self.ruleTypes:
                            # It's a rule type
                            string_types.append( "R" )
                            inRule = True
                        else:
                            # must be question tag or answer-side link
                            semicolonAt = i.find( ";" )
                            if semicolonAt > 0:
                                string_types.append( str( semicolonAt ) )
                            else:
                                string_types.append( "Q" )

                else:
                    semicolonAt = i.find(";")
                    if semicolonAt > 0:
                        string_types.append(str(semicolonAt))
                    else:
                        if len(i) > 0:
                            if priorQString.strip().endswith('?'):
                                # next things are answers even if not marked with ;
                                string_types.append(len(i))
                            else:
                                string_types.append("Q")
                                priorQString = i
                        else:
                            string_types.append("Q")
                            priorQString = i

#        for index, string in enumerate(strings):
#            print string_types[index], string
        return string_types

    def regroup( self, strings, string_types ):
        """Use string_types to sort strings into
        Questions, Answers, Responses and Subsequent Actions
        and Rules"""
        onString    = 0
        sequence    = []
        question    = []
        answer      = []
        response    = []
        action      = []
        destination = []
        link        = []
        inputFlags  = []
        photos      = []
        tag         = u''
        rules       = []
        photoSmile = photoTalk = photoListen = None
        while onString < len( strings ):
            if string_types[ onString ] == "Q":
                # check for tags and configuration overrides (which use =)
                if strings[ onString ].startswith('['):
                    if strings[ onString ].find( '=' ) == -1:
                        # this is a tag
                        bracketAt = strings[ onString ].find( ']' )
                        tag = strings[ onString ][ 1 : bracketAt ]
                        tag = tag.lower()
                    else:
                        # this is a configuration override
                        # strip [ and ] and then split on =
                        bracketAt = strings[ onString ].find( ']' )
                        configItem, configValue = \
                           strings[ onString ][ 1 : bracketAt ].split( '=' )
                        configItem = configItem.strip().lower()
                        configValue = configValue.strip().lower()
                        if configItem == 'smile':
                            photoSmile = configValue.strip()
                        elif configItem == 'talk':
                            photoTalk = configValue.strip()
                        elif configItem == 'listen':
                            photoListen = configValue.strip()

                        if isinstance( photoSmile, unicode ) and \
                           isinstance( photoTalk, unicode ) and \
                           isinstance( photoListen, unicode ):
                            photos.append( photoSmile )
                            photos.append( photoTalk )
                            photos.append( photoListen )
                            del photoSmile, photoTalk, photoListen

                        if configItem == 'language':
                            self.language = configValue
                            if len(self.language) > 0:
                                mytrans = gettext.translation(u"openallure",
                                                              localedir='locale',
                                                              languages=[self.language], fallback=True)
                                mytrans.install(unicode=True) # must set explicitly here for mac
                                #print _('Language is %s') % self.language

                # check if next string is a link
                # if so, this Q is really an A and will consume both lines
                elif onString < len(string_types) - 1 and string_types[ onString + 1 ] == "L":
                    answer.append( '[' + strings[ onString ].strip() + ']' )
                    response.append(u'')
                    action.append(1)
                    destination.append(u'')
                    link.append( strings[ onString + 1 ].strip() )
                    inputFlags.append(0)
                else:
                    question.append( strings[ onString ].rstrip() )
            elif string_types[ onString ] == "N":
                # add a default response if no subsequent response is provided
                # (also test whether next or final types are N)
                nextOrFinalType = string_types[ min( onString + 1, len(string_types) - 1) ]
                if len(question) and not len(answer) and \
                not self.defaultAnswer == '' and \
                nextOrFinalType == 'Q':
                    if self.defaultAnswer == 'next':
                        answer.append(_(u'[next]'))
                        response.append(u'')
                        action.append(1)
                        destination.append(u'')
                        link.append(u'')
                        inputFlags.append(1)
                    elif self.defaultAnswer == 'input':
                        answer.append(_(u'[input]'))
                        response.append(u'')
                        action.append(0)
                        destination.append(u'nltkResponse.txt')
                        link.append(u'')
                        inputFlags.append(1)
                # signal for end of question IF there are responses
                if len(response):
                    # add to sequence and reset
                    if len(question) == 0:
                        question.append(u'')
                    sequence.append( [question, answer, response, action,
                                      destination, link, inputFlags, photos, tag] )
                    question    = []
                    answer      = []
                    response    = []
                    action      = []
                    destination = []
                    link        = []
                    inputFlags  = []
                    photos      = []
                    tag         = u''
            elif string_types[ onString ] == "C":
                # skip over comment strings
                pass
            elif string_types[ onString ] == "L":
                # skip over link strings (used by prior answer)
                pass
            elif string_types[ onString ] == "R":
                # collect script-based rules
                rules.append( strings[ onString ] )
            else:
                # use number to break string into answer and response
                answerString = strings[ onString ][ :int( string_types[ onString ] ) ].rstrip()

                # examine answerString to determine if it contains
                # 1/ an [input] instruction
                # 2/ a link in the wiki format [link label]
                linkString = u''
                inputFlag = 0
                if answerString.startswith(_(u'[input]')):
                    # no text will be displayed until the user types it,
                    # but the instruction can be passed through as the answer string
                    # to serve as a prompt
                    label = _(u'[input]')
                    inputFlag = 1
                elif answerString.startswith(_(u'[next]')):
                    # no text will be displayed until the user types it,
                    # but the instruction can be passed through as the answer string
                    # to serve as a prompt
                    label = _(u'[next]')
                    inputFlag = 1
                elif answerString.startswith(u'['):
                    spaceAt = answerString.find(u' ')
                    closeBracketAt = answerString.find(u']')
                    # The syntax only has a chance of being correct if the space comes before the closing bracket
                    if spaceAt > 0 and closeBracketAt > 0 and spaceAt < closeBracketAt:
                        linkString = answerString[ 1 : spaceAt]
                        label = u'[' + answerString[ spaceAt + 1 : ]
                    else:
                        # If a space is not found between the brackets AND
                        # the string did not match the translated values of [input] or [next]
                        # then we are probably trying to make Open Allure work in the wrong language
                        # TODO: Get user interaction here, not just console
                        print( u"Incorrect syntax in answer: %s " % answerString )
                        print( u"This is probably due to your language setting (%s)" % self.language)
                        raise SystemExit
                elif answerString.startswith(u'http://'):
                    spaceAt = answerString.find(u' ')
                    # The syntax only has a chance of being correct if the space comes before the closing bracket
                    if spaceAt > 0:
                        linkString = answerString[ : spaceAt]
                        label = u'[' + answerString[ spaceAt + 1 : ] + u']'
                    else:
                        linkString = answerString
                        label = u'[' + answerString + u']'
                else:
                    label = answerString
                link.append( linkString )
                answer.append( label )
                inputFlags.append( inputFlag )

                # NOTE: +1 means to leave off first semi-colon
                responseString = strings[ onString ][ int( string_types[ onString ] ) + 1: ].strip()
                # catch answers with no marking
                if responseString == '':
                    responseString = ';'

                # examine start of responseString to determine if it signals action
                # with additional ;'s or digits ( including + and - ) or brackets
                # IF none found, leave action as 0
                actionValue = 0
                linkString = u''
                while len( responseString ) and responseString.startswith(u';'):
                    actionValue += 1
                    responseString = responseString[ 1: ].lstrip()
                digits = u''
                while len( responseString ) and \
                         ( responseString[ 0 ].isdigit() or
                           responseString[ 0 ] in [u'+',u'-'] ):
                    digits += responseString[ 0 ]
                    responseString = responseString[ 1: ].lstrip()
                if len( digits ):
                    actionValue = int( digits )
                if responseString.startswith( u'[' ):
                    linkEnd = responseString.find( u']' )
                    linkString = responseString[ 1 : linkEnd ].strip()
                    responseString = responseString[ linkEnd + 1 : ].lstrip()
                    # now look at link and decide whether it is a page name
                    # that needs help to become a URL
                    # or a tag
                    if not linkString.startswith(u'http'):
                        # do not put a path in front of a .txt file
                        if not linkString.endswith(u'.txt'):
                            linkString = self.path + linkString
                            # to sort out whether this is a tag
                            # we need a complete parsing of the question sequence
                            # so this evaluation will take place in a second pass
                            # which will convert LINKS to ACTIONS when we find a link that points
                            # to a tag within the sequence
                        #print linkString

                # If there is [input] in the answerString and no destination
                # in the responseString, default to nltkResponse.txt
                if inputFlag and len( linkString ) == 0:
                    linkString = u'nltkResponse.txt'

                destination.append( linkString )
                response.append( responseString )
                action.append( actionValue )

            onString += 1

        # append last question if not already signaled by N at end of inputs
        if len( question ) > 0 or len( response ) > 0:
            if len(question) == 0:
                question.append(u'')
            if len(question) and not len(answer):
                answer.append(_(u'[input]'))
                response.append(u'')
                action.append(0)
                destination.append(u'nltkResponse.txt')
                link.append(u'')
                inputFlags.append(1)
            sequence.append( [question, answer, response, action,
                              destination, link, inputFlags, photos, tag] )

        # catch sequence with a question with no answers
        # and turn it into an input
        if len(sequence) == 0:
            sequence.append( [ [_(u'What now?')],[_(u'[input]')],[u''],[0], \
                               [u''],[u''],[1],[],u'' ])
        if len(sequence[0][QUESTION]) == 0:
            sequence[0][QUESTION] = [_(u'[input]')]
            sequence[0][ACTION] = [0]
            sequence[0][DESTINATION] = [u'nltkResponse.txt']
            sequence[0][INPUTFLAG] = [1]
        # photos will not be changed if they are not found

        # Take second pass at sequence to convert LINKS to TAGS into ACTIONS
        tags = [ question[TAG] for question in sequence ]
        for qnum, question in enumerate( sequence ):
            for lnum, link in enumerate( question[DESTINATION] ):
                if not link == u'' and link[link.rfind('/') + 1:].lower() in tags:
                    # remove link
                    sequence[ qnum ][DESTINATION][ lnum ] = u''
                    # change action to RELATIVE position of question
                    # that is, how much shift from current question, qnum
                    # to tagged question
                    sequence[ qnum ][ACTION][ lnum ] = tags.index(link[link.rfind('/') + 1:].lower()) - qnum

        # Parse just the lines classified as rules
        ruleStrings = [ str( unicodeStr ) for unicodeStr in rules ]
        scriptRules = ConfigObj( infile = ruleStrings )
        rules = []
        for section in scriptRules.sections:
            for subsection in scriptRules[section].sections:
                # a regular expression overrides an example
                if 're' in scriptRules[section][subsection]:
                    if 'reply' in scriptRules[section][subsection]:
                        reply = scriptRules[section][subsection]['reply']
                    else:
                        reply = '[' + subsection + ']'
                    rule = ( scriptRules[section][subsection]['re'],
                             reply,
                             section, subsection )
                elif 'example' in scriptRules[section][subsection]:
                    # turn example into a regular expression
                    example = scriptRules[section][subsection]['example']
                    openBracketAt = example.find('[')
                    closeBracketAt = example.find(']', openBracketAt + 1)
                    secondOpenBracketAt = example.find('[', closeBracketAt + 1)
                    secondCloseBracketAt = example.find(']', secondOpenBracketAt + 1)
                    if openBracketAt == -1:
                        # if no brackets, use whole example as the regular expression
                        re = example
                    else:
                        firstPartRE = example[ openBracketAt + 1 : closeBracketAt ].strip()
                        re = '(' + firstPartRE + ')(.*)'
                        if openBracketAt > 0:
                            re = '(.*)' + re
                        if secondOpenBracketAt > closeBracketAt:
                            secondPartRE = example[ secondOpenBracketAt + 1 : secondCloseBracketAt ].strip()
                            re = re + '(' + secondPartRE + ')(.*)'
                    if 'reply' in scriptRules[section][subsection]:
                        reply = scriptRules[section][subsection]['reply']
                    else:
                        reply = '[' + subsection + ']'
                    rule = ( re, reply, section, subsection )
                rules.append(rule)
        sequence[ 0 ].append( tuple( rules ) )
        return sequence


if __name__ == "__main__":
    if len(sys.argv) > 1 and 0 != len(sys.argv[1]):
        seq = QSequence( sys.argv[1] )
    else:
        seq = QSequence('welcome.txt')
    for question in seq.sequence:
        print '------------'
        print 'TAG         ',question[8]
        print 'QUESTION    ',question[0]
        print 'ANSWER      ',question[1]
        print 'RESPONSE    ',question[2]
        print 'ACTION      ',question[3]
        print 'DESTINATION ',question[4]
        print 'LINK        ',question[5]
        print 'INPUTFLAG   ',question[6]
        print 'PHOTOS      ',question[7]
        if len(question) > 9:
            print 'RULES       ',question[9]
