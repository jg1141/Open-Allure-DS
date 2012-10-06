# -*- coding: utf-8 -*-
"""
SlideSpeechConverter.py
a component of SlideSpeech.py

Extract speaker notes from .odp or .ppt file
Prepare script.txt for SlideSpeech
Prepare convert.bat to generate audio via text-to-speech
Output HTML wrappers for slide images and audio
Prepare makeVid.bat to generate video

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt

20110825 Add version to title bar
20110901 Add direct to video output
20110901 Switch to jpg, mklink with /h
20110902 Switch to jpg for Windows and png for Mac
20110907 More tweaks to joinContents
20110909 Allow over 20 slides in MP4Box to cat for Mac
20110910 Coping with unavailable mklink in Windows and path names containing spaces
20110913 Remove [] from script output and wrap ctypes import with win32 test
20110915 Added boilerplate script comments including version number
20110916 Read Unicode
20110917 Write out bits of Question/Answer/Response
20111118 Show image along with question. Requires slide with comment first.
         Example:
            Comment on Slide4
            [questions=on]
            Question for slide 4:
            Answer 1 ; Response 1
            [questions=off]

         NOTE: last slide must not have questions

img1.png > img1.htm > img1.mp3
[questions=on]
How many slides have we seen? > q/img1q1.htm > q/img1q1.mp3
One ;; > q/img1q1a1.mp3
Two ;; > q/img1q1a1.mp3

What slide is next? > q/img1q2.htm > q/img1q2.mp3
Third ;; > q/img1q2a1.mp3
Fourth; No, just the third. > q/img1q2a2.mp3, > q/img1q2r2.mp3

[questions=off]

20111112 If script has [Source=http:// ...] add this link to the question page
20111121 Turn off debug2.txt and put quotes around calls in makeVid.bat
20111128 Working Linux version once dependencies are installed
    Linux dependencies include:
    sox
    ffmpeg
    mencode
    espeak
20111205 Allow for direct script and image creation from PowerPoint files
20111206 Renamed SlideSpeech Converter
20111207 Changed to using mencoder to create .avi files for makeVid Windows
"""
__version__ = "0.1.31"

import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from ConfigParser import ConfigParser
import codecs
import easygui
import math
import os
import os.path
import shutil
import scriptParser
import stat
import subprocess
import sys
import time
if sys.platform.startswith("win"):
    import win32com.client
import webbrowser
from zipfile import ZipFile

def ensure_dir(d):
    """Make a directory if it does not exist"""
    if not os.path.exists(d):
        os.makedirs(d)

# Find location of Windows common application data files for odp2ss.ini
iniDirectory = None
if sys.platform.startswith("win"):
    import ctypes
    from ctypes import wintypes, windll
    CSIDL_COMMON_APPDATA = 35

    _SHGetFolderPath = windll.shell32.SHGetFolderPathW
    _SHGetFolderPath.argtypes = [wintypes.HWND,
                                ctypes.c_int,
                                wintypes.HANDLE,
                                wintypes.DWORD, wintypes.LPCWSTR]


    path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
    result = _SHGetFolderPath(0, CSIDL_COMMON_APPDATA, 0, 0, path_buf)
    iniDirectory = path_buf.value+os.sep+"SlideSpeech"
else:
    iniDirectory = os.path.expanduser('~')+os.sep+".SlideSpeech"

ensure_dir(iniDirectory)

if sys.platform.startswith("win"):
    imageFileSuffix = ".jpg"
else:
    imageFileSuffix = ".png"

## Obtain odpFile name and directory

# Check for last .odp file in config file
if sys.platform.startswith("win"):
    lastOdpFile = '~/*.ppt*'
else:
    lastOdpFile = '~/*.odp'
config = ConfigParser()
try:
    config.read(iniDirectory+os.sep+'odp2ss.ini')
    lastOdpFile = config.get("Files","lastOdpFile")
except:
    config.add_section("Files")
    config.set("Files","lastOdpFile","")
    with open(iniDirectory+os.sep+'odp2ss.ini', 'wb') as configfile:
        config.write(configfile)

if not os.path.isfile(lastOdpFile):
    lastOdpFile = None

if sys.platform.startswith("win"):
    odpFilePath = easygui.fileopenbox(title="SlideSpeech from PPT Converter "+__version__, msg="Select a .ppt file",
                              default=lastOdpFile, filetypes=None)
else:
    odpFilePath = easygui.fileopenbox(title="SlideSpeech from ODP Converter "+__version__, msg="Select an .odp file",
                              default=lastOdpFile, filetypes=None)

if odpFilePath == None:
    sys.exit()

(odpFileDirectory, odpFile) = os.path.split(odpFilePath)
(odpName, odpSuffix) = odpFile.split(".")

## Find or create list of .png or .jpg files

odpFileSubdirectory = odpFileDirectory+os.sep+odpName
# Create a subdirectory for generated files (if needed)
ensure_dir(odpFileSubdirectory)

scriptAndImagesCreated = False
if sys.platform.startswith("win") and odpSuffix.startswith("ppt"):
    # create .jpg files
    slideNotes = []
    try:
        Application = win32com.client.Dispatch("PowerPoint.Application")
    except:
        easygui.msgbox("PowerPoint not available.")
        sys.exit()
    Application.Visible = True
    Presentation = Application.Presentations.Open(odpFilePath)
    onSlide = 0
    for Slide in Presentation.Slides:
         imageName = "Slide" + str(onSlide) + ".jpg"
         onSlide += 1
         Slide.Export(odpFileSubdirectory+os.sep+imageName,"JPG",800,600)

         for Shape in Slide.NotesPage.Shapes:
            if Shape.HasTextFrame:
                if Shape.TextFrame.HasText:
                    text = Shape.TextFrame.TextRange.Text
                    if not text.isdigit():
                        slideNotes.append(text)
    Application.Quit()

    # Look for .jpg files (slide images) in the odpName subdirectory
    dir = os.listdir(odpFileSubdirectory)
    imageFileList = [file for file in dir if file.lower().endswith(imageFileSuffix)]

    outFile = open(odpFileSubdirectory+os.sep+"script.txt","w")
    onSlide = 0
    for item in slideNotes:
        imageName = "Slide" + str(onSlide) + ".jpg\n"
        onSlide += 1
        outFile.write(imageName)
        outFile.write(item + "\n\n")
    outFile.close()

    if ((0 != len(odpFile)) and (os.path.exists(odpFilePath))):
        # Save file name to config file
        config.set("Files","lastOdpFile",odpFilePath)
        with open(iniDirectory+os.sep+'odp2ss.ini', 'wb') as configfile:
            config.write(configfile)

    scriptAndImagesCreated = True
else:
    # Look for .jpg files (slide images) in the odpName subdirectory
    dir = os.listdir(odpFileSubdirectory)
    imageFileList = [file for file in dir if file.lower().endswith(imageFileSuffix)]

    # If no image files found there ...
    if len(imageFileList)==0:
        # ... look for image files in odpFileDirectory and copy to odpName subdirectory
        dir = os.listdir(odpFileDirectory)
        imageFileList = [file for file in dir if file.lower().endswith(imageFileSuffix)]
        # If still no image files, request some.
        if len(imageFileList)==0:
            easygui.msgbox("Need some slide image files for this presentation.\n.jpg for Windows or .png for Mac OSX.")
            sys.exit()
        else:
            for file in imageFileList:
                shutil.copy(odpFileDirectory+os.sep+file, odpFileSubdirectory)

# Find minimum value for slide number for linking to First Slide
# Find maximum value for slide number for linking to Last Slide
# Find imageFilePrefix, imageFileSuffix
# Default values
minNum = 0
maxNum = 0
wrongStem = False

for file in imageFileList:
    # Parse out file name stem (which includes number) and imageFileSuffix
    (stem, imageFileSuffix) = file.split(".")

    # Parse out just number (num) and imageFilePrefix
    if stem.startswith("Slide"):
        # PowerPoint Slide images are output to jpg with starting index of 0
        imageFilePrefix = "Slide"
        minNum=0
        num = int(stem[5:])
    elif stem.startswith("img"):
        # ODP slide images are output to img with starting index of 0
        imageFilePrefix = "img"
        num = int(stem[3:])
    else:
        wrongStem = True

if wrongStem:
    easygui.msgbox("Need slide image files for this presentation\n"+
    "with consistent stem: Slide* or img*\n\nCheck in "+odpFileSubdirectory)
    sys.exit()
else:
    if num>maxNum:
        maxNum=num

if not scriptAndImagesCreated:
    ## Step 1 - parse the .odp file, prepare script.txt and .zip file

    def joinContents(textPList):
        """Combine tagged XML into single string

    Needs to handle this from PowerPoint:
        <text:p text:style-name="a785" text:class-names="" text:cond-style-name="">
         <text:span text:style-name="a783" text:class-names="">Voice over 1</text:span>
         <text:span text:style-name="a784" text:class-names=""/>
        </text:p>

    or worse, this:
        <text:p text:style-name="a786" text:class-names="" text:cond-style-name="">
         <text:span text:style-name="a783" text:class-names="">
          Voice
          <text:s text:c="1"/>
         </text:span>
         <text:span text:style-name="a784" text:class-names="">
          over 1
          <text:s text:c="1"/>
          asdf
         </text:span>
         <text:span text:style-name="a785" text:class-names=""/>
        </text:p>

        """
        # item is list of all the XML for a single slide
        joinedItems = ""
        if len(textPList)>0:
            textItems = []
            i = 0
            for textP in textPList:
                textSpans = []
                # break the XML into a list of tagged pieces (text:span)
                for item in textP:
                    if type(item)==BeautifulSoup.Tag:
                        tagContents = item.contents
                        if type(tagContents)==type([]):
                            for item2 in tagContents:
                                if type(item2)==BeautifulSoup.Tag:
                                    textSpans.append([item2.contents])
                                else:
                                    textSpans.append([item2])
                        else:
                            textSpans.append([tagContents])
                    else:
                        textSpans.append([item])

                # flatten list
                textSpans1 = [item for sublist in textSpans for item in sublist]
                # clean up
                textSpans1b = []
                for item in textSpans1:
                    if type(item)==BeautifulSoup.NavigableString:
                        textSpans1b.append(item)
                    elif type(item)==type([]):
                        if len(item)==0:
                            pass
                        elif len(item)==1:
                            textSpans1b.append(item[0])
                        else:
                            for itemInList in item:
                                textSpans1b.append(itemInList)
                # find the contents of these pieces if they are still tagged (text:s)
                textSpans2 = []
                for textSpan in textSpans1b:
                    if type(textSpan)==BeautifulSoup.Tag:
                        textSpans2.append(textSpan.text)
                    else:
                        if (type(textSpan)==type([]) and len(textSpan)>0):
                            textSpans2.append(unicode(textSpan[0]))
                        else:
                            textSpans2.append(unicode(textSpan))

                justText = u""
                for item in textSpans2:
                    # deal with single quote and double quotes and dashes
                    # \u2018 LEFT SINGLE QUOTATION MARK
                    justText = justText + item + u" "
                textItems.append(justText)
            joinedItems = "\n".join(textItems)
        return joinedItems

    if ((0 != len(odpFile)) and (os.path.exists(odpFilePath))):
        # Save file name to config file
        config.set("Files","lastOdpFile",odpFilePath)
        with open(iniDirectory+os.sep+'odp2ss.ini', 'wb') as configfile:
            config.write(configfile)

        odpName = odpFile.replace(".odp","")
        odp = ZipFile(odpFilePath,'r')
        f = odp.read(u'content.xml')
        soup = BeautifulStoneSoup(f)
        notes = soup.findAll(attrs={"presentation:class":"notes"})
        noteTextPLists = [item.findAll("text:p") for item in notes]
        noteText = [joinContents(noteTextPList) for noteTextPList in noteTextPLists]
    else:
        sys.exit()

    # Create script.txt file
    scriptFile = codecs.open(odpFileSubdirectory+os.sep+'script.txt', encoding='utf-8', mode='w+')
    scriptFile.write("""#[path=]
    #
    #     Script created with SlideSpeech from ODP version """+__version__+
    "\n#     http://slidespeech.org\n"+
    "#     Date: "+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+"""
    #
    #     Title:
    #     Author:
    #
    #     SlideSpeech Slide show version
    #     http://
    #
    #     SlideSpeech Video version
    #     http://
    #
    #     SlideSpeech script:
    """)
    onImg = minNum
    for item in noteText:
        if onImg-minNum == 0: # first slide
            # insert line with link to first slide image after parameter lines
            # For example, noteText could start with [path=...]
            lines = item.split("\n")
            slideOnLine = -1
            for linenum, line in enumerate(lines):
                if len(line.strip())>0:
                    if line.startswith("["):
                        scriptFile.write(line+"\n")
                    elif slideOnLine == -1:
                        scriptFile.write(imageFilePrefix+str(onImg)+"."+imageFileSuffix+"\n")
                        slideOnLine = linenum
                        scriptFile.write(line+"\n")
                    else:
                        scriptFile.write(line+"\n")
                else:
                    scriptFile.write("\n")
        else:
            # Add a line with a link to each slide
            scriptFile.write(imageFilePrefix+str(onImg)+"."+imageFileSuffix+"\n")
            # followed by the voice over text for the slide
            scriptFile.write(item+"\n")
        scriptFile.write("\n")
        onImg += 1
    scriptFile.close()

# Collect script and image files into ZIP file
outputFile = ZipFile(odpFileDirectory+os.sep+odpName+".zip",'w')
savePath = os.getcwd()
os.chdir(odpFileSubdirectory)
outputFile.write("script.txt")
for file in imageFileList:
    outputFile.write(file)
os.chdir(savePath)
easygui.msgbox("Zipped script.txt and image files to "+odpFileDirectory+os.sep+odpName+".zip")

## Step 2 - Sequence script and make and run convert.bat
def convertItem(f,item,onImgStr):
    if sys.platform.startswith("win"):
        # For Windows
        f.write('"'+savePath+os.sep+'sapi2wav.exe" '+imageFilePrefix+onImgStr+'.wav 1 -t "')
        lines = item.split("\n")
        for linenum, line in enumerate(lines):
            if not line.startswith("["):
                line.replace('"',' ').replace('`',' ').replace(';',' ')
                if not line.startswith("#"):
                    f.write(line+" ")
            elif linenum>0:
                break
        f.write('"\n')
        f.write('"'+savePath+os.sep+'lame.exe" -h '+imageFilePrefix+onImgStr+'.wav '+ '"' + \
                             odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.mp3"\n')
        f.write('"'+savePath+os.sep+'sox.exe" '+imageFilePrefix+onImgStr+'.wav '+ '"' + \
                         odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.ogg"\n')
        f.write('del '+imageFilePrefix+onImgStr+'.wav\n')
    elif sys.platform.startswith("darwin"):
        # For Mac OSX
        f.write("/usr/bin/say -o "+imageFilePrefix+onImgStr+'.aiff "')
        lines = item.split("\n")
        for linenum, line in enumerate(lines):
            line.replace('"',' ').replace('`',' ').replace(';',' ')
            if not line.startswith("["):
                f.write(line+" ")
            elif linenum>0:
                break
    #    f.write(item)
        f.write('"\n')
        f.write("~/bin/sox "+imageFilePrefix+onImgStr+'.aiff "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.ogg"\n')
        f.write("~/bin/sox "+imageFilePrefix+onImgStr+'.aiff "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.mp3"\n')
        f.write("rm "+imageFilePrefix+onImgStr+'.aiff\n')

    else:
        # For Linux
        f.write("/usr/bin/espeak -w "+imageFilePrefix+onImgStr+'.wav "')
        lines = item.split("\n")
        for linenum, line in enumerate(lines):
            line.replace('"',' ').replace('`',' ').replace(';',' ')
            if not line.startswith("["):
                f.write(line+" ")
            elif linenum>0:
                break
    #    f.write(item)
        f.write('"\n')
        f.write("/usr/bin/sox "+imageFilePrefix+onImgStr+'.wav "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.ogg"\n')
        f.write("/usr/bin/sox "+imageFilePrefix+onImgStr+'.wav "'+
          odpFileSubdirectory+os.sep+imageFilePrefix+onImgStr+'.mp3"\n')
        # f.write("rm "+imageFilePrefix+onImgStr+'.wav\n')

def writeHtmlHeader(htmlFile):
    htmlFile.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' + "\n")
    htmlFile.write('"http://www.w3.org/TR/html4/transitional.dtd">' + "\n")
    htmlFile.write("<html>\n<head>\n")
    htmlFile.write('<meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">' + "\n")
    htmlFile.write('<title>SlideSpeech</title>\n')

def writeHtmlHeader2(htmlFile):
    htmlFile.write('</head>\n')
    htmlFile.write('<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">' + "\n")
    htmlFile.write('<center>' + "\n")

def writeHtmlFileNavigation(htmlFile, questionFileNames,  maxNum, position):
    # First page and Back navigation
    # First page
    if position==0:
        htmlFile.write("""First page Back """)
    # Second page
    elif position==1:
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href="../""" +
                                            odpName +""".htm">Back</a> """)
    # Rest of pages
    else:
        htmlFile.write("""<a href="../""" + odpName +""".htm">First page</a> <a href=""" + '"' +
                        questionFileNames[position-1]+""".htm">Back</a> """)

    # Continue and Last Page navigation
    # Last page
    if position==maxNum:
        htmlFile.write('Continue Last page<br>\n')
    # First page
    elif position==0:
        htmlFile.write( \
            '<a href="'+
            odpName+"/"+questionFileNames[position+1]+
            '.htm">Continue</a> ')
        htmlFile.write( \
            '<a href="'+
            odpName+"/"+questionFileNames[-1]+
            '.htm">Last page</a><br>\n')
    # Rest of pages
    else:
        htmlFile.write( \
            '<a href="'+
            questionFileNames[position+1]+
            '.htm">Continue</a> ')
        htmlFile.write( \
            '<a href="' +
            questionFileNames[-1] +
            '.htm">Last page</a><br>\n')

def writeHtmlJavascript(htmlFile,
                        questionFileNames,
                        question,
                        position,
                        audioFileTimes):
    """
        <script language="javascript" type="text/javascript">
        var t;
        function respond0()
        {
            clearTimeout(t)
            document.getElementById("a0").innerHTML = "Separators of plus and quotes";
            document.getElementById("a0").style.color = "grey";
            document.getElementById('playaudio').innerHTML='<audio controls autoplay><source src="img8q1r0.mp3" /><source src="img8q1r0.ogg" />Your browser does not support the <code>audio</code> element.</audio><!--[if lte IE 8]><embed src="img8q1r0.mp3" autostart="true"><![endif]-->';
        }
        function respond1()
        {
            clearTimeout(t)
            document.getElementById('playaudio').innerHTML='<audio controls autoplay><source src="img8q1r1.mp3" /><source src="img8q1r1.ogg" />Your browser does not support the <code>audio</code> element.</audio><!--[if lte IE 8]><embed src="img8q1r1.mp3" autostart="true"><![endif]-->';
            t=setTimeout("advance1()",12762);
        }
        function advance1()
        {
            location.href="img8q2.htm";
        }

    </script>
    """
    htmlFile.write('<script language="javascript" type="text/javascript">\nvar t;\n')
    for answerNum, answer in enumerate(question.answers):
        if len(answer.answerText)>0:
            htmlFile.write('function respond'+
                str(answerNum)+
                '()\n{\n    clearTimeout(t);\n')
            if not answer.action > 0:
                htmlFile.write('    document.getElementById("a'+
                    str(answerNum)+'").innerHTML = "'+
                    answer.answerText+
                    '";\n')
                htmlFile.write('    document.getElementById("a'+
                    str(answerNum)+
                    '").style.color = "grey";\n')

            if len(answer.responseText)>0:
                if position==0:
                    pathToAudio = odpName+'/'+questionFileNames[position]+'r'+str(answerNum)
                else:
                    pathToAudio = questionFileNames[position]+'r'+str(answerNum)

                htmlFile.write( \
                    "    document.getElementById('playaudio').innerHTML=" +
                    "'<audio controls autoplay><source src=" +
                    '"' + pathToAudio +
                    '.mp3" />')
                htmlFile.write('<source src="' +
                    pathToAudio +
                    '.ogg" />')
                htmlFile.write( \
                    "<embed src=" +
                    '"' + pathToAudio +
                    '.mp3' +
                    '" autostart="true"></audio>' + "';\n")
                if answer.action > 0:
                    htmlFile.write('    t=setTimeout("advance'+
                    str(answerNum)+
                    '()",'+
                    str(audioFileTimes[pathToAudio]+1000)+
                    ');\n')
            elif answer.action > 0:
                htmlFile.write("    advance"+
                    str(answerNum)+
                    '();\n')
            htmlFile.write('}\n')

            if (answer.action > 0 and position+answer.action < len(questionFileNames)):
                htmlFile.write('function advance'+
                    str(answerNum)+
                    '()\n{\n')
                htmlFile.write('    location.href="'+
                    questionFileNames[position+answer.action]+
                    '.htm";\n}\n')
    htmlFile.write('</script>\n')


def makeConvert(sequence):
    # Make list of question file names for navigation
    questionFileNames = []
    onImg = minNum
    onImgStr = str(onImg)
    onQ = 0
    for question in sequence:
        if len(question.answers)==0:
            questionFileNames.append(imageFilePrefix+onImgStr)
            onImg += 1
            onImgStr = str(onImg)
            onQ = 0
        else:
            onQ += 1
            questionFileNames.append(imageFilePrefix+onImgStr+"q"+str(onQ))
    maxNum = len(questionFileNames)-1

    # Make convert.bat to convert questionText into audio files
    f = codecs.open(odpFileDirectory+os.sep+"convert.bat", encoding='utf-8', mode='w+')
    os.chmod(odpFileDirectory+os.sep+"convert.bat",stat.S_IRWXU)
    onImg = minNum
    onImgStr = str(onImg)
    onQ = 0
    oggList = []
    for position, question in enumerate(sequence):

        # write convert.bat
        if len(question.answers)==0:
            convertItem(f," ".join(question.questionTexts),onImgStr)
            oggList.append(onImgStr)
            onImg += 1
            onImgStr = str(onImg)
            onQ = 0
        else:
            onQ += 1
            convertItem(f," ".join(question.questionTexts),onImgStr+"q"+str(onQ))
            oggList.append(onImgStr+"q"+str(onQ))
            onAns = 0
            for answer in question.answers:
                convertItem(f,answer.answerText,onImgStr+"q"+str(onQ)+"a"+str(onAns))
                oggList.append(onImgStr+"q"+str(onQ)+"a"+str(onAns))
                if len(answer.responseText)>0:
                    convertItem(f,answer.responseText,onImgStr+"q"+str(onQ)+"r"+str(onAns))
                    oggList.append(onImgStr+"q"+str(onQ)+"r"+str(onAns))
                onAns += 1

    # Write concatenation of all .ogg files into all.ogg
    f.write('cd "'+odpFileSubdirectory+'"\n')
    if sys.platform.startswith("win"):
        f.write('"'+savePath+os.sep+'sox.exe" ')
    elif sys.platform.startswith("darwin"):
        f.write("~/bin/sox ")
    else:
        f.write("/usr/bin/sox ")
    for item in oggList:
        f.write(imageFilePrefix+item+".ogg ")
        f.write('"'+savePath+os.sep+'silence.ogg" ')
    f.write("all.ogg\n")
    f.close()

def fetchAudioFileTimes():
    os.chdir(odpFileSubdirectory)
    dir = os.listdir(odpFileSubdirectory)
    ogg = [file for file in dir if file.lower().endswith(".ogg")]
    oggDict = {}

    for file in ogg:
        # Parse out file name stem
        (stem, audioFileSuffix) = file.split(".")
        # soxi -D returns the duration in seconds of the audio file as a float
        if sys.platform.startswith("win"):
            # Unfortunately, there is a requirement that soxi (with an implict .exe)
            # be the command to check audio file duration in Win32
            # but soxi is the name of the unix version of this utility
            # So we need to delete the (unix) file called soxi so the command line call
            # to soxi will run soxi.exe
            if os.path.isfile(savePath+os.sep+"soxi"):
                os.remove(savePath+os.sep+"soxi")
            command = [savePath+os.sep+"soxi","-D",odpFileSubdirectory+os.sep+file]
        elif sys.platform.startswith("darwin"):
            if os.path.isfile(savePath+os.sep+"soxi"):
                command = [savePath+os.sep+"soxi","-D",odpFileSubdirectory+os.sep+file]
            elif os.path.isfile(savePath+os.sep+"Contents/Resources/soxi"):
                command = [savePath+os.sep+"Contents/Resources/soxi","-D",odpFileSubdirectory+os.sep+file]
            else:
                command = ["soxi","-D",odpFileSubdirectory+os.sep+file]
        else :
            command = ["soxi","-D",odpFileSubdirectory+os.sep+file]

        process = subprocess.Popen(command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True)
        output = process.communicate()
        retcode = process.poll()
        if retcode:
            print "No time available"
        oggDict[stem]=int(float(output[0].strip())*1000)
    return oggDict

def writeHtml(sequence, audioFileTimes):

    # Make list of question file names for navigation
    questionFileNames = []
    onImg = minNum
    onImgStr = str(onImg)
    onQ = 0
    for question in sequence:
        if len(question.answers)==0:
            questionFileNames.append(imageFilePrefix+onImgStr)
            onImg += 1
            onImgStr = str(onImg)
            onQ = 0
        else:
            onQ += 1
            questionFileNames.append(imageFilePrefix+onImgStr+"q"+str(onQ))
    maxNum = len(questionFileNames)-1

    onImg = minNum
    onImgStr = str(onImg)
    onQ = 0
    for position, question in enumerate(sequence):

        if position==0:
            # Create first .htm file in same directory as odpFile
            htmlFile = codecs.open(odpFileDirectory+os.sep+odpName+".htm", encoding='utf-8', mode='w+')
        else:
            # Create subsequent .htm files in folder in same directory as odpFile
            htmlFile = codecs.open(odpFileSubdirectory+os.sep+questionFileNames[position]+".htm", encoding='utf-8', mode='w+')

        writeHtmlHeader(htmlFile)

        if len(question.answers)==0:
            writeHtmlHeader2(htmlFile)
            writeHtmlFileNavigation(htmlFile, questionFileNames,  maxNum, position)
        else:
            writeHtmlJavascript(htmlFile, questionFileNames, question, position,
                                audioFileTimes)
            writeHtmlHeader2(htmlFile)
            writeHtmlFileNavigation(htmlFile, questionFileNames, maxNum, position)

        if len(question.answers)==0:
            # image src and link to next slide
            # Last page which is not (also) the first page
            if (position==maxNum and position>0):
                # src but no link
                htmlFile.write( \
                    '<img src="' +
                    questionFileNames[position] + '.' + imageFileSuffix +
                    '" style="border:0px"><br>\n')
            # Last page which is also the first page
            elif (position==maxNum and position==0):
                # src but no link
                htmlFile.write( \
                    '<img src="' +
                    odpName+"/"+questionFileNames[position] + '.' + imageFileSuffix +
                    '" style="border:0px"><br>\n')
            # First page
            elif position==0:
                htmlFile.write( \
                    '<a href="' +
                    odpName+"/"+questionFileNames[position+1] +
                    '.htm">')
                htmlFile.write( \
                    '<img src="' +
                    odpName +"/" + questionFileNames[position] + '.' + imageFileSuffix +
                    '" style="border:0px"></a><br>\n')
            # Rest of pages
            else:
                htmlFile.write( \
                    '<a href="' +
                    questionFileNames[position+1] +
                    '.htm">')
                htmlFile.write( \
                    '<img src="' +
                    questionFileNames[position] + '.' + imageFileSuffix +
                    '" style="border:0px"></a><br>\n')

            # Add source link, if any
            if 0<len(question.sourceLink):
                htmlFile.write( \
                    '<a href="' + question.sourceLink + '">' + question.sourceLink + '</a><br>\n')

        else:
            htmlFile.write("<br><br><hr><br><center>\n")
            if len(question.linkToShow)>0:
                # src but no link
                htmlFile.write( \
                    '<img src="' +
                    question.linkToShow +
                    '" style="border:0px"><br>\n')
            htmlFile.write("""<table width="400" style="text-align:left"><tbody>
<tr><td>""")
            htmlFile.write(" ".join(question.questionTexts)+ "</td></tr>\n" )

            for answerNumber, answer in enumerate(question.answers):
                if len(answer.answerText)>0:
                    htmlFile.write('<tr><td><div id="a'+
                    str(answerNumber)+
                    '"><a href="javascript:respond'+
                    str(answerNumber)+
                    '();">'+
                    answer.answerText +
                    '</a></div></td></tr>\n')
            htmlFile.write("""</tbody>
</table>
</center><br><hr>""")

        # include audio
        # First page
        if position==0:
            pathToAudio = odpName+'/'+questionFileNames[position]
        else:
            pathToAudio = questionFileNames[position]
        # For Safari
        htmlFile.write( \
            '<p id="playaudio">' +
            '<audio controls autoplay><source src="' +
            pathToAudio +
            '.mp3" />')
        # For Firefox
        htmlFile.write( \
            '<source src="' +
            pathToAudio +
            '.ogg" />\n')
        # For others
        htmlFile.write( \
            'Your browser does not support the <code>audio</code> element.\n</audio>\n')
        htmlFile.write( \
            '</p>\n')
        # For Internet Explorer
        htmlFile.write( \
            '<!--[if lte IE 8]>\n' +
            '<script>\n' +
            'document.getElementById("playaudio").innerHTML=' + "'" +
            '<embed src="' +
            pathToAudio +
            '.mp3" autostart="true">' + "'" + ';\n' +
            '</script>\n' +
            '<![endif]-->\n')

        htmlFile.write('</center>' + "\n")
        htmlFile.write('</body>\n</html>\n')
        htmlFile.close()


sequence = scriptParser.parseTxtFile(odpFileSubdirectory+os.sep+"script.txt")
makeConvert(sequence)
os.chdir(odpFileDirectory)
p = subprocess.Popen('"'+odpFileDirectory+os.sep+'convert.bat"',shell=True).wait()
audioFileTimes = fetchAudioFileTimes()
writeHtml(sequence, audioFileTimes)


## Step 3 - create makeVid.bat
os.chdir(odpFileSubdirectory)
dir = os.listdir(odpFileSubdirectory)
ogg = [file for file in dir if file.lower().endswith(".ogg")]
oggDict = {}
for file in ogg:
    # Parse out file name stem (which includes number) and imageFileSuffix
    (stem, audioFileSuffix) = file.split(".")

    # Parse out just number (num) and imageFilePrefix
    if stem.startswith("Slide"):
        numberPart = file[5:].split(".")[0]
        if numberPart.isdigit():
            oggDict[int(numberPart)] = file
    else:
        # imgXX.ogg
        numberPart = file[3:].split(".")[0]
        if numberPart.isdigit():
            oggDict[int(file[3:].split(".")[0])] = file
sortedOgg = oggDict.values()
times = []
for file in sortedOgg:
    # soxi -D returns the duration in seconds of the audio file as a float
    if sys.platform.startswith("win"):
        # Unfortunately, there is a requirement that soxi (with an implict .exe)
        # be the command to check audio file duration in Win32
        # but soxi is the name of the unix version of this utility
        # So we need to delete the (unix) file called soxi so the command line call
        # to soxi will run soxi.exe
        if os.path.isfile(savePath+os.sep+"soxi"):
            os.remove(savePath+os.sep+"soxi")
        command = [savePath+os.sep+"soxi","-D",odpFileSubdirectory+os.sep+file]
    elif sys.platform.startswith("darwin"):
        if os.path.isfile(savePath+os.sep+"soxi"):
            command = [savePath+os.sep+"soxi","-D",odpFileSubdirectory+os.sep+file]
        elif os.path.isfile(savePath+os.sep+"Contents/Resources/soxi"):
            command = [savePath+os.sep+"Contents/Resources/soxi","-D",odpFileSubdirectory+os.sep+file]
        else:
            command = ["soxi","-D",odpFileSubdirectory+os.sep+file]
    else:
        command = ["soxi","-D",odpFileSubdirectory+os.sep+file]
    process = subprocess.Popen(command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
    output = process.communicate()
    retcode = process.poll()
    if retcode:
        print "No time available"
    times.append(float(output[0].strip()))

# Create makeVid.bat in odpFileDirectory for Windows
f = open(odpFileDirectory+os.sep+"makeVid.bat","w")
os.chmod(odpFileDirectory+os.sep+"makeVid.bat",stat.S_IRWXU)

if sys.platform.startswith("win"):
    # find out if mklink is available
    mklinkAvailable = False
    if os.path.isfile("win32_mklink_test"):
        subprocess.Popen(["del","win32_mklink_test"],shell=True)
    os.chdir(odpFileDirectory)
    subprocess.Popen(["mklink","/h","win32_mklink_test","convert.bat"],shell=True).wait()
    if os.path.isfile("win32_mklink_test"):
        mklinkAvailable = True
        subprocess.Popen(["del","win32_mklink_test"],shell=True)

    f.write("echo off\ncls\n")
    f.write("if exist output.avi (del output.avi)\n")
    catCommand = "copy /b"
    for i, file in enumerate(sortedOgg):
        stem, suffix = file.split(".")
        # Add the slide video to the list of videos to be concatenated
        if i==0:
            catCommand += " "+stem+".avi"
        else:
            catCommand += " + "+stem+".avi"
        tenthsOfSeconds = int(math.floor(times[i]*10))
        # If we are on the last slide, add enough frames
        # to give audio time to finish
        if sortedOgg[i]==sortedOgg[-1]:
            tenthsOfSeconds += 20
        # Make a symlink to the slide image for each second the audio runs
        # Only 999 symlinks are allowed per image, so, if there are more
        # than this number, we need to also make additional copies of the
        # slide image to link to
        for j in range(tenthsOfSeconds):
            if ((j > 0) and (j % 900 == 0)):
                f.write("copy "+stem+'.jpg '+stem+str(j)+'.jpg\n')
        extraStem = ""
        for j in range(tenthsOfSeconds):
            if ((j > 0) and (j % 900 == 0)):
                extraStem = str(j)
            if mklinkAvailable:
                f.write("mklink /h "+stem+'_'+str(j).zfill(5)+'.jpg '+stem+extraStem+'.jpg\n')
            else:
                f.write("copy "+stem+'.jpg '+stem+'_'+str(j).zfill(5)+'.jpg\n')
        # Convert the images to a video of that slide with voice over
        # NOTE: Little trick here -- Windows wants to substitute the batch file name
        #       into %0 so we use %1 and pass %0 as the first parameter
        f.write('"'+savePath+os.sep+'ffmpeg" -i '+stem+'.mp3 -r 10 -i "'+stem+'_%15d.jpg" -ab 64k '+stem+".avi\n")
        # Delete the symlinks
        for j in range(tenthsOfSeconds):
            f.write("del "+stem+'_'+str(j).zfill(5)+'.jpg\n')
        # Delete any extra copies
        for j in range(tenthsOfSeconds):
            if ((j > 0) and (j % 900 == 0)):
                f.write("del "+stem+str(j)+'.jpg\n')
    # Add an output file name for the concatenation
    catCommand += " temp.avi\n"

    if os.path.isfile(savePath+os.sep+"mencoder.exe"):
        catCommand += '"'+savePath+os.sep+'mencoder.exe" temp.avi -o output.avi -forceidx -ovc copy -oac copy\n'
    else:
        catCommand += "mencoder.exe temp.avi -o output.avi -forceidx -ovc copy -oac copy\n"
    f.write(catCommand)
    # Delete all the single slide videos
    for file in sortedOgg:
        stem, suffix = file.split(".")
        f.write('del '+stem+'.avi\n')
    f.close()

elif sys.platform.startswith("darwin"):
    # For Mac OSX
    # ffmpeg -i Slide1.mp3 -r 1 -i Slide1_%03d.png -ab 64k output.mp4
    f.write("clear\n")
    f.write("if [ -f output.mp4 ]\n")
    f.write("then rm output.mp4\n")
    f.write("fi\n")
    if os.path.isfile(savePath+os.sep+"MP4Box"):
        # for uncompiled run
        catCommand = '"'+savePath+os.sep+'MP4Box"'
    elif os.path.isfile(savePath+os.sep+"Contents/Resources/MP4Box"):
        # for compiled run
        catCommand = '"'+savePath+os.sep+'Contents/Resources/MP4Box"'
    else:
        # for when MP4Box is not distributed but is installed
        catCommand = "MP4Box"
    # save another copy for subsequent cat lines if more than 20 slides
    catCommand2 = catCommand
    tempFilesToDelete = []
    for i, file in enumerate(sortedOgg):
        stem, suffix = file.split(".")
        # Add the slide video to the list of videos to be concatenated
        catCommand += " -cat "+stem+".mp4"
        if ((i>0) and (i % 18 == 0)):
            tempFilesToDelete.append("temp"+ str(i) +".mp4")
            # add a temp.mp4 for output and then input on next line
            catCommand += " temp" + str(i) +".mp4\n"+catCommand2+" -cat temp" + str(i) +".mp4"
        tenthsOfSeconds = int(math.floor(times[i]*10))
        # If we are on the last slide, add enough frames
        # to give audio time to finish
        if sortedOgg[i]==sortedOgg[-1]:
            tenthsOfSeconds += 20
        # Make a symlink to the slide image for each second the audio runs
        for j in range(tenthsOfSeconds):
            # ln -s Slide2.png Slide2_001.png
            f.write("ln -s "+stem+'.png '+stem+'_'+str(j).zfill(5)+'.png\n')
        f.write('"'+savePath+os.sep+'ffmpeg" -i '+stem+'.mp3 -r 10 -i "'+stem+'_%05d.png" -ab 64k '+stem+".mp4\n")
        # Delete the symlinks
        for j in range(tenthsOfSeconds):
            f.write("rm "+stem+'_'+str(j).zfill(5)+'.png\n')
    # Add an output file name for the concatenation
    catCommand += " output.mp4\n"
    f.write(catCommand)
    # Delete all the single slide videos
    for file in sortedOgg:
        stem, suffix = file.split(".")
        f.write('rm '+stem+'.mp4\n')
    for file in tempFilesToDelete:
        f.write('rm '+file+"\n")
    f.close()

else:
    # For Linux
    # ffmpeg -i Slide1.mp3 -r 1 -i Slide1_%03d.png -ab 64k output.mp4
    f.write("clear\n")
    f.write("if [ -f output.mp4 ]\n")
    f.write("then rm output.mp4\n")
    f.write("fi\n")

    # We need to do this:
    #   cat img0.avi img1.avi > output.avi
    #   mencoder output.avi -o final.avi -forceidx -ovc copy -oac copy
    catCommand = "cat "
    catCommand2= "cat "

    # save another copy for subsequent cat lines if more than 20 slides
    tempFilesToDelete = []
    for i, file in enumerate(sortedOgg):
        stem, suffix = file.split(".")
        # Add the slide video to the list of videos to be concatenated
        catCommand += " " + stem+".avi"
        if ((i>0) and (i % 18 == 0)):
            tempFilesToDelete.append("temp"+ str(i) +".avi")
            # add a temp.mp4 for output and then input on next line
            catCommand += " temp" + str(i) +".avi\n"+catCommand2+" temp" + str(i) +".avi"
        tenthsOfSeconds = int(math.floor(times[i]*10))
        # If we are on the last slide, add enough frames
        # to give audio time to finish
        if sortedOgg[i]==sortedOgg[-1]:
            tenthsOfSeconds += 20
        # Make a symlink to the slide image for each second the audio runs
        for j in range(tenthsOfSeconds):
            # ln -s Slide2.png Slide2_001.png
            f.write("ln -s "+stem+'.png '+stem+'_'+str(j).zfill(5)+'.png\n')
        f.write('ffmpeg -i '+stem+'.mp3 -r 10 -i "'+stem+'_%05d.png" -ab 64k '+stem+".avi\n")
        # Delete the symlinks
        for j in range(tenthsOfSeconds):
            f.write("rm "+stem+'_'+str(j).zfill(5)+'.png\n')
    # Add an output file name for the concatenation
    catCommand += " > output.avi\n mencoder output.avi -o final.avi -forceidx -ovc copy -oac copy\n"
    f.write(catCommand)
    # Delete all the single slide videos
    for file in sortedOgg:
        stem, suffix = file.split(".")
        f.write('rm '+stem+'.avi\n')
    for file in tempFilesToDelete:
        f.write('rm '+file+"\n")
    f.close()

# Run the makeVid.bat file with %0 as the first parameter
os.chdir(odpFileSubdirectory)
if sys.platform.startswith("win"):
    p = subprocess.Popen([odpFileDirectory+os.sep+'makeVid.bat',"%0"],shell=True).wait()
    webbrowser.open_new_tab(odpFileDirectory+os.sep+odpName+'.htm')
else:
    p = subprocess.Popen([odpFileDirectory+os.sep+"makeVid.bat"],shell=True).wait()
    p = subprocess.Popen('open "'+odpFileDirectory+os.sep+odpName+'.htm"', shell=True).pid
os.chdir(savePath)


