# -*- coding: utf-8 -*-
import sys
from node import Node
import os
from noderenderer import NodeRenderer
from nodeboidssimulator import NodeBoidsSimulator

def main(args):
    master = Node("MASTER")
    renderer = NodeRenderer(640, 480)
    boids_simulator = NodeBoidsSimulator(20)
    
    master.attach(renderer)
    master.attach(boids_simulator)
    
    master.run()
    
if __name__ == "__main__":
    main(sys.argv[1:])