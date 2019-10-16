__filename__ = "threads.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import threading
import sys
import trace
import time
import datetime

class threadWithTrace(threading.Thread):
    def __init__(self, *args, **keywords):
        self.startTime=datetime.datetime.utcnow()
        tries=0
        while tries<3:
            try:
                self._args, self._keywords = args, keywords
                threading.Thread.__init__(self, *self._args, **self._keywords) 
                self.killed = False
                break
            except Exception as e:
                print('ERROR: threads.py/__init__ failed - '+str(e))
                time.sleep(1)
                tries+=1
  
    def start(self): 
        tries=0
        while tries<3:
            try:
                self.__run_backup = self.run 
                self.run = self.__run       
                threading.Thread.start(self)
                break
            except Exception as e:
                print('ERROR: threads.py/start failed - '+str(e))
                time.sleep(1)
                tries+=1
  
    def __run(self):
        tries=0
        while tries<3:
            try:
                sys.settrace(self.globaltrace) 
                self.__run_backup() 
                self.run = self.__run_backup
                break
            except Exception as e:
                print('ERROR: threads.py/__run failed - '+str(e))
                time.sleep(1)
                tries+=1

    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line': 
                raise SystemExit() 
        return self.localtrace 
  
    def kill(self): 
        self.killed = True

    def clone(self,fn):
        return threadWithTrace(target=fn, \
                               args=self._args, \
                               daemon=True)        

def removeDormantThreads(threadsList: [],debug: bool) -> None:
    """Removes threads whose execution has completed
    """
    if len(threadsList)==0:
        return

    dormantThreads=[]
    currTime=datetime.datetime.utcnow()

    # which threads are dormant?
    noOfActiveThreads=0
    for th in threadsList:
        removeThread=False        

        if not th.is_alive():
            if debug:
                print('DEBUG: thread is not alive')
            removeThread=True
        elif not th.startTime:
            if debug:
                print('DEBUG: thread has no start time')
            removeThread=True
        elif (currTime-th.startTime).total_seconds()>200:
            if debug:
                print('DEBUG: thread is too old')
            removeThread=True

        if removeThread:
            dormantThreads.append(th)
        else:
            noOfActiveThreads+=1
    if debug:
        print('DEBUG: '+str(noOfActiveThreads) + ' active threads out of '+str(len(threadsList)))

    # remove the dormant threads
    dormantCtr=0
    for th in dormantThreads:
        if debug:
            print('DEBUG: Removing dormant thread '+str(dormantCtr))
            dormantCtr+=1        
        threadsList.remove(th)
        th.kill()
