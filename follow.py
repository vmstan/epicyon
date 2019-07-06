__filename__ = "follow.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
from pprint import pprint
import os
import sys
from person import validNickname
from utils import domainPermitted
from posts import sendSignedJson
from capabilities import isCapable
from acceptreject import createAccept

def getFollowersOfPerson(baseDir: str,nickname: str,domain: str,followFile='following.txt') -> []:
    """Returns a list containing the followers of the given person
    Used by the shared inbox to know who to send incoming mail to
    """
    followers=[]
    handle=nickname.lower()+'@'+domain.lower()
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        return followers
    for subdir, dirs, files in os.walk(baseDir+'/accounts'):
        for account in dirs:
            filename = os.path.join(subdir, account)+'/'+followFile
            if account == handle or account.startswith('sharedinbox@'):
                continue
            if not os.path.isfile(filename):
                continue
            with open(filename, 'r') as followingfile:
                for followingHandle in followingfile:
                    if followingHandle.replace('\n','')==handle:
                        if account not in followers:
                            followers.append(account)
                        break
    return followers

def followPerson(baseDir: str,nickname: str, domain: str, \
                 followNickname: str, followDomain: str, \
                 federationList: [], followFile='following.txt') -> bool:
    """Adds a person to the follow list
    """
    if not domainPermitted(followDomain.lower().replace('\n',''), federationList):
        return False
    handle=nickname.lower()+'@'+domain.lower()
    handleToFollow=followNickname.lower()+'@'+followDomain.lower()
    if not os.path.isdir(baseDir+'/accounts'):
        os.mkdir(baseDir+'/accounts')
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        os.mkdir(baseDir+'/accounts/'+handle)
    filename=baseDir+'/accounts/'+handle+'/'+followFile
    if os.path.isfile(filename):
        if handleToFollow in open(filename).read():
            return True
        with open(filename, "a") as followfile:
            followfile.write(handleToFollow+'\n')
            return True
    with open(filename, "w") as followfile:
        followfile.write(handleToFollow+'\n')
    return True

def followerOfPerson(baseDir: str,nickname: str, domain: str, \
                     followerNickname: str, followerDomain: str, \
                     federationList: []) -> bool:
    """Adds a follower of the given person
    """
    return followPerson(baseDir,nickname, domain, \
                        followerNickname, followerDomain, \
                        federationList, 'followers.txt')

def unfollowPerson(baseDir: str,nickname: str, domain: str, \
                   followNickname: str, followDomain: str, \
                   followFile='following.txt') -> None:
    """Removes a person to the follow list
    """
    handle=nickname.lower()+'@'+domain.lower()
    handleToUnfollow=followNickname.lower()+'@'+followDomain.lower()
    if not os.path.isdir(baseDir+'/accounts'):
        os.mkdir(baseDir+'/accounts')
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        os.mkdir(baseDir+'/accounts/'+handle)
    filename=baseDir+'/accounts/'+handle+'/'+followFile
    if os.path.isfile(filename):
        if handleToUnfollow not in open(filename).read():
            return
        with open(filename, "r") as f:
            lines = f.readlines()
        with open(filename, "w") as f:
            for line in lines:
                if line.strip("\n") != handleToUnfollow:
                    f.write(line)

def unfollowerOfPerson(baseDir: str,nickname: str,domain: str, \
                       followerNickname: str,followerDomain: str) -> None:
    """Remove a follower of a person
    """
    unfollowPerson(baseDir,nickname,domain,followerNickname,followerDomain,'followers.txt')

def clearFollows(baseDir: str,nickname: str,domain: str,followFile='following.txt') -> None:
    """Removes all follows
    """
    handle=nickname.lower()+'@'+domain.lower()
    if not os.path.isdir(baseDir+'/accounts'):
        os.mkdir(baseDir+'/accounts')
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        os.mkdir(baseDir+'/accounts/'+handle)
    filename=baseDir+'/accounts/'+handle+'/'+followFile
    if os.path.isfile(filename):
        os.remove(filename)

def clearFollowers(baseDir: str,nickname: str,domain: str) -> None:
    """Removes all followers
    """
    clearFollows(baseDir,nickname, domain,'followers.txt')

def getNoOfFollows(baseDir: str,nickname: str,domain: str,followFile='following.txt') -> int:
    """Returns the number of follows or followers
    """
    handle=nickname.lower()+'@'+domain.lower()
    filename=baseDir+'/accounts/'+handle+'/'+followFile
    if not os.path.isfile(filename):
        return 0
    ctr = 0
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            if '#' not in line:
                if '@' in line and '.' in line and not line.startswith('http'):
                    ctr += 1
                elif line.startswith('http') and '/users/' in line:
                    ctr += 1
    return ctr

def getNoOfFollowers(baseDir: str,nickname: str,domain: str) -> int:
    """Returns the number of followers of the given person
    """
    return getNoOfFollows(baseDir,nickname,domain,'followers.txt')

def getFollowingFeed(baseDir: str,domain: str,port: int,path: str,httpPrefix: str, \
                     followsPerPage=12,followFile='following') -> {}:
    """Returns the following and followers feeds from GET requests
    """
    if '/'+followFile not in path:
        return None
    # handle page numbers
    headerOnly=True
    pageNumber=None    
    if '?page=' in path:
        pageNumber=path.split('?page=')[1]
        if pageNumber=='true':
            pageNumber=1
        else:
            try:
                pageNumber=int(pageNumber)
            except:
                pass
        path=path.split('?page=')[0]
        headerOnly=False
    
    if not path.endswith('/'+followFile):
        return None
    nickname=None
    if path.startswith('/users/'):
        nickname=path.replace('/users/','',1).replace('/'+followFile,'')
    if path.startswith('/@'):
        nickname=path.replace('/@','',1).replace('/'+followFile,'')
    if not nickname:
        return None
    if not validNickname(nickname):
        return None
            
    if port!=80 and port!=443:
        domain=domain+':'+str(port)

    if headerOnly:
        following = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'first': httpPrefix+'://'+domain+'/users/'+nickname+'/'+followFile+'?page=1',
            'id': httpPrefix+'://'+domain+'/users/'+nickname+'/'+followFile,
            'totalItems': getNoOfFollows(nickname,domain),
            'type': 'OrderedCollection'}
        return following

    if not pageNumber:
        pageNumber=1

    nextPageNumber=int(pageNumber+1)
    following = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': httpPrefix+'://'+domain+'/users/'+nickname+'/'+followFile+'?page='+str(pageNumber),
        'orderedItems': [],
        'partOf': httpPrefix+'://'+domain+'/users/'+nickname+'/'+followFile,
        'totalItems': 0,
        'type': 'OrderedCollectionPage'}        

    handle=nickname.lower()+'@'+domain.lower()
    filename=baseDir+'/accounts/'+handle+'/'+followFile+'.txt'
    if not os.path.isfile(filename):
        return following
    currPage=1
    pageCtr=0
    totalCtr=0
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            if '#' not in line:
                if '@' in line and '.' in line and not line.startswith('http'):
                    pageCtr += 1
                    totalCtr += 1
                    if currPage==pageNumber:
                        url = httpPrefix + '://' + line.lower().replace('\n','').split('@')[1] + \
                            '/users/' + line.lower().replace('\n','').split('@')[0]
                        following['orderedItems'].append(url)
                elif (line.startswith('http') or line.startswith('dat')) and '/users/' in line:
                    pageCtr += 1
                    totalCtr += 1
                    if currPage==pageNumber:
                        following['orderedItems'].append(line.lower().replace('\n',''))
            if pageCtr>=followsPerPage:
                pageCtr=0
                currPage += 1
    following['totalItems']=totalCtr
    lastPage=int(totalCtr/followsPerPage)
    if lastPage<1:
        lastPage=1
    if nextPageNumber>lastPage:
        following['next']=httpPrefix+'://'+domain+'/users/'+nickname+'/'+followFile+'?page='+str(lastPage)
    return following

def receiveFollowRequest(session,baseDir: str,httpPrefix: str,port: int,sendThreads: [],postLog: [],cachedWebfingers: {},personCache: {},messageJson: {},federationList: [],capsList: [],debug : bool) -> bool:
    """Receives a follow request within the POST section of HTTPServer
    """
    if not messageJson['type'].startswith('Follow'):
        return False
    if not messageJson.get('actor'):
        if debug:
            print('DEBUG: follow request has no actor')
        return False
    if '/users/' not in messageJson['actor']:
        if debug:
            print('DEBUG: "users" missing from actor')            
        return False
    domain=messageJson['actor'].split('/users/')[0].replace('https://','').replace('http://','').replace('dat://','')
    if ':' in domain:
        domain=domain.split(':')[0]
    if not domainPermitted(domain,federationList):
        if debug:
            print('DEBUG: follower from domain not permitted - '+domain)
        return False
    nickname=messageJson['actor'].split('/users/')[1].replace('@','')
    handle=nickname.lower()+'@'+domain.lower()
    if '/users/' not in messageJson['object']:
        if debug:
            print('DEBUG: "users" not found within object')
        return False
    domainToFollow=messageJson['object'].split('/users/')[0].replace('https://','').replace('http://','').replace('dat://','')
    toPort=port
    if ':' in domainToFollow:
        toPort=domainToFollow.split(':')[1]
        domainToFollow=domainToFollow.split(':')[0]
    if not domainPermitted(domainToFollow,federationList):
        if debug:
            print('DEBUG: follow domain not permitted '+domainToFollow)
        return False
    nicknameToFollow=messageJson['object'].split('/users/')[1].replace('@','')
    handleToFollow=nicknameToFollow.lower()+'@'+domainToFollow.lower()
    if domainToFollow==domain:
        if not os.path.isdir(baseDir+'/accounts/'+handleToFollow):
            if debug:
                print('DEBUG: followed account not found - '+baseDir+'/accounts/'+handleToFollow)
            return False
    if not followerOfPerson(baseDir,nickname,domain,nicknameToFollow,domainToFollow,federationList):
        if debug:
            print('DEBUG: '+nickname+'@'+domain+' is already a follower of '+nicknameToFollow+'@'+domainToFollow)
        return False
    # send accept back
    if debug:
        print('DEBUG: sending Accept from '+nickname+'@'+domain+' for follow request')
    personUrl=messageJson['actor']
    acceptJson=createAccept(baseDir,federationList,capsList,nickname,domain,port, \
                            personUrl,'',httpPrefix,messageJson['object'])
    clientToServer=False
    sendSignedJson(acceptJson,session,baseDir,nickname,domain,port, \
                   nicknameToFollow,domainToFollow,toPort, '', \
                   httpPrefix,True,clientToServer, \
                   federationList, capsList, \
                   sendThreads,postLog,cachedWebfingers,personCache,debug)

def sendFollowRequest(session,baseDir: str,nickname: str,domain: str,port: int,httpPrefix: str, \
                      followNickname: str,followDomain: str,followPort: bool,followHttpPrefix: str, \
                      clientToServer: bool,federationList: [],capsList: [], \
                      sendThreads: [],postLog: [],cachedWebfingers: {},personCache: {},
                      debug : bool) -> {}:
    """Gets the json object for sending a follow request
    """    
    if not domainPermitted(followDomain,federationList):
        return None
    
    followActor=httpPrefix+'://'+domain+'/users/'+nickname    
    if port!=80 and port!=443:
        followActor=httpPrefix+'://'+domain+':'+str(port)+'/users/'+nickname

    requestDomain=followDomain
    if followPort!=80 and followPort!=443:
        requestDomain=followDomain+':'+str(followPort)

    # check that we are capable
    if capsList:
        if not isCapable(followActor,capsList,'inbox:write'):
            return None
        
    newFollowJson = {
        'type': 'Follow',
        'actor': followActor,
        'object': followHttpPrefix+'://'+requestDomain+'/users/'+followNickname
    }

    sendSignedJson(newFollowJson,session,baseDir,nickname,domain,port, \
                   followNickname,followDomain,followPort, '', \
                   httpPrefix,True,clientToServer, \
                   federationList, capsList, \
                   sendThreads,postLog,cachedWebfingers,personCache, debug)

    return newFollowJson
