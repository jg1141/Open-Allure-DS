'''
The Natural Language Processing component of open-allure-ds.
Based on the Chat bot class from NLTK

Modify the bottom of this file to run doc tests or to hold a conversation.

TODO::

   Fix the natural language math parsing
   - make all test cases pass

'''
from util import Chat as BaseChat

from configobj import ConfigObj
import gettext
import re
import random

RESPONSE = 0
TYPE = 1
NAME = 2

reflections = {
  "am"     : "are",
  "was"    : "were",
  "i"      : "you",
  "i'd"    : "you would",
  "i've"   : "you have",
  "i'll"   : "you will",
  "my"     : "your",
  "are"    : "am",
  "you've" : "I have",
  "you'll" : "I will",
  "your"   : "my",
  "yours"  : "mine",
  "you"    : "me",
  "me"     : "you"
}

class Chat(BaseChat):
    def __init__(self, tuples, reflections={}):
        """
Initialize the chatbot.

tuples must contain an iterable of patterns, responses and types.

Each pattern is a regular expression matching the user's statement or question,
e.g. r'I like (.*)'.  For each such pattern a list of possible responses
is given, e.g. ['Why do you like %1', 'Did you ever dislike %1'].  Material
which is matched by parenthesized sections of the patterns (e.g. .*) is mapped
to the numbered positions in the responses, e.g. %1.

TODO: Need to mention the types that have been introduced to the tuples
math, text etc..

@type tuples: C{list} of C{tuple}
@param tuples: The patterns, responses, response types and rule names

@type reflections: C{dict}
@param reflections: A mapping between first and second person expressions
"""

        self._tuples = [(re.compile(x, re.IGNORECASE), y, z ,ruleName) \
        for (x, y, z, ruleName) in tuples]
        self._reflections = reflections

    def respond(self, inputString, scriptRules):
        """
        Generate a response to the users input.

        @type inputString: C{string}
        @param inputString: The string to be mapped
        @rtype: C{string}
        """
        if scriptRules != None:
            scriptRuleTuples = [(re.compile(x, re.IGNORECASE), y, z ,ruleName) \
                                 for (x, y, z, ruleName) in scriptRules]
            # Put the script rules at the front
            scriptRuleTuples.extend(self._tuples)
            self._tuples = scriptRuleTuples

        # check each pattern
        respType = u''
        respName = u''
        for (pattern, response, responseType, ruleName) in self._tuples:
            match = pattern.match(inputString)

            # did the pattern match?
            if match:

                respType = responseType
                respName = ruleName

                if responseType == "goto":
                    # find question with goto tag = ruleName
                    resp = u'Confirm\nGo to tag ' + ruleName + '\n[input];'

                elif responseType == "graph":
                    if ruleName == 'list':
                        resp = u'Confirm\nList Records\n[input];'
                    elif ruleName == 'meta':
                        resp = u'Confirm\nShow Meta Graph\n[input];'
                    elif ruleName == 'reset':
                        resp = u'Confirm\nReset Graph\n[input];'
                    elif ruleName == 'hide':
                        resp = u'Confirm\Hide Graph\n[input];'
                    elif ruleName == 'show':
                        resp = u'Confirm\nShow Graph\n[input];'
                    elif ruleName == 'hideText':
                        resp = u'Confirm\Hide Graph Text\n[input];'
                    elif ruleName == 'showText':
                        resp = u'Confirm\nShow Graph Text\n[input];'
                    elif ruleName == 'hideLabels':
                        resp = u'Confirm\Hide Graph Labels\n[input];'
                    elif ruleName == 'showLabels':
                        resp = u'Confirm\nShow Graph Labels\n[input];'
                    elif ruleName == 'hideResp':
                        resp = u'Confirm\Hide Graph Responses\n[input];'
                    elif ruleName == 'showResp':
                        resp = u'Confirm\nShow Graph Responses\n[input];'

                elif responseType == "quit":
                    # System exit handled in openallure.py
                    resp = u'Confirm\nQuit\n[input];'
                    pass

                elif responseType == "return":
                    # Return handled in openallure.py
                    resp = u'Confirm\nReturn\n[input];'
                    pass

                elif responseType == "open":
                    pos = response.find('%')
                    num = int(response[pos + 1:pos + 2])
                    sequenceToOpen = match.group(num)

                    resp = _(u'Confirm') + '\n' + _(u'Open ') + sequenceToOpen + \
                           ';[' + sequenceToOpen + ']\n' + _(u'[input];')

                elif responseType == "text":
                    if isinstance(response, tuple):
                        # pick a random response
                        resp = random.choice(response)
                    else:
                        resp = response
                    resp = self._wildcards(resp, match) # process wild cards

                elif responseType == "link":
                    # follow link to question tag (jump to question)
                    resp = response

                elif responseType == "show":
                    if ruleName == 'source':
                        resp = response

                elif responseType == "math":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos + 1:pos + 2])
                        operands.append(match.group(num))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos + 2:]
                        pos = response.find('%')
                    operator = response.split()[3]
                    errorMessage = ""
                    if operator == "add":
                        evalString = operands[0] + '+' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Adding " + " to ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "subtract":
                        evalString = operands[0] + '-' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Subtracting " + operands[1] + " from " + \
                               operands[0] + " gives " + \
                               str(calculatedResult) + errorMessage
                    if operator == "multiply":
                        evalString = operands[0] + '*' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Multiplying " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    if operator == "divide":
                        evalString = operands[0] + '* 1.0 /' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Dividing " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage

                elif responseType == "wordMath":
                    operands = []
                    pos = response.find('%')
                    while pos >= 0:
                        num = int(response[pos + 1:pos + 2])
                        numberWord = match.group(num)
                        if numberWord[0].isdigit():
                            number = eval(numberWord)
                        else:
                            number = ['zero', 'one', 'two', 'three', 'four',
                            'five', 'six', 'seven', 'eight', 'nine', 'ten',
                            'eleven', 'twelve', 'thirteen', 'fourteen',
                            'fifteen', 'sixteen', 'seventeen', 'eighteen',
                                      'nineteen', 'twenty'].index(numberWord)
                        operands.append(str(number))
                        response = response[:pos] + \
                            self._substitute(match.group(num)) + \
                            response[pos + 2:]
                        pos = response.find('%')
                    operator = response.split()[3]
                    errorMessage = ""
                    if operator == "add":
                        evalString = operands[0] + '+' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Adding " + " to ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    elif operator == "subtract":
                        evalString = operands[0] + '-' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Subtracting " + operands[1] + " from " + \
                                operands[0] + " gives " + \
                                str(calculatedResult) + errorMessage
                    elif operator == "multiply":
                        evalString = operands[0] + '*' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Multiplying " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage
                    elif operator == "divide":
                        evalString = operands[0] + '* 1.0 /' + operands[1]
                        try:
                            calculatedResult = eval(evalString)
                        except SyntaxError:
                            calculatedResult = 0
                            errorMessage = " (due to syntax error)"
                        resp = "Dividing " + " by ".join(operands) + \
                        " gives " + str(calculatedResult) + errorMessage

                else:
                    print "Other response type: %s" % respType
                    raise SystemExit
                return resp, respType, respName

# Read rules from separate configuration file.
# This file contains the DEFAULT rules which can be supplemented
# by rules included in the scripts.
gettext.install(domain='openallure', localedir='locale', unicode=True)

config = ConfigObj("openallure.cfg")
try:
    language = config['Options']['language']
except KeyError:
    language = 'en'
if len(language) > 0 and language != 'en':
    mytrans = gettext.translation(u"openallure",
                                  localedir='locale',
                                  languages=[language], fallback=True)
    mytrans.install(unicode=True) # must set explicitly here for mac
    # Add underscore for use in file name of responses.cfg
    responsesFile = "responses_" + language + ".cfg"
else:
    responsesFile = "responses.cfg"

config = ConfigObj(responsesFile)
ruleTypes = config.sections
rules = []
for section in config.sections:
    for subsection in config[section].sections:
        rule = ( config[section][subsection]['re'],
                 config[section][subsection]['reply'],
                 section, subsection )
        rules.append(rule)
responses = tuple(rules)

# As a last resort, ask for input
responses = responses + \
((r'(.*)', (_("Sorry, I don't understand that. What now?") + '\n' + _("[input];"),), "text", "what now"),)


import unittest

class TestChat(unittest.TestCase):

    def setUp(self):
        self.chatter = Chat(responses, reflections)

    def testQuit(self):
        self.assertEqual(self.chatter.respond('quit')[TYPE],'quit')
    def testExit(self):
        self.assertEqual(self.chatter.respond('exit')[TYPE],'quit')

    def testOpenType(self):
        self.assertEqual(self.chatter.respond('open something')[TYPE],'open')
    def testOpening(self):
        # Test that words STARTING with "open" do not trigger rule
        self.assertEqual( \
        self.chatter.respond('opening something')[NAME],'what now')

    def testReturn(self):
        self.assertEqual(self.chatter.respond('return')[TYPE],'return')
    def testRet(self):
        self.assertEqual(self.chatter.respond('ret')[TYPE],'return')
    def testReturning(self):
        # Test that words STARTING with "return" do not trigger rule
        self.assertEqual(self.chatter.respond('returning')[NAME],'what now')

    def testHi(self):
        self.assertTrue( \
        self.chatter.respond('hi')[RESPONSE].startswith("Welcome"))

class TestChatMath(unittest.TestCase):

    def setUp(self):
        self.chatter = Chat(responses, reflections)

    def testAddTwoAndThree(self):
        self.assertTrue( \
        self.chatter.respond('add two and three')[RESPONSE].endswith('5'))

    def testAddTwoToThree(self):
        self.assertTrue( \
        self.chatter.respond('add two to three')[RESPONSE].endswith('5'))

    def testAdd2And3(self):
        self.assertTrue( \
        self.chatter.respond('add 2 and 3')[RESPONSE].endswith('5'))

    def testSubtraction20From30(self):
        self.assertTrue( \
        self.chatter.respond('subtract 20 from 30')[RESPONSE].endswith('10'))

    def testSubtract200From100(self):
        response = self.chatter.respond('subtract 200 from 1000')[RESPONSE]
        self.assertTrue(response.endswith('800'), \
        'Response was: %s' % response)

    def testSubtractionSymbol(self):
        response = \
        self.chatter.respond('subtract twenty minus eight')[RESPONSE]
        self.assertTrue(response.endswith('12'), \
        'Response was: %s' % response)

    def testSubtractionWords(self):
        response = \
        self.chatter.respond('subtract two from three')[RESPONSE]
        self.assertTrue(response.endswith('1'), response)

    def testAdditionPlus(self):
        response = \
        self.chatter.respond('add two plus three')[RESPONSE]
        self.assertTrue(response.endswith('5'), response)

    def testAdditionTo(self):
        response = \
        self.chatter.respond('add two to three')[RESPONSE]
        self.assertTrue(response.endswith('5'), response)

    def testAdditionAnd(self):
        response = \
        self.chatter.respond('add two and three')[RESPONSE]
        self.assertTrue(response.endswith('5'), response)

    def testMultiply(self):
        response = \
        self.chatter.respond('multiply five and four')[RESPONSE]
        self.assertTrue(response.endswith('20'), response)

    def testDivide(self):
        response = \
        self.chatter.respond('divide twelve by four')[RESPONSE]
        self.assertTrue(response.endswith('3.0'), response)

    def testHideResp(self):
        self.assertTrue( \
        self.chatter.respond('hide resp')[NAME] == 'hideResp')

    def testHideGraph(self):
        self.assertTrue( \
        self.chatter.respond('hide graph')[NAME] == 'hide')

    def testHideMap(self):
        self.assertTrue( \
        self.chatter.respond('hide map')[NAME] == 'hide')
    def testlist(self):
        self.assertTrue( \
        self.chatter.respond('show rec')[NAME] == 'list')
    def testlist1(self):
        self.assertTrue( \
        self.chatter.respond('show records')[NAME] == 'list')
    def testlist2(self):
        self.assertTrue( \
        self.chatter.respond('show list')[NAME] == 'list')
    def testlist3(self):
        self.assertTrue( \
        self.chatter.respond('list rec')[NAME] == 'list')
    def testlist4(self):
        self.assertTrue( \
        self.chatter.respond('list records')[NAME] == 'list')
    def testmeta5(self):
        self.assertTrue( \
        self.chatter.respond('show meta')[NAME] == 'meta')
    def testmeta1(self):
        self.assertTrue( \
        self.chatter.respond('show meta graph')[NAME] == 'meta')
    def testmeta2(self):
        self.assertTrue( \
        self.chatter.respond('where am i overall')[NAME] == 'meta')
    def testreset(self):
        self.assertTrue( \
        self.chatter.respond('reset graph')[NAME] == 'reset')
    def testreset2(self):
        self.assertTrue( \
        self.chatter.respond('graph reset')[NAME] == 'reset')
    def testshow(self):
        self.assertTrue( \
        self.chatter.respond('show map')[NAME] == 'show')
    def testshow1(self):
        self.assertTrue( \
        self.chatter.respond('show graph')[NAME] == 'show')
    def testshow2(self):
        self.assertTrue( \
        self.chatter.respond('where am i')[NAME] == 'show')
    def testshowResp(self):
        self.assertTrue( \
        self.chatter.respond('show resp')[NAME] == 'showResp')
    def testshowText(self):
        self.assertTrue( \
        self.chatter.respond('show text')[NAME] == 'showText')
    def testhideText(self):
        self.assertTrue( \
        self.chatter.respond('hide text')[NAME] == 'hideText')
    def testshowlabels(self):
        self.assertTrue( \
        self.chatter.respond('show labels')[NAME] == 'showLabels')
    def testhidelabels(self):
        self.assertTrue( \
        self.chatter.respond('hide labels')[NAME] == 'hideLabels')


if __name__ == "__main__":
    test = False
    #test = True
    if test:
        unittest.main()
    else:
        chatter = Chat(responses,reflections)
        chatter.converse()
