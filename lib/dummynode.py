# -*- coding: utf-8 -*-
from node import Node
import os

class DummyNode(Node):
    def __init__(self, name):
        Node.__init__(self)
        self._name = name
        self.count = 10
        
    def event_update(self):
        print self.count
        self.count -= 1
        if self.count < 0:
            self._running = False
            
    def event_init(self):
        print "hello, my name is", self._name
        print os.getpid()        
        print "I'm connected with:", self._pipes
        
    def msg_ping(self, name_from):
        print "Hey! He ping'd me:", name_from
        self.send("pong", name_from)

