# -*- coding: utf-8 -*-
import threading

chunk = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]    

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        self.result = ''
        threading.Thread.__init__(self)
        
    def run(self):
        self.result = self._target(*self._args)
