class Sequence(object):
    """Object containing a series of questions/statements"""
    def __init__(self):
        self.sequence = []
        self.onQuestion = 0
        self.questionTagMap = {}
        self.rules = []

class Question(object):
    """Object containing a question/statement with optional answers"""
    def __init__(self):
        self.tag = ""
        self.questionTexts = []
        self.answers = []
        self.language = ""
        self.linkToShow = ""
        self.pathToImageFiles = ""
        self.sourceLink = "" # For citations

class Answer(object):
    """Object containing an answer with optional response"""
    def __init__(self):
        self.answerText = ""
        self.answerSideLink = ""
        self.sticky = False
        self.input = False
        self.token = ""
        self.responseText = ""
        self.responseSideLink = ""
        self.action = 0
        self.visited = False
        self.answerLanguage = ""
        self.responseLanguage = ""

class Rule(object):
    """Object containing a rule"""
    def __init__(self):
        self.rulePattern = None
        self.ruleType = ""
        self.ruleName = ""
        self.ruleResponse = ""


