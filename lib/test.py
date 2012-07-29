# -*- coding: utf-8 -*-
import sys
import os

from node import Node
from noderenderer import NodeRenderer
from nodeboidssimulator import NodeBoidsSimulator
from dummynode import DummyNode

def dummy_test():
    d1 = DummyNode("dummy")
    d2 = DummyNode("dumby")
    d3 = DummyNode("tardy")
    
    master = Node("MASTER")
    
    master.attach(d1)
    master.attach(d2)
    master.attach(d3)

    master.run()
    
def engine_test(count):
    master = Node("MASTER")
    renderer = NodeRenderer(640, 480)
    boids_simulator = NodeBoidsSimulator(count)
    
    master.attach(renderer)
    master.attach(boids_simulator)
    
    master.run()
    
def main(args):
    dummy_test()
    engine_test(int(args[0]))
    
if __name__ == "__main__":
    main(sys.argv[1:])