# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 00:26:32 2012

@author: Laurent
"""
import sys
from navier_strokes import NavierStrokes as NS1
from navier_strokes_orig import NavierStrokesOrig as NSO
import numpy as np

def main(args):
    size = 5
    dt = 0.1
    diff = 0.
    visc = 0.
    force = 5.0
    source = 100.
    nats = NSO(size + 2)
    nats2 = NS1(size + 2)
    
    lol = np.zeros((size + 2, size + 2))
    lol[-2, -2] = 0.9
    
    nats.add_source(nats.density, lol, 1)
    nats2.add_source(nats.density, lol, 1)
    
    print nats.density - nats2.density
    print nats.u - nats2.u
    print nats.v - nats2.v
    
    nats.velocity_step(nats.u, nats.v, nats.u_prev, nats.v_prev, visc, dt)
    nats.density_step(nats.density, nats.density_prev, nats.u, nats.v, diff, dt)
    nats2.velocity_step(nats2.u, nats2.v, nats2.u_prev, nats2.v_prev, visc, dt)
    nats2.density_step(nats2.density, nats2.density_prev, nats2.u, nats2.v, diff, dt)

    print nats.density - nats2.density
    print nats.u - nats2.u
    print nats.v - nats2.v
    
if __name__ == "__main__":
    main(sys.argv[1:])