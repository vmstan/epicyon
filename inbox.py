__filename__ = "inbox.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
import os
import datetime
import time
import json
import commentjson
from shutil import copyfile
from utils import urlPermitted
from utils import createInboxQueueDir
from httpsig import verifyPostHeaders
from session import createSession
from session import getJson
from follow import receiveFollowRequest
from pprint import pprint
from cache import getPersonFromCache
from cache import storePersonInCache

def getPersonPubKey(session,personUrl: str,personCache: {},debug: bool) -> str:
    if not personUrl:
        return None
    personUrl=personUrl.replace('#main-key','')
    personJson = getPersonFromCache(personUrl,personCache)
    if not personJson:
        if debug:
            print('DEBUG: Obtaining public key for '+personUrl)
        asHeader = {'Accept': 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'}
        personJson = getJson(session,personUrl,asHeader,None)
        if not personJson:
            return None
    pubKey=None
    if personJson.get('publicKey'):
        if personJson['publicKey'].get('publicKeyPem'):
            pubKey=personJson['publicKey']['publicKeyPem']
    else:
        if personJson.get('publicKeyPem'):
            pubKey=personJson['publicKeyPem']

    if not pubKey:
        if debug:
            print('DEBUG: Public key not found for '+personUrl)

    storePersonInCache(personUrl,personJson,personCache)
    return pubKey

def inboxMessageHasParams(messageJson: {}) -> bool:
    """Checks whether an incoming message contains expected parameters
    """
    expectedParams=['type','to','actor','object']
    for param in expectedParams:
        if not messageJson.get(param):
            return False
    return True

def inboxPermittedMessage(domain: str,messageJson: {},federationList: []) -> bool:
    """ check that we are receiving from a permitted domain
    """
    testParam='actor'
    if not messageJson.get(testParam):
        return False
    actor=messageJson[testParam]
    # always allow the local domain
    if domain in actor:
        return True

    if not urlPermitted(actor,federationList):
        return False

    if messageJson.get('object'):
        if messageJson['object'].get('inReplyTo'):
            inReplyTo=messageJson['object']['inReplyTo']
            if not urlPermitted(inReplyTo, federationList):
                return False

    return True

def validPublishedDate(published) -> bool:
    currTime=datetime.datetime.utcnow()
    pubDate=datetime.datetime.strptime(published,"%Y-%m-%dT%H:%M:%SZ")
    daysSincePublished = (currTime - pubTime).days
    if daysSincePublished>30:
        return False
    return True

def savePostToInboxQueue(baseDir: str,httpPrefix: str,nickname: str, domain: str,postJson: {},host: str,headers: str) -> str:
    """Saves the give json to the inbox queue for the person
    keyId specifies the actor sending the post
    """
    if ':' in domain:
        domain=domain.split(':')[0]
    if not postJson.get('id'):
        return None
    postId=postJson['id'].replace('/activity','')

    currTime=datetime.datetime.utcnow()
    published=currTime.strftime("%Y-%m-%dT%H:%M:%SZ")

    inboxQueueDir=createInboxQueueDir(nickname,domain,baseDir)

    handle=nickname+'@'+domain
    destination=baseDir+'/accounts/'+handle+'/inbox/'+postId.replace('/','#')+'.json'
    if os.path.isfile(destination):
        # inbox item already exists
        return None
    filename=inboxQueueDir+'/'+postId.replace('/','#')+'.json'

    sharedInboxItem=False
    if nickname=='sharedinbox':
        sharedInboxItem=True
        
    newQueueItem = {
        'sharedInbox': sharedInboxItem,
        'published': published,
        'host': host,
        'headers': headers,
        'post': postJson,
        'filename': filename,
        'destination': destination
    }
    
    with open(filename, 'w') as fp:
        commentjson.dump(newQueueItem, fp, indent=4, sort_keys=False)
    return filename

def runInboxQueue(baseDir: str,httpPrefix: str,personCache: {},queue: [],domain: str,port: int,useTor: bool,federationList: [],debug: bool) -> None:
    """Processes received items and moves them to
    the appropriate directories
    """
    currSessionTime=int(time.time())
    sessionLastUpdate=currSessionTime
    session=createSession(domain,port,useTor)
    if debug:
        print('DEBUG: Inbox queue running')

    while True:
        if len(queue)>0:
            currSessionTime=int(time.time())
            if currSessionTime-sessionLastUpdate>1200:
                session=createSession(domain,port,useTor)
                sessionLastUpdate=currSessionTime

            # oldest item first
            queue.sort()
            queueFilename=queue[0]
            if not os.path.isfile(queueFilename):
                if debug:
                    print("DEBUG: queue item rejected becase it has no file: "+queueFilename)
                queue.pop(0)
                continue

            # Load the queue json
            with open(queueFilename, 'r') as fp:
                queueJson=commentjson.load(fp)

            # Try a few times to obtain the public key
            pubKey=None
            keyId=None
            for tries in range(8):
                keyId=None
                signatureParams=queueJson['headers'].split(',')
                for signatureItem in signatureParams:
                    if signatureItem.startswith('keyId='):
                        if '"' in signatureItem:
                            keyId=signatureItem.split('"')[1]
                            break
                if not keyId:
                    if debug:
                        print('DEBUG: No keyId in signature: '+queueJson['headers']['signature'])
                    os.remove(queueFilename)
                    queue.pop(0)
                    continue

                pubKey=getPersonPubKey(session,keyId,personCache,debug)
                if pubKey:
                    print('DEBUG: public key: '+str(pubKey))
                    break
                    
                if debug:
                    print('DEBUG: Retry '+str(tries+1)+' obtaining public key for '+keyId)
                time.sleep(5)

            if not pubKey:
                if debug:
                    print('DEBUG: public key could not be obtained from '+keyId)
                os.remove(queueFilename)
                queue.pop(0)
                continue

            # check the signature
            verifyHeaders={
                'host': queueJson['host'],
                'signature': queueJson['headers']
            }
            if not verifyPostHeaders(httpPrefix, \
                                     pubKey, verifyHeaders, \
                                     '/inbox', False, \
                                     json.dumps(queueJson['post'])):
                if debug:
                    print('DEBUG: Header signature check failed')
                os.remove(queueFilename)
                queue.pop(0)
                continue

            if debug:
                print('DEBUG: Signature check success')

            if receiveFollowRequest(baseDir, \
                                    queueJson['post'], \
                                    federationList):
            
                if debug:
                    print('DEBUG: Follow accepted from '+keyId)
                    os.remove(queueFilename)
                    queue.pop(0)
                    continue
                    
            if debug:
                print('DEBUG: Queue post accepted')

            if queueJson['sharedInbox']:
                if '/users/' in keyId:
                    # Who is this from? Use the actor from the keyId where we obtained the public key
                    fromList=keyId.replace('https://','').replace('http://','').replace('dat://','').replace('#main-key','').split('/users/')
                    fromNickname=fromList[1]
                    fromDomain=fromList[0]
                    # get the followers of the sender
                    followList=getFollowersOfPerson(baseDir,fromNickname,fromDomain)
                    for followerHandle in followList:
                        followerDir=baseDir+'/accounts/'+followerHandle
                        if os.path.isdir(followerDir):                        
                            if not os.path.isdir(followerDir+'/inbox'):
                                os.mkdir(followerDir+'/inbox')
                                postId=queueJson['post']['id'].replace('/activity','')
                                destination=followerDir+'/inbox/'+postId.replace('/','#')+'.json'
                                if os.path.isfile(destination):
                                    # post already exists in this person's inbox
                                    continue
                                # We could do this in a more storage space efficient way
                                # by linking to the inbox of sharedinbox@domain
                                # However, this allows for easy deletion by individuals
                                # without affecting any other people
                                copyfile(queueFilename, destination)
                # copy to followers
                # remove item from shared inbox
                os.remove(queueFilename)
            else:
                # move to the destination inbox
                os.rename(queueFilename,queueJson['destination'])
            queue.pop(0)
        time.sleep(2)
