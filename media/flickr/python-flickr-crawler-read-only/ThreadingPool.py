'''
Created on Sep 28, 2010

@author: ziliangdotme
'''
import threading
import thread
import time
import Queue

class ThreadingPool(object):
    '''classdocs'''
    
    

    def __init__(self, cnt):
        self.threads = []
        queuedSize = 1024
        self.pool = Queue.Queue(queuedSize)
        for i in xrange(cnt):
            wT = threading.Thread(target=ThreadingPool.working, args=[self])
            #wT = threading.Thread(target=ThreadingPool.working, kwargs={'host':self})
            wT.start()
            self.threads.append(wT)
            
    def addTask(self, task, args=(), kwargs={}):
        self.pool.put({'task':task, 'args':args, 'kwargs':kwargs})
            
    @staticmethod
    def working(host):
        pool = host.pool
        
        task = None
        args = None
        kwargs = None
        while True:
            print 'size ' + str(pool.qsize())
            workUnit = pool.get()
            task = workUnit['task']
            args = workUnit['args']
            kwargs = workUnit['kwargs']
            task(*args, **kwargs)
            pool.task_done()
        
