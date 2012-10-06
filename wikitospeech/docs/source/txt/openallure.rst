=====================
`openallure.cfg`
=====================

Modify this configuration file to suit your needs::

    [Source]
    #
    # Set the source for the starting question sequence
    #
    # This can be the local file name for a plain text file
    # with the syntax specified at
    # http://code.google.com/p/open-allure-ds/wiki/SeparateContentFileSyntax
    #
    # OR an internet address (URL) for a web page that contains
    # the question sequence tagged as preformatted text
    # (i.e. text between the tags <pre> and </pre>)
    #
    url = welcome.txt
    #url = http://openallureds.ning.com/profiles/blogs/open-allure-script-for-the
    #url = test.txt
    #url = 20101101_Khan.txt
    #url = talk.txt
    #url = sage.txt
    #url = temp.txt
    #url = http://ietherpad.com/dR9b1BiBo6
    #url = input.txt
    
    [Options]
    #
    # fadeTime controls how long text takes (in milliseconds) to appear on screen
    #
    fadeTime = 30
    
    # delayTime is the default time (in milliseconds) for an automatic page turn
    #
    delayTime = 3000
    
    # allowNext allows right arrow on keyboard to skip to
    #    the next question without giving an answer or hearing a response
    #
    allowNext = 1
    
    # defaultAnswer allows a script to have questions without specific answers
    #    (a blank line signals the end of a question or statement)
    #    in which case defaultAnswer is added by default to fill the gap.
    #    Leave blank to disable.
    #    Key:
    #    defaultAnswer = next
    #      inserts a default answer of [next];;
    #    defaultAnswer = input
    #      inserts a default answer of [input];;
    #
    defaultAnswer = next
    
    [Browser]
    #
    # windowsBrowser is the browser that will be used in Windows
    # darwinBrowser is the browser that will be used in Mac
    #
    windowsBrowser = d:\\firefox\\firefox
    darwinBrowser = open
    #darwinBrowser = /Applications/Firefox.app/Contents/MacOS/firefox-bin
    
    [Colors]
    #
    # Copy the desired (Red, Green, Blue) color codes into the things to color below
    #
    # black = 0,0,0
    # gray  = 200,200,200
    # white = 255,255,255
    # red   = 255,0,0
    # green = 0,255,0
    # blue  = 0,0,255
    # yellow= 255,255,0
    # purple= 255,0,255
    #
    background      = 255,255,255
    unreadText      = 255,255,255
    readText        = 0,0,0
    selectedText    = 255,0,0
    highlightedText = 255,255,0
    
    [Data]
    #
    # oadb is the Open Allure Database
    # different users could use different databases
    #
    oadb = oadb
    
    [Font]
    #
    # Default uses system font
    # heititc supports Chinese characters
    #
    font = heititc
    size = 25
    #
    # margins are top x, top y, x width, y width
    #
    margins = [ 20, 20, 600, 440 ]
    
    [GraphViz]
    #
    # GraphViz displays a graph of the flow of questions and answers
    # Commands:
    #    show graph
    #    hide graph
    # autoStart causes Open Allure to start in show graph mode
    # path is the full path including the name of the application
    # showResponses causes responses to be show on the graph
    # showText causes the text of the question/answer/response to show as words
    #    if False, text shows at Q<num>A<num> codes
    # showLabels causes the text labels to show
    #
    autoStart = False
    path = /Applications/Graphviz.app/Contents/MacOS/Graphviz
    showResponses = True
    showText = True
    showLabels = True
    
    [Photos]
    #
    # Smile is the awaiting-input image
    # Listen is the image when user input has begun
    # Talk is the image when text-to-speech is in progress
    #
    # TODO: Support for multiple speakers (for example, the characters in a play)
    #
    smile  = jg-smile-small.jpg
    listen = jg-listening-small.jpg
    talk   = jg-gesturing-small.jpg
    
    [Voice]
    #
    # Indicate which text-to-speech engine will generate spoken output
    # If none is selected, the default is to just print output to the console
    #
    # Dragonfly may be available on Mac and PC systems
    # eSpeak may be available on Unix systems
    # Say may be available on Mac systems
    #
    # (optional) language is added to the command line string for eSpeak and say
    # to permit different voices/accents
    #
    useDragonfly = 0
    useEspeak = 0
    useSay = 1
    useSayStatic = 0
    #language = -v french
    #language = -v english
    language =
