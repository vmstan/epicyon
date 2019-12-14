__filename__ = "question.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.1.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import os
from utils import locatePost
from utils import loadJson
from utils import saveJson

def questionUpdateVotes(baseDir: str,nickname: str,domain: str,replyJson: {}) -> {}:
    """ For a given reply update the votes on a question
    Returns the question json object if the vote totals were changed
    """
    if not replyJson.get('object'):
        return None
    if not isinstance(replyJson['object'], dict):
        return None
    if not replyJson['object'].get('inReplyTo'):
        return None
    if not replyJson['object']['inReplyTo']:
        return None
    if not replyJson['object'].get('content'):
        return None
    inReplyTo=replyJson['object']['inReplyTo']
    questionPostFilename=locatePost(baseDir,nickname,domain,inReplyTo)
    if not questionPostFilename:
        return None
    questionJson=loadJson(questionPostFilename)
    if not questionJson:
        return None
    if not questionJson.get('object'):
        return None
    if not isinstance(questionJson['object'], dict):
        return None
    if not questionJson['object'].get('type'):
        return None
    if questionJson['type']!='Question':
        return None
    if not questionJson['object'].get('oneOf'):
        return None
    if not isinstance(questionJson['object']['oneOf'], list):
        return None
    if not questionJson['object'].get('content'):
        return None
    content=replyJson['object']['content']
    # does the reply content match any possible question option?
    foundAnswer=None
    for possibleAnswer in questionJson['object']['oneOf']:
        if not possibleAnswer.get('name'):
            continue
        if possibleAnswer['name'] in content:
            foundAnswer=possibleAnswer
            break
    if not foundAnswer:
        return None
    # update the voters file
    votersFileSeparator=';;;'
    votersFilename=questionPostFilename.replace('.json','.voters')
    if not os.path.isfile(votersFilename):
        # create a new voters file
        votersFile=open(votersFilename, "w")
        if votersFile:
            votersFile.write(replyJson['actor']+votersFileSeparator+foundAnswer+'\n')
            votersFile.close()
    else:
        if replyJson['actor'] not in open(votersFilename).read():
            # append to the voters file
            votersFile=open(votersFilename, "a+")
            if votersFile:
                votersFile.write(replyJson['actor']+votersFileSeparator+foundAnswer+'\n')
                votersFile.close()
        else:
            # change an entry in the voters file
            with open(votersFilename, "r") as votersFile:
                lines = votersFile.readlines()
                newlines=[]
                saveVotersFile=False
                for voteLine in lines:
                    if voteLine.startswith(replyJson['actor']+votersFileSeparator):
                        newVoteLine=replyJson['actor']+votersFileSeparator+foundAnswer+'\n'
                        if voteLine==newVoteLine:
                            break
                        saveVotersFile=True
                        newlines.append(newVoteLine)
                    else:
                        newlines.append(voteLine)
                if saveVotersFile:
                    with open(votersFilename, "w") as votersFile:
                        for voteLine in newlines:
                            votersFile.write(voteLine)
                else:
                    return None
    # update the vote counts
    questionTotalsChanged=False
    for possibleAnswer in questionJson['object']['oneOf']:
        if not possibleAnswer.get('name'):
            continue
        totalItems=0
        with open(votersFilename, "r") as votersFile:
            lines = votersFile.readlines()
            for voteLine in lines:
                if voteLine.endswith(votersFileSeparator+possibleAnswer['name']+'\n'):
                    totalItems+=1                    
        if possibleAnswer['replies']['totalItems']!=totalItems:
            possibleAnswer['replies']['totalItems']=totalItems
            questionTotalsChanged=True
    if not questionTotalsChanged:
        return None
    # save the question with altered totals
    saveJson(questionJson,questionPostFilename)
    return questionJson
