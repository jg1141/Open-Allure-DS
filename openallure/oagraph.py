# Apply buzhug data to color graph
def main():
    from buzhug import Base
    try:
        db = Base('oadb').open()
    except IOError:
        print('Error opening oadb')
        
    import os
    from qsequence import QSequence
    #seq = QSequence(filename='welcome.txt')
    #seq = QSequence(filename='sky.txt')
    #seq = QSequence(filename='http://openallure.wikia.com/wiki/Evaluation_of_Software_Architecture_Structural_Quality')
    #seq = QSequence(filename='Structural Quality of Software Architectures.txt')
    seq = QSequence(filename='http://openallureds.ning.com/profiles/blogs/open-allure-script-for-the')
    
    #showResponses = True
    #showText = True

def wrapWords(string, wordWidth):
    words = string.split(' ')
    wordCount = len(words)
    onWord = 0
    line = ''
    lineCount = 0
    for word in words:
        line = line + word
        onWord += 1
        if word and onWord < wordCount:
            if word[-1].isalpha():
                lineCount += 1
                if lineCount > 6:
                    line = line + '\\n'
                    lineCount = 0
                else:
                    line = line + ' '
            else:
                line = line + '\\n'
                lineCount = 0
    return line
        
def oaMetaGraph(db):
    f = open('oagraph.dot', 'w')
    f.write("digraph G {\n")
    records = [record for record in db]
    uniqueSequenceSet = sorted(set([record.url for record in records]))
    uniqueSequences = []
    for seq in uniqueSequenceSet:
        uniqueSequences.append(seq)
    for snum, seq in enumerate(uniqueSequences):
        f.write("S" + str(snum) + ' [label="' + seq + '"];\n')
    links = [(record.url, record.cmd) for record in db if (record.cmd in uniqueSequences)]
    uniqueLinkSet = set(links)
    for link in uniqueLinkSet:
        f.write("S" + str(uniqueSequences.index(link[0])) + ' -> ' \
        + "S" + str(uniqueSequences.index(link[1]))  + ';\n')
    f.write("}")
    f.close()
    # Make sure file is finished flushing to disk
    f = open('oagraph.dot', 'r')
    f.close()
    
def oagraph(seq,db,url,showText,showResponses,showLabels):
    records = [record for record in db if record.url == url]
    # The '+ 1' in the following lines translates from the 0 based count in oadb
    # to the 1 based counting in the .dot graph
    #print(records)
    questionsTouched = ["Q" + str(record.q + 1) for record in records if not record.q == None]
    answersTouched = ["Q" + str(record.q + 1) + "A" + str(record.a + 1) for record in records if not record.a == None]
    responsesTouched = ["Q" + str(record.q + 1) + "R" + str(record.a + 1) for record in records if not record.a == None]
    #print(questionsTouched, answersTouched, responsesTouched)
    f = open('oagraph.dot', 'w')
    f.write("digraph G {\n")
    for qnum, question in enumerate( seq.sequence ):
        # Count from 1 not 0
        qnum1 = qnum + 1
        # Add question to graph with ID of Q<number>
        colorString = ''
        labelString = ''
        if showText:
            labelText = wrapWords("\\n".join(question[0]),8)
        else:
            labelText = "Q" + str(qnum1)
        if "Q" + str(qnum1) in questionsTouched:
            colorString = 'style=filled colorscheme=pastel13 color=1 '
        else:
            colorString = 'style=filled colorscheme=greys3 color=3 '
        if showLabels:
           labelString = 'fontcolor=white label="' + labelText + '"'
        else:
           labelString = 'label=""'
        f.write("Q" + str(qnum1) + ' [' + colorString + labelString + '];\n')
        
        # Add answers to graph with ID of Q<number>A<number>
        for anum, answer in enumerate( question[1] ):
            # Count from 1 not 0
            anum1 = anum + 1
            colorString = ''
            labelString = ''
            if "Q" + str(qnum1) + "A" + str(anum1) in answersTouched:
                colorString = 'style=filled colorscheme=pastel13 color=2 '
            else:
                colorString = 'style=filled colorscheme=greys3 color=2 '
            if showText:
                if question[6][anum]:
                    labelText = u'[input]'
                else:
                    labelText = question[1][anum]
            else:
                labelText = "Q" + str(qnum1) + "A" + str(anum1)
            if showLabels:
               labelString = 'fontcolor=black label="' + labelText + '"'
            else:
               labelString = 'label=""'
            f.write("Q" + str(qnum1) + "A" + str(anum1) + \
            ' [' + colorString + labelString + '];\n')
            # link INTO answer from question with and without arrow head
            # depending on whether there is a link OUT
            if question[3][anum] > 0 or question[4][anum]:
                # with arrowhead
                if question[1][anum].startswith('[next]'):
                    f.write("Q" + str(qnum1) + ":w -> " + \
                    "Q" + str(qnum1) + "A" + str(anum1) + ':n;\n')
                elif question[1][anum].startswith('[') or question[4][anum]:
                    f.write("Q" + str(qnum1) + ":e -> " + \
                    "Q" + str(qnum1) + "A" + str(anum1) + ':n;\n')
                else:
                    f.write("Q" + str(qnum1) + " -> " + \
                    "Q" + str(qnum1) + "A" + str(anum1) + ';\n')
            else:
                # with no arrowhead
                f.write("Q" + str(qnum1) + " -> " + \
                "Q" + str(qnum1) + "A" + str(anum1) + \
                ' [colorscheme=greys3 color=2 dir=none];\n')
            
            # Add response to graph with ID of Q<number>R<number>, if any
            if anum < len(question[2]) and \
            question[2][anum] and showResponses == True:
                colorString = ''
                if "Q" + str(qnum1) + "R" + str(anum1) in responsesTouched:
                    colorString = 'style=filled colorscheme=pastel13 color=3 '
                else:
                    colorString = u'style=filled colorscheme=greys3 color=1 '
                if showText:
                    labelText = wrapWords(question[2][anum], 6) + \
                    (u'\\n' + question[4][anum]).rstrip()
                else:
                    labelText = "Q" + str(qnum1) + "R" + str(anum1)
                if showLabels:
                   labelString = 'label="' + labelText + '"'
                else:
                   labelString = 'label=""'
                f.write(u"Q" + str(qnum1) + u"R" + str(anum1) + \
                u' [' + colorString + labelString + u'];\n')
                # link INTO response with and without arrow head
                if question[3][anum] > 0 or question[4][anum] or question[6][anum]:
                    # link INTO response with arrow head
                    if question[4][anum]:
                        f.write("Q" + str(qnum1) + "A" + str(anum1) + \
                        ":e -> " + \
                        "Q" + str(qnum1) + "R" + str(anum1) + ':n;\n')
                    else:
                        f.write("Q" + str(qnum1) + "A" + str(anum1) + \
                        " -> " + \
                        "Q" + str(qnum1) + "R" + str(anum1) + ';\n')
                    # link OUT of respose to next question 
                    if not question[6][anum] and question[3][anum] > 0:
                        f.write("Q" + str(qnum1) + "R" + str(anum1) + " -> " \
                        + "Q" + str(qnum1 + question[3][anum]) + ';\n')
                else:
                    # link INTO response with no arrow head
                    f.write("Q" + str(qnum1) + "A" + str(anum1) + \
                    " -> " + \
                    "Q" + str(qnum1) + "R" + str(anum1) + \
                    ' [colorscheme=greys3 color=2 dir=none];\n')
            else:
                # link OUT of answer to next question if not [input]
                if not question[1][anum] == u'[input]' and question[3][anum] > 0:
                    f.write("Q" + str(qnum1) + "A" + str(anum1) + " -> " \
                    + "Q" + str(qnum1 + question[3][anum]) + ';\n')
    f.write("}")
    f.close()
    # Make sure file is finished flushing to disk
    f = open('oagraph.dot', 'r')
    f.close()
    

if __name__ == "__main__":
    test = True
    if test:
        import os
        os.system("/Applications/Graphviz.app/Contents/MacOS/Graphviz oagraph.dot")
    else:
        pass
        
        
