__filename__ = "daemon.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

from http.server import BaseHTTPRequestHandler, HTTPServer
#import socketserver
import json
import cgi
from pprint import pprint
from session import createSession
from webfinger import webfingerMeta
from webfinger import webfingerLookup
from person import personLookup
from person import personKeyLookup
from person import personOutboxJson
from inbox import inboxPermittedMessage
from follow import getFollowingFeed
import os
import sys

# Avoid giant messages
maxMessageLength=5000

# maximum number of posts to list in outbox feed
maxPostsInFeed=20

# number of follows/followers per page
followsPerPage=12

def readFollowList(filename: str):
    """Returns a list of ActivityPub addresses to follow
    """
    followlist=[]
    if not os.path.isfile(filename):
        return followlist
    followUsers = open(filename, "r")    
    for u in followUsers:
        if u not in followlist:
            username,domain = parseHandle(u)
            if username:
                followlist.append(username+'@'+domain)
    followUsers.close()
    return followlist

class PubServer(BaseHTTPRequestHandler):
    def _set_headers(self,fileFormat):
        self.send_response(200)
        self.send_header('Content-type', fileFormat)
        self.end_headers()

    def _404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<html><head></head><body><h1>404 Not Found</h1></body></html>".encode('utf-8'))

    def _webfinger(self) -> bool:
        if not self.path.startswith('/.well-known'):
            return False

        if self.path.startswith('/.well-known/host-meta'):
            wfResult=webfingerMeta()
            if wfResult:
                self._set_headers('application/xrd+xml')
                self.wfile.write(wfResult.encode('utf-8'))
            return

        wfResult=webfingerLookup(self.path,self.server.baseDir)
        if wfResult:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(wfResult).encode('utf-8'))
        else:
            self._404()
        return True

    def _permittedDir(self,path):
        if path.startswith('/wfendpoints') or \
           path.startswith('/keys') or \
           path.startswith('/accounts'):
            return False
        return True

    def do_GET(self):        
        try:
            if self.GETbusy:
                self.send_response(429)
                self.end_headers()
                return                
        except:
            pass
        self.GETbusy=True

        if not self._permittedDir(self.path):
            self._404()
            self.GETbusy=False
            return
        # get webfinger endpoint for a person
        if self._webfinger():
            self.GETbusy=False
            return
        # get outbox feed for a person
        outboxFeed=personOutboxJson(self.server.baseDir,self.server.domain,self.server.port,self.path,self.server.https,maxPostsInFeed)
        if outboxFeed:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(outboxFeed).encode('utf-8'))
            self.GETbusy=False
            return
        following=getFollowingFeed(self.server.baseDir,self.server.domain,self.server.port,self.path,self.server.https,followsPerPage)
        if following:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(following).encode('utf-8'))
            self.GETbusy=False
            return            
        followers=getFollowingFeed(self.server.baseDir,self.server.domain,self.server.port,self.path,self.server.https,followsPerPage,'followers')
        if followers:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(followers).encode('utf-8'))
            self.GETbusy=False
            return            
        # look up a person
        getPerson = personLookup(self.server.domain,self.path,self.server.baseDir)
        if getPerson:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(getPerson).encode('utf-8'))
            self.GETbusy=False
            return
        personKey = personKeyLookup(self.server.domain,self.path,self.server.baseDir)
        if personKey:
            self._set_headers('text/html; charset=utf-8')
            self.wfile.write(personKey.encode('utf-8'))
            self.GETbusy=False
            return
        # check that a json file was requested
        if not self.path.endswith('.json'):
            self._404()
            self.GETbusy=False
            return
        # check that the file exists
        filename=self.server.baseDir+self.path
        if os.path.isfile(filename):
            self._set_headers('application/json')
            with open(filename, 'r', encoding='utf8') as File:
                content = File.read()
                contentJson=json.loads(content)
                self.wfile.write(json.dumps(contentJson).encode('utf8'))
        else:
            self._404()
        self.GETbusy=False

    def do_HEAD(self):
        self._set_headers('application/json')
        
    def do_POST(self):
        print('**************** POST recieved!')
        try:
            if self.POSTbusy:
                self.send_response(429)
                self.end_headers()
                return                
        except:
            pass
        print('**************** POST ready to receive')
        self.POSTbusy=True
        if not self.headers.get('Content-type'):
            print('**************** No Content-type')
            self.send_response(400)
            self.end_headers()
            self.POSTbusy=False
            return
        print('*****************headers: '+str(self.headers))
        
        # refuse to receive non-json content
        if self.headers['Content-type'] != 'application/json':
            print("**************** That's no Json!")
            self.send_response(400)
            self.end_headers()
            self.POSTbusy=False
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-length'])
        print('**************** content-length: '+str(length))
        if length>maxMessageLength:
            self.send_response(400)
            self.end_headers()
            self.POSTbusy=False
            return
        print('**************** Reading message')
        messageBytes=self.rfile.read(length)
        messageJson = json.loads(messageBytes)

        if not inboxPermittedMessage(self.server.domain,messageJson,self.server.federationList):
            print('**************** Ah Ah Ah')
            self.send_response(403)
            self.end_headers()
            self.POSTbusy=False
            return
        
        print('**************** POST valid')
        pprint(messageJson)
        # add a property to the object, just to mess with data
        #message['received'] = 'ok'
        
        # send the message back
        #self._set_headers('application/json')
        #self.wfile.write(json.dumps(message).encode('utf-8'))
        self.send_response(200)
        self.end_headers()
        self.POSTbusy=False

def runDaemon(domain: str,port=80,https=True,fedList=[],useTor=False) -> None:
    if len(domain)==0:
        domain='127.0.0.1'
    if '.' not in domain:
        print('Invalid domain: ' + domain)
        return
    session = createSession(useTor)

    serverAddress = ('', port)
    httpd = HTTPServer(serverAddress, PubServer)
    httpd.domain=domain
    httpd.port=port
    httpd.https=https
    httpd.federationList=fedList.copy()
    httpd.baseDir=os.getcwd()
    print('Running ActivityPub daemon on ' + domain + ' port ' + str(port))
    httpd.serve_forever()
