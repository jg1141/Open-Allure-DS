"""
voice.py
a component of pyGhost.py

Collection of functions for rendering text-to-speech

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

class Voice(object):
    """Text-to-speech Functionality (optional)"""

    def __init__(self):
        """Initialize flag for available text-to-speech engine

        TODO: Make this dynamic rather than hardcoded.
        """

        self.systemHasDragonfly = 0
        self.systemHasEspeak    = 0

        if self.systemHasDragonfly:
            import dragonfly
            class SpeakRule(CompoundRule):
                spec = "[select] [letter] <abc>"
                extras = [Choice("abc", {
                                          "A.": "a",
                                          "B.": "b",
                                          "C.": "c",
                                          "D.": "d",
                                          "E.": "e",
                                          "F.": "f",
                                          "G.": "g",
                                          "H.": "h",
                                          "I.": "i",
                                          "J.": "j",
                                          "K.": "k",
                                          "L.": "l",
                                          "M.": "m",
                                          "N.": "n",
                                          "O.": "o",
                                          "P.": "p",
                                          "Q.": "q",
                                          "R.": "r",
                                          "S.": "s",
                                          "T.": "t",
                                          "U.": "u",
                                          "V.": "v",
                                          "W.": "w",
                                          "X.": "x",
                                          "Y.": "y",
                                          "Z.": "z"
                                         }
                                )
                         ]

                def _process_recognition(self, node, extras):
                    # repeat voice recognition
                    spokenLetter = extras["abc"]
                    Key(spokenLetter).execute()

                self.speechEngine = dragonfly.get_engine()
                self.speechEngine.speak("Hello")
                self.grammar = Grammar("alphabet")
                self.grammar.add_rule(self.SpeakRule())    # Add the top-level rule.
                self.grammar.load()                   # Load the grammar.

    def speak(self,phrase):
       """Say or print phrase using available text-to-speech engine or stdout"""

       if self.systemHasDragonfly:
           import dragonfly
           self.speechEngine.speak(phrase)
       elif self.systemHasEspeak:
           import os
           os.system('espeak -s150 "' + phrase + '"')
       else:
           print phrase
           #pygame.time.wait(500)

