__filename__ = "bookmarks.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.1.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import os
from pprint import pprint
from utils import removePostFromCache
from utils import urlPermitted
from utils import getNicknameFromActor
from utils import getDomainFromActor
from utils import locatePost
from utils import getCachedPostFilename
from utils import loadJson
from utils import saveJson
from posts import sendSignedJson
from session import postJson
from webfinger import webfingerHandle
from auth import createBasicAuthHeader
from posts import getPersonBox


def undoBookmarksCollectionEntry(recentPostsCache: {},
                                 baseDir: str, postFilename: str,
                                 objectUrl: str,
                                 actor: str, domain: str, debug: bool) -> None:
    """Undoes a bookmark for a particular actor
    """
    postJsonObject = loadJson(postFilename)
    if not postJsonObject:
        return

    # remove any cached version of this post so that the
    # bookmark icon is changed
    nickname = getNicknameFromActor(actor)
    cachedPostFilename = getCachedPostFilename(baseDir, nickname,
                                               domain, postJsonObject)
    if cachedPostFilename:
        if os.path.isfile(cachedPostFilename):
            os.remove(cachedPostFilename)
    removePostFromCache(postJsonObject, recentPostsCache)

    if not postJsonObject.get('type'):
        return
    if postJsonObject['type'] != 'Create':
        return
    if not postJsonObject.get('object'):
        if debug:
            pprint(postJsonObject)
            print('DEBUG: post ' + objectUrl + ' has no object')
        return
    if not isinstance(postJsonObject['object'], dict):
        return
    if not postJsonObject['object'].get('bookmarks'):
        return
    if not isinstance(postJsonObject['object']['bookmarks'], dict):
        return
    if not postJsonObject['object']['bookmarks'].get('items'):
        return
    totalItems = 0
    if postJsonObject['object']['bookmarks'].get('totalItems'):
        totalItems = postJsonObject['object']['bookmarks']['totalItems']
        itemFound = False
    for bookmarkItem in postJsonObject['object']['bookmarks']['items']:
        if bookmarkItem.get('actor'):
            if bookmarkItem['actor'] == actor:
                if debug:
                    print('DEBUG: bookmark was removed for ' + actor)
                bmIt = bookmarkItem
                postJsonObject['object']['bookmarks']['items'].remove(bmIt)
                itemFound = True
                break

    if not itemFound:
        return

    if totalItems == 1:
        if debug:
            print('DEBUG: bookmarks was removed from post')
        del postJsonObject['object']['bookmarks']
    else:
        bmItLen = len(postJsonObject['object']['bookmarks']['items'])
        postJsonObject['object']['bookmarks']['totalItems'] = bmItLen
    saveJson(postJsonObject, postFilename)

    # remove from the index
    bookmarksIndexFilename = baseDir + '/accounts/' + \
        nickname + '@' + domain + '/bookmarks.index'
    if not os.path.isfile(bookmarksIndexFilename):
        return
    if '/' in postFilename:
        bookmarkIndex = postFilename.split('/')[-1].strip()
    else:
        bookmarkIndex = postFilename.strip()
    if bookmarkIndex not in open(bookmarksIndexFilename).read():
        return
    indexStr = ''
    indexStrChanged = False
    with open(bookmarksIndexFilename, 'r') as indexFile:
        indexStr = indexFile.read().replace(bookmarkIndex + '\n', '')
        indexStrChanged = True
    if indexStrChanged:
        bookmarksIndexFile = open(bookmarksIndexFilename, 'w')
        if bookmarksIndexFile:
            bookmarksIndexFile.write(indexStr)
            bookmarksIndexFile.close()


def bookmarkedByPerson(postJsonObject: {}, nickname: str, domain: str) -> bool:
    """Returns True if the given post is bookmarked by the given person
    """
    if noOfBookmarks(postJsonObject) == 0:
        return False
    actorMatch = domain + '/users/' + nickname
    for item in postJsonObject['object']['bookmarks']['items']:
        if item['actor'].endswith(actorMatch):
            return True
    return False


def noOfBookmarks(postJsonObject: {}) -> int:
    """Returns the number of bookmarks ona  given post
    """
    if not postJsonObject.get('object'):
        return 0
    if not isinstance(postJsonObject['object'], dict):
        return 0
    if not postJsonObject['object'].get('bookmarks'):
        return 0
    if not isinstance(postJsonObject['object']['bookmarks'], dict):
        return 0
    if not postJsonObject['object']['bookmarks'].get('items'):
        postJsonObject['object']['bookmarks']['items'] = []
        postJsonObject['object']['bookmarks']['totalItems'] = 0
    return len(postJsonObject['object']['bookmarks']['items'])


def updateBookmarksCollection(recentPostsCache: {},
                              baseDir: str, postFilename: str,
                              objectUrl: str,
                              actor: str, domain: str, debug: bool) -> None:
    """Updates the bookmarks collection within a post
    """
    postJsonObject = loadJson(postFilename)
    if postJsonObject:
        # remove any cached version of this post so that the
        # bookmark icon is changed
        nickname = getNicknameFromActor(actor)
        cachedPostFilename = getCachedPostFilename(baseDir, nickname,
                                                   domain, postJsonObject)
        if cachedPostFilename:
            if os.path.isfile(cachedPostFilename):
                os.remove(cachedPostFilename)
        removePostFromCache(postJsonObject, recentPostsCache)

        if not postJsonObject.get('object'):
            if debug:
                pprint(postJsonObject)
                print('DEBUG: post ' + objectUrl + ' has no object')
            return
        if not objectUrl.endswith('/bookmarks'):
            objectUrl = objectUrl + '/bookmarks'
        if not postJsonObject['object'].get('bookmarks'):
            if debug:
                print('DEBUG: Adding initial bookmarks to ' + objectUrl)
            bookmarksJson = {
                "@context": "https://www.w3.org/ns/activitystreams",
                'id': objectUrl,
                'type': 'Collection',
                "totalItems": 1,
                'items': [{
                    'type': 'Bookmark',
                    'actor': actor
                }]
            }
            postJsonObject['object']['bookmarks'] = bookmarksJson
        else:
            if not postJsonObject['object']['bookmarks'].get('items'):
                postJsonObject['object']['bookmarks']['items'] = []
            for bookmarkItem in postJsonObject['object']['bookmarks']['items']:
                if bookmarkItem.get('actor'):
                    if bookmarkItem['actor'] == actor:
                        return
                    newBookmark = {
                        'type': 'Bookmark',
                        'actor': actor
                    }
                    nb = newBookmark
                    bmIt = len(postJsonObject['object']['bookmarks']['items'])
                    postJsonObject['object']['bookmarks']['items'].append(nb)
                    postJsonObject['object']['bookmarks']['totalItems'] = bmIt

        if debug:
            print('DEBUG: saving post with bookmarks added')
            pprint(postJsonObject)

        saveJson(postJsonObject, postFilename)

        # prepend to the index
        bookmarksIndexFilename = baseDir + '/accounts/' + \
            nickname + '@' + domain + '/bookmarks.index'
        bookmarkIndex = postFilename.split('/')[-1]
        if os.path.isfile(bookmarksIndexFilename):
            if bookmarkIndex not in open(bookmarksIndexFilename).read():
                try:
                    with open(bookmarksIndexFilename, 'r+') as bmIndexFile:
                        content = bmIndexFile.read()
                        bmIndexFile.seek(0, 0)
                        bmIndexFile.write(bookmarkIndex + '\n' + content)
                        if debug:
                            print('DEBUG: bookmark added to index')
                except Exception as e:
                    print('WARN: Failed to write entry to bookmarks index ' +
                          bookmarksIndexFilename + ' ' + str(e))
        else:
            bookmarksIndexFile = open(bookmarksIndexFilename, 'w')
            if bookmarksIndexFile:
                bookmarksIndexFile.write(bookmarkIndex + '\n')
                bookmarksIndexFile.close()


def bookmark(recentPostsCache: {},
             session, baseDir: str, federationList: [],
             nickname: str, domain: str, port: int,
             ccList: [], httpPrefix: str,
             objectUrl: str, actorBookmarked: str,
             clientToServer: bool,
             sendThreads: [], postLog: [],
             personCache: {}, cachedWebfingers: {},
             debug: bool, projectVersion: str) -> {}:
    """Creates a bookmark
    actor is the person doing the bookmarking
    'to' might be a specific person (actor) whose post was bookmarked
    object is typically the url of the message which was bookmarked
    """
    if not urlPermitted(objectUrl, federationList, "inbox:write"):
        return None

    fullDomain = domain
    if port:
        if port != 80 and port != 443:
            if ':' not in domain:
                fullDomain = domain + ':' + str(port)

    newBookmarkJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Bookmark',
        'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
        'object': objectUrl
    }
    if ccList:
        if len(ccList) > 0:
            newBookmarkJson['cc'] = ccList

    # Extract the domain and nickname from a statuses link
    bookmarkedPostNickname = None
    bookmarkedPostDomain = None
    bookmarkedPostPort = None
    if actorBookmarked:
        acBm = actorBookmarked
        bookmarkedPostNickname = getNicknameFromActor(acBm)
        bookmarkedPostDomain, bookmarkedPostPort = getDomainFromActor(acBm)
    else:
        if '/users/' in objectUrl or \
           '/channel/' in objectUrl or \
           '/profile/' in objectUrl:
            ou = objectUrl
            bookmarkedPostNickname = getNicknameFromActor(ou)
            bookmarkedPostDomain, bookmarkedPostPort = getDomainFromActor(ou)

    if bookmarkedPostNickname:
        postFilename = locatePost(baseDir, nickname, domain, objectUrl)
        if not postFilename:
            print('DEBUG: bookmark baseDir: ' + baseDir)
            print('DEBUG: bookmark nickname: ' + nickname)
            print('DEBUG: bookmark domain: ' + domain)
            print('DEBUG: bookmark objectUrl: ' + objectUrl)
            return None

        updateBookmarksCollection(recentPostsCache,
                                  baseDir, postFilename, objectUrl,
                                  newBookmarkJson['actor'], domain, debug)
        
        #sendSignedJson(newBookmarkJson, session, baseDir,
        #               nickname, domain, port,
        #               bookmarkedPostNickname,
        #               bookmarkedPostDomain, bookmarkedPostPort,
        #               'https://www.w3.org/ns/activitystreams#Public',
        #               httpPrefix, True, clientToServer, federationList,
        #               sendThreads, postLog, cachedWebfingers, personCache,
        #               debug, projectVersion)

    return newBookmarkJson


def bookmarkPost(recentPostsCache: {},
                 session, baseDir: str, federationList: [],
                 nickname: str, domain: str, port: int, httpPrefix: str,
                 bookmarkNickname: str, bookmarkedomain: str,
                 bookmarkPort: int,
                 ccList: [],
                 bookmarkStatusNumber: int, clientToServer: bool,
                 sendThreads: [], postLog: [],
                 personCache: {}, cachedWebfingers: {},
                 debug: bool, projectVersion: str) -> {}:
    """Bookmarks a given status post. This is only used by unit tests
    """
    bookmarkedomain = bookmarkedomain
    if bookmarkPort:
        if bookmarkPort != 80 and bookmarkPort != 443:
            if ':' not in bookmarkedomain:
                bookmarkedomain = bookmarkedomain + ':' + str(bookmarkPort)

    actorBookmarked = httpPrefix + '://' + bookmarkedomain + \
        '/users/' + bookmarkNickname
    objectUrl = actorBookmarked + '/statuses/' + str(bookmarkStatusNumber)

    return bookmark(recentPostsCache,
                    session, baseDir, federationList, nickname, domain, port,
                    ccList, httpPrefix, objectUrl, actorBookmarked,
                    clientToServer,
                    sendThreads, postLog, personCache, cachedWebfingers,
                    debug, projectVersion)


def undoBookmark(recentPostsCache: {},
                 session, baseDir: str, federationList: [],
                 nickname: str, domain: str, port: int,
                 ccList: [], httpPrefix: str,
                 objectUrl: str, actorBookmarked: str,
                 clientToServer: bool,
                 sendThreads: [], postLog: [],
                 personCache: {}, cachedWebfingers: {},
                 debug: bool, projectVersion: str) -> {}:
    """Removes a bookmark
    actor is the person doing the bookmarking
    'to' might be a specific person (actor) whose post was bookmarked
    object is typically the url of the message which was bookmarked
    """
    if not urlPermitted(objectUrl, federationList, "inbox:write"):
        return None

    fullDomain = domain
    if port:
        if port != 80 and port != 443:
            if ':' not in domain:
                fullDomain = domain + ':' + str(port)

    newUndoBookmarkJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Undo',
        'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
        'object': {
            'type': 'Bookmark',
            'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
            'object': objectUrl
        }
    }
    if ccList:
        if len(ccList) > 0:
            newUndoBookmarkJson['cc'] = ccList
            newUndoBookmarkJson['object']['cc'] = ccList

    # Extract the domain and nickname from a statuses link
    bookmarkedPostNickname = None
    bookmarkedPostDomain = None
    bookmarkedPostPort = None
    if actorBookmarked:
        acBm = actorBookmarked
        bookmarkedPostNickname = getNicknameFromActor(acBm)
        bookmarkedPostDomain, bookmarkedPostPort = getDomainFromActor(acBm)
    else:
        if '/users/' in objectUrl or \
           '/channel/' in objectUrl or \
           '/profile/' in objectUrl:
            ou = objectUrl
            bookmarkedPostNickname = getNicknameFromActor(ou)
            bookmarkedPostDomain, bookmarkedPostPort = getDomainFromActor(ou)

    if bookmarkedPostNickname:
        postFilename = locatePost(baseDir, nickname, domain, objectUrl)
        if not postFilename:
            return None

        undoBookmarksCollectionEntry(recentPostsCache,
                                     baseDir, postFilename, objectUrl,
                                     newUndoBookmarkJson['actor'],
                                     domain, debug)

        #sendSignedJson(newUndoBookmarkJson, session, baseDir,
        #               nickname, domain, port,
        #               bookmarkedPostNickname, bookmarkedPostDomain,
        #               bookmarkedPostPort,
        #               'https://www.w3.org/ns/activitystreams#Public',
        #               httpPrefix, True, clientToServer, federationList,
        #               sendThreads, postLog, cachedWebfingers, personCache,
        #               debug, projectVersion)
    else:
        return None

    return newUndoBookmarkJson


def undoBookmarkPost(session, baseDir: str, federationList: [],
                     nickname: str, domain: str, port: int, httpPrefix: str,
                     bookmarkNickname: str, bookmarkedomain: str,
                     bookmarkPort: int, ccList: [],
                     bookmarkStatusNumber: int, clientToServer: bool,
                     sendThreads: [], postLog: [],
                     personCache: {}, cachedWebfingers: {},
                     debug: bool) -> {}:
    """Removes a bookmarked post
    """
    bookmarkedomain = bookmarkedomain
    if bookmarkPort:
        if bookmarkPort != 80 and bookmarkPort != 443:
            if ':' not in bookmarkedomain:
                bookmarkedomain = bookmarkedomain + ':' + str(bookmarkPort)

    objectUrl = httpPrefix + '://' + bookmarkedomain + \
        '/users/' + bookmarkNickname + \
        '/statuses/' + str(bookmarkStatusNumber)

    return undoBookmark(session, baseDir, federationList,
                        nickname, domain, port,
                        ccList, httpPrefix, objectUrl, clientToServer,
                        sendThreads, postLog, personCache,
                        cachedWebfingers, debug)


def sendBookmarkViaServer(baseDir: str, session,
                          fromNickname: str, password: str,
                          fromDomain: str, fromPort: int,
                          httpPrefix: str, bookmarkUrl: str,
                          cachedWebfingers: {}, personCache: {},
                          debug: bool, projectVersion: str) -> {}:
    """Creates a bookmark via c2s
    """
    if not session:
        print('WARN: No session for sendBookmarkViaServer')
        return 6

    fromDomainFull = fromDomain
    if fromPort:
        if fromPort != 80 and fromPort != 443:
            if ':' not in fromDomain:
                fromDomainFull = fromDomain + ':' + str(fromPort)

    newBookmarkJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Bookmark',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'object': bookmarkUrl
    }

    handle = httpPrefix + '://' + fromDomainFull + '/@' + fromNickname

    # lookup the inbox for the To handle
    wfRequest = webfingerHandle(session, handle, httpPrefix,
                                cachedWebfingers,
                                fromDomain, projectVersion)
    if not wfRequest:
        if debug:
            print('DEBUG: announce webfinger failed for ' + handle)
        return 1

    postToBox = 'outbox'

    # get the actor inbox for the To handle
    (inboxUrl, pubKeyId, pubKey,
     fromPersonId, sharedInbox,
     capabilityAcquisition, avatarUrl,
     displayName) = getPersonBox(baseDir, session, wfRequest, personCache,
                                 projectVersion, httpPrefix, fromNickname,
                                 fromDomain, postToBox)

    if not inboxUrl:
        if debug:
            print('DEBUG: No ' + postToBox + ' was found for ' + handle)
        return 3
    if not fromPersonId:
        if debug:
            print('DEBUG: No actor was found for ' + handle)
        return 4

    authHeader = createBasicAuthHeader(fromNickname, password)

    headers = {
        'host': fromDomain,
        'Content-type': 'application/json',
        'Authorization': authHeader
    }
    postResult = postJson(session, newBookmarkJson, [],
                          inboxUrl, headers, "inbox:write")
    if not postResult:
        if debug:
            print('DEBUG: POST announce failed for c2s to ' + inboxUrl)
        return 5

    if debug:
        print('DEBUG: c2s POST bookmark success')

    return newBookmarkJson


def sendUndoBookmarkViaServer(baseDir: str, session,
                              fromNickname: str, password: str,
                              fromDomain: str, fromPort: int,
                              httpPrefix: str, bookmarkUrl: str,
                              cachedWebfingers: {}, personCache: {},
                              debug: bool, projectVersion: str) -> {}:
    """Undo a bookmark via c2s
    """
    if not session:
        print('WARN: No session for sendUndoBookmarkViaServer')
        return 6

    fromDomainFull = fromDomain
    if fromPort:
        if fromPort != 80 and fromPort != 443:
            if ':' not in fromDomain:
                fromDomainFull = fromDomain + ':' + str(fromPort)

    newUndoBookmarkJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Undo',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'object': {
            'type': 'Bookmark',
            'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
            'object': bookmarkUrl
        }
    }

    handle = httpPrefix + '://' + fromDomainFull + '/@' + fromNickname

    # lookup the inbox for the To handle
    wfRequest = webfingerHandle(session, handle, httpPrefix, cachedWebfingers,
                                fromDomain, projectVersion)
    if not wfRequest:
        if debug:
            print('DEBUG: announce webfinger failed for ' + handle)
        return 1

    postToBox = 'outbox'

    # get the actor inbox for the To handle
    (inboxUrl, pubKeyId, pubKey,
     fromPersonId, sharedInbox,
     capabilityAcquisition, avatarUrl,
     displayName) = getPersonBox(baseDir, session, wfRequest, personCache,
                                 projectVersion, httpPrefix, fromNickname,
                                 fromDomain, postToBox)

    if not inboxUrl:
        if debug:
            print('DEBUG: No ' + postToBox + ' was found for ' + handle)
        return 3
    if not fromPersonId:
        if debug:
            print('DEBUG: No actor was found for ' + handle)
        return 4

    authHeader = createBasicAuthHeader(fromNickname, password)

    headers = {
        'host': fromDomain,
        'Content-type': 'application/json',
        'Authorization': authHeader
    }
    postResult = postJson(session, newUndoBookmarkJson, [],
                          inboxUrl, headers, "inbox:write")
    if not postResult:
        if debug:
            print('DEBUG: POST announce failed for c2s to ' + inboxUrl)
        return 5

    if debug:
        print('DEBUG: c2s POST undo bookmark success')

    return newUndoBookmarkJson


def outboxBookmark(recentPostsCache: {},
                   baseDir: str, httpPrefix: str,
                   nickname: str, domain: str, port: int,
                   messageJson: {}, debug: bool) -> None:
    """ When a bookmark request is received by the outbox from c2s
    """
    if not messageJson.get('type'):
        if debug:
            print('DEBUG: bookmark - no type')
        return
    if not messageJson['type'] == 'Bookmark':
        if debug:
            print('DEBUG: not a bookmark')
        return
    if not messageJson.get('object'):
        if debug:
            print('DEBUG: no object in bookmark')
        return
    if not isinstance(messageJson['object'], str):
        if debug:
            print('DEBUG: bookmark object is not string')
        return
    if messageJson.get('to'):
        if not isinstance(messageJson['to'], list):
            return
        if len(messageJson['to']) != 1:
            print('WARN: Bookmark should only be sent to one recipient')
            return
        if messageJson['to'][0] != messageJson['actor']:
            print('WARN: Bookmark should be addressed to the same actor')
            return
    if debug:
        print('DEBUG: c2s bookmark request arrived in outbox')

    messageId = messageJson['object'].replace('/activity', '')
    if ':' in domain:
        domain = domain.split(':')[0]
    postFilename = locatePost(baseDir, nickname, domain, messageId)
    if not postFilename:
        if debug:
            print('DEBUG: c2s bookmark post not found in inbox or outbox')
            print(messageId)
        return True
    updateBookmarksCollection(recentPostsCache,
                              baseDir, postFilename, messageId,
                              messageJson['actor'], domain, debug)
    if debug:
        print('DEBUG: post bookmarked via c2s - ' + postFilename)


def outboxUndoBookmark(recentPostsCache: {},
                       baseDir: str, httpPrefix: str,
                       nickname: str, domain: str, port: int,
                       messageJson: {}, debug: bool) -> None:
    """ When an undo bookmark request is received by the outbox from c2s
    """
    if not messageJson.get('type'):
        return
    if not messageJson['type'] == 'Undo':
        return
    if not messageJson.get('object'):
        return
    if not isinstance(messageJson['object'], dict):
        if debug:
            print('DEBUG: undo bookmark object is not dict')
        return
    if not messageJson['object'].get('type'):
        if debug:
            print('DEBUG: undo bookmark - no type')
        return
    if not messageJson['object']['type'] == 'Bookmark':
        if debug:
            print('DEBUG: not a undo bookmark')
        return
    if not messageJson['object'].get('object'):
        if debug:
            print('DEBUG: no object in undo bookmark')
        return
    if not isinstance(messageJson['object']['object'], str):
        if debug:
            print('DEBUG: undo bookmark object is not string')
        return
    if messageJson.get('to'):
        if not isinstance(messageJson['to'], list):
            return
        if len(messageJson['to']) != 1:
            print('WARN: Bookmark should only be sent to one recipient')
            return
        if messageJson['to'][0] != messageJson['actor']:
            print('WARN: Bookmark should be addressed to the same actor')
            return
    if debug:
        print('DEBUG: c2s undo bookmark request arrived in outbox')

    messageId = messageJson['object']['object'].replace('/activity', '')
    if ':' in domain:
        domain = domain.split(':')[0]
    postFilename = locatePost(baseDir, nickname, domain, messageId)
    if not postFilename:
        if debug:
            print('DEBUG: c2s undo bookmark post not found in inbox or outbox')
            print(messageId)
        return True
    undoBookmarksCollectionEntry(recentPostsCache,
                                 baseDir, postFilename, messageId,
                                 messageJson['actor'], domain, debug)
    if debug:
        print('DEBUG: post undo bookmarked via c2s - ' + postFilename)
