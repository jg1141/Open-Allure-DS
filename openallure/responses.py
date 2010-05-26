
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

# This serves as a set of default responses.
# responses are matched top to bottom, so non-specific matches occur later
# for each match, a list of possible responses is provided
responses = (

    (r'(demo|hi|hello)(.*)',
    ( """Welcome. Here are some choices:
Do simple math;;
Explore a dictionary;;;
Learn about Open Allure;[about.txt]
[input];;;;
    
OK. 
Try some two operand math
like ADD 2 + 2:
[input];;
    
Look up words
by entering WHAT IS <word>:
[input];;
"""),"text"),

    (r'(.*)(turing|loebner)(.*)',
    ( "I was hoping this would come up.\nLook at std-turing.aiml;[turing.txt]"),"text"),

    (r'(open|start)\s*([a-zA-Z0-9\-\_\.\/\:]+)',
    ( "Request to open new sequence%2"),"open"),

    (r'(quit|exit)',
    ( "Request to quit"),"quit"),

    (r'(good|bad)',
    ( "I'm not%1","You're%1","So%1"),"text"),

# Extract numbers from math expressions

    # Addition
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\+\s*(\-?[0-9.]+)',
    ( "You want to add%1 and%2"),"math"),
    # Subtraction
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\-\s*(\-?[0-9.]+)',
    ( "You want to subtract%1 minus%2"),"math"),
    # Multiplication
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\*\s*(\-?[0-9.]+)',
    ( "You want to multiply%1 by%2"),"math"),
    # Division /
    (r'[a-z]*\s*[a-z\']*\s*(\-?[0-9.]+)\s*\/\s*(\-?[0-9.]+)',
    ( "You want to divide%1 by%2"),"math"),

# Word math expressions

    # Addition
    (r'(what is|what\'s|find|calculate|add)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|[0-9.]+)\s+plus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to add%2 and%3"),"wordMath"),

    (r'add\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(and|plus)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to add%1 and%3"),"wordMath"),

    # Subtraction
    (r'(what is|what\'s|find|calculate|subtract)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+minus\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to subtract%2 minus%3"),"wordMath"),

    (r'subtract\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+from\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to subtract%2 minus%1"),"wordMath"),

    # Multiplication
    (r'(what is|what\'s|find|calculate|multiply)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(times|multiplied by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to multiply%2 by%4"),"wordMath"),

    # Division /
    (r'(what is|what\'s|find|calculate|divide)\s+(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)\s+(over|divided by|by)\s(zero|one|two|three|fourteen|four|five|sixteen|six|seventeen|seven|eighteen|eight|nineteen|nine|ten|eleven|twelve|thirteen|fifteen|twenty|[0-9.]+)',
    ( "You want to divide%2 by%4"),"wordMath"),

# Word lookup expressions

    (r'(what does|what\'s)\s+(.*)\s+mean(.*)',
    ( "You want to define%2"),"wordLookup"),

    (r'(what is an|what is a|what is the|what is|search for|search|what\'s an|what\'s a|what\'s|find|define|defined)\s+(.*)',
    ( "You want to define%2"),"wordLookup"),
)
