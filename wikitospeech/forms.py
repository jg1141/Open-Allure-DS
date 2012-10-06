# forms.py
import urllib

def scriptInputFormWithErrorMessage(version, errorMessage):
    return '''<html><head><title>SlideSpeech {0}</title></head>
              <body><br><br><hr><br><center><form action="getScriptName" method="GET">
            SlideSpeech Script:<br>
            <input type="text" name="name" size="80" /><br>
            <input type="submit" value="Open"/><br><br>
            </form>
            <small>Version {0}<br><form action="SlideSpeech_Exit_Complete" method="GET">
            <input type="submit" value="Exit"/><br><br>
            </form><br>
            <italic>{1}</italic></center><br><hr></body></html>'''.format(version, errorMessage)

def loading(name):
    return "Loading script: " + name + " ..."

def showQuestion(q, qnum):
    questionString = ""
    for questionText in q.questionTexts:
        questionString = questionString + " " + questionText
    answerStringBase = '<tr><td><a href="http://localhost:8080/nextSlideFromAnswer'
    answerString = ""
    answerNumber = 0
    for a in q.answers:
        if len(a.answerText)>0:
            if a.visited == False:
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '?q=' + str(qnum) +'">' + a.answerText + "</a></td></tr>\n"
            else:
                # Visited = True, Change text color to gray
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '"><span style="color:#CCCCCC">' + \
                     a.answerText + "</span></a></td></tr>\n"
            answerNumber += 1

    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<br><br><hr><br><center>
<table width="400" style="text-align:left"><tbody>
<tr><td>""" + \
questionString + "</td></tr>\n" + \
answerString + \
"""
</tbody>
</table>
</center><br><hr>
</body>
</html>
"""
def showWebsite(q):
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
<script type="text/javascript">
<!--
window.location = "http://www.google.com/"
//-->
</script>
</head>
<body></body>
</html>
"""

def showQuestionAndWebsiteLink(q):
    questionString = ""
    for questionText in q.questionTexts:
        questionString = questionString + " " + questionText
    answerStringBase = '<tr><td><a href="http://localhost:8080/nextSlideFromAnswer'
    answerString = ""
    answerNumber = 0
    for a in q.answers:
        if len(a.answerText)>0:
            if a.visited == False:
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '">' + a.answerText + "</a></td></tr>\n"
            else:
                # Visited = True, Change text color to gray
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '"><span style="color:#CCCCCC">' + \
                     a.answerText + "</span></a></td></tr>\n"
            answerNumber += 1

    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<br><br><hr><br><center>
<table width="400" style="text-align:left"><tbody>
<tr><td><a href=""" + '"' +\
q.linkToShow + '">' + \
questionString + "</a></td></tr>\n" + \
answerString + \
"""
</tbody>
</table>
</center><br><hr>
</body>
</html>
"""

def showQuestionAndWebsite(q, qnum):
    questionString = ""
    for questionText in q.questionTexts:
        questionString = questionString + " " + questionText
    answerStringBase = '<tr><td><a href="http://localhost:8080/nextSlideFromAnswer'
    answerString = ""
    answerNumber = 0
    for a in q.answers:
        if len(a.answerText)>0:
            if a.visited == False:
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '?q=' + str(qnum) + '">' + a.answerText + "</a></td></tr>\n"
            else:
                # Visited = True, Change text color to gray
                answerString = answerString + answerStringBase + \
                     str(answerNumber) + '?q=' + str(qnum) + '"><span style="color:#CCCCCC">' + \
                     a.answerText + "</span></a></td></tr>\n"
            answerNumber += 1

    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
  <script>
  window.open('""" + \
q.linkToShow + \
"""','_newtab');
  </script>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<br><br><hr><br><center>
<table width="400" style="text-align:left"><tbody>
<tr><td>""" + \
questionString + "</td></tr>\n" + \
answerString + \
"""
<tr><td><a href="http://localhost:8080/nextSlide">[next]</a></td></tr>
</tbody>
</table>
</center><br><hr>
</body>
</html>
"""

def showJPGSlideWithQuestion(jpgName, q):
    answerStringBase = '<tr><td><a href="http://localhost:8080/nextSlideFromAnswer'
    answerString = ""
    answerNumber = 0
    for a in q.answers:
        if len(a.answerText)>0:
            answerString = answerString + answerStringBase + \
                 str(answerNumber) + '">' + a.answerText + "</a></td></tr>\n"
            answerNumber += 1
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/transitional.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<center>
<a href="http://localhost:8080/nextSlide"><img src=""" + '"' + jpgName + '"' + """ width="400" height="300"></a>
<hr><br>
<table width="400" style="text-align:left"><tbody>
<tr><td>""" + \
q.questionTexts[0] + "</td></tr>\n" + \
answerString + \
"""
</tbody>
</table>
</center><br><hr>
</body>
</html>
"""

def showScript(name, text):
    return "Showing script: " + name + " ..." + text

def showJPGSlide(jpgName):
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/transitional.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Wiki-to-Speech</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<center>
<a href="http://localhost:8080/nextSlide"><img src=""" + '"' + jpgName + '"' + """ width="800" height="600"></a>
</center>
</body>
</html>
"""
def showPDFSlide(pdfName):
    urlName = urllib.urlencode({"url":pdfName})
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/transitional.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>Slide 1</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<a href="http://localhost:8080/nextSlide">Next Slide</a><br>
<center>
<center>
<iframe src="http://docs.google.com/viewer?""" + urlName + """&embedded=true" width="600" height="780" style="border: none;"></iframe>
</center>
</body>
</html>
"""
#http%3A%2F%2Fwww.google.com%2Fgoogle-d-s%2FdocsQuickstartGuide.pdf
#<a href="http://localhost:8080/nextSlide"><a href=""" + '"' + jpegName + '"' + """></a>

def showDHTML():
    return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>Test</title>
    <style type="text/css">
      h2 {background-color: green; width: 100%}
      a {font-size: larger; background-color: red;}
      a:hover {background-color: gold}
      #example1 {display: none; margin: 3%; padding: 4%; background-color: limegreen}
    </style>
    <script type="text/javascript">
      function changeDisplayState (id) {
        d=document.getElementById("showhide");
        e=document.getElementById(id);
        if (e.style.display == 'none' || e.style.display == "") {
          e.style.display = 'block';
          d.innerHTML = 'Hide example..............';
        } else {
          e.style.display = 'none';
          d.innerHTML = 'Show example';
        }
      }
    </script>
  </head>
  <body>

<a href="http://localhost:8080/nextSlide">Next Slide</a><br>
    <h2>How to use a DOM function</h2>
    <div><a id="showhide" href="javascript:changeDisplayState('example1')">Show example</a></div>
    <div id="example1">
      This is the example.
      (Additional information, which is only displayed on request)...
    </div>
    <div>The general text continues...</div>
  </body>
</html>
"""

def showSWF():
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/transitional.dtd">
<html>
<head>
  <meta HTTP-EQUIV=CONTENT-TYPE CONTENT="text/html; charset=utf-8">
  <title>SWF Slide</title>
</head>
<body text="#000000" bgcolor="#FFFFFF" link="#000080" vlink="#0000CC" alink="#000080">
<center>
<a href="http://localhost:8080/nextSlide">Next Slide 2</a><br>
<object width="550" height="400">
<param name="movie" value="http://www.tizag.com/pics/example.swf">
<embed src="http://www.tizag.com/pics/example.swf" width="550" height="400">
</embed>
</object>

</center>
  </body>
</html>
"""