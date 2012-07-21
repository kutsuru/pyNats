# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 13:50:28 2012

@author: Laurent
"""
import numpy as np

class LazyNavier(object):
    """Encapsulate a NavierStrokes solver."""
    def __init__(self, main, size=5, dt=.1, diff=0., visc=0., force=5.,
                 source=100.):
        self.size = size + 2
        self.dt = dt
        self.diff = diff
        self.visc = visc
        self.force = force
        self.source = source
        
        self.me = main(self.size)
        
    def velocity_step(self, dt=None):
        if dt is None:
            dt = self.dt
            
        self.me.velocity_step(self.me.u, self.me.v,
                              self.me.u_prev, self.me.v_prev,
                              self.visc, dt)
                              
    def density_step(self, dt=None):
        if dt is None:
            dt = self.dt
                              
        self.me.density_step(self.me.density, self.me.density_prev,
                             self.me.u, self.me.v, self.diff, dt)        

def show_v(v):
    """Debug visualisation for speed matrix"""
    for i in range(len(v)):
        for j in range(len(v[i])):
            print "(%.2f, %.2f) " % v[i][j],
        print
    
def main():
    """Testing main, comparing the NavierStrokes solver"""
    from navier_strokes_orig import NavierStrokesOrig
    size = 5
    n = LazyNavier(NavierStrokesOrig, size=size)
    
    n.me.density[2, 2] = 0.5
    n.me.u[2, 2] = 0.1
    
    def show():
        print "density:"        
        print n.me.density
        print "velocity:"
        show_v(n.velocity())
        
    print "=" * 5, "init"
    show()
    
    for i in range(2):
        print "=" * 5, "tick", i
        
        n.density_step()
        n.velocity_step()
        
        n.me.density_prev = np.zeros((size, size))
        n.me.u_prev = np.zeros((size, size))
        n.me.v_prev = np.zeros((size, size))
        
        show()


if __name__ == "__main__":
    main()