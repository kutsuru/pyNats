# -*- coding: utf-8 -*-
"""
Node system for multiprocessing using message passing,
in order to understand Python multi-core capabilities.

Heavily inspired by http://code.google.com/p/multiproc-pygame/
"""
import multiprocessing
import time

class Node(object):
    """Parallelized node"""
    def __init__(self, name):
        self._pipes = {}
        self._processes = {}
        self._name = name
        self._master = None
        
    def connect(self, name, pipe):
        """Add a connection to NAME trough PIPE."""
        self._pipes[name] = pipe
        
    def send(self, msg_name, rcv_name, *args):
        """Send a message MSG_NAME to the given RCV_NAME, associate ARGS.
        If RCV_NAME is unknown, send a forward message to MASTER."""
        if rcv_name in self._pipes:            
            self._pipes[rcv_name].send((msg_name, args))
        elif self._master is not None:
            full_mess = (msg_name, rcv_name, args)
            self._pipes[self._master].send(("forward", full_mess))
            
    def attach(self, node):
        """Attach the given node,
        all attached nodes will be run with their master."""
        name = node._name
        p1, p2 = multiprocessing.Pipe()
        node.connect(self._name, p2)
        p = multiprocessing.Process(target=node._loop, args=(self._name,))
        
        self._processes[name] = (p, p1, node)
        self._pipes[name] = p1
        
    def _parse(self, message, name_from):
        """Parse the message, and call the corresponding method."""
        name, args = message
        fct = getattr(self, "msg_"+name)

        if args:
            fct(name_from, *args)
        else:
            fct(name_from)
        
    def _pipes_update(self):
        """Check for new messages in the pipes (active :())."""
        for (name, pipe) in self._pipes.items():
            while pipe.poll():
                mess = pipe.recv()
                self._parse(mess, name)
                
    def run(self):
        self._loop(None)
        
    def _loop(self, master):
        """The loop, called when the node is started by a manager."""
        
        self._running = True
        self._master = master
        
        self.event_init()
        self._start_attached()        
        
        while self._running:
            self.event_update()
            self._pipes_update()
            
        self._cleanup()
        self.event_stop()
        
    def _cleanup(self):
        fct_alive = lambda name, (process, pipe, node): process.is_alive()
        
        while True in self.map_processes(fct_alive):
            time.sleep(0.01)
        
        
    def map_processes(self, fct):
        return [fct(name, info) for (name, info) in self._processes.items()]
        
    def _start_attached(self):
        self.map_processes(lambda name, (process, pipe, node): process.start())
            
    def _join_attached(self):
        self.map_processes(lambda name, (process, pipe, node): process.join())
        
        
    # == Preset communications facilities
    def msg_sysexit(self, name_from, *args):
        self.map_processes(lambda name, info: self.send("sysexit", name))
        self._running = False
        
    def msg_forward(self, name_from, mess_name, orig_name, args):
        self.send(mess_name, orig_name, *args)
        
        
    # == Overloadable events handler
    def event_init(self):
        """Called when the node is started, should be overloaded."""
        pass
    
    def event_update(self):
        """Called when the node is upated, should be overloaded."""
        pass
    
    def event_stop(self):
        """Called when the node is stopped, should be overloaded."""
        pass
        
