# -*- coding: utf-8 -*-
from node import Node
import os
import time

class DummyNode(Node):
    def event_update(self):
        print "TICK"
        time.sleep(1)
        self.send("sysexit", self._master)
            
    def event_init(self):
        print "hello, my name is", self._name
        print os.getpid()        
        print "I'm connected with:", self._pipes
        
    def msg_ping(self, name_from):
        print "Hey! He ping'd me:", name_from
        self.send("pong", name_from)

