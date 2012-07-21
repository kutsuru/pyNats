# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 22:58:11 2012

@author: Laurent
"""
import sys
import time
import pygame

from pygame.locals import *
from OpenGL.GL import *

from navier_strokes_orig import NavierStrokesOrig
from navier_strokes import NavierStrokes
from lazynavier import LazyNavier

from textdisplay import TextDisplay
from boids import Boids

#import pyximport; pyximport.install()
from matrixdensityslow import MatrixDensity
from matrixvectors import MatrixVectors

class Renderer(object):
    """
    Base class for a renderer (uncomplete).
    """
    def __init__(self, width, height):
        pygame.init()
        pygame.display.set_mode((width, height), OPENGL|DOUBLEBUF)
        
        glClearColor(0.1, 0.1, 0.1, 0.1)
        glColor3f(0.0, 0.0, 0.0)
        glPointSize(4.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho (0, width, 0, height, -1, 1)
        
        self._debug = False
        
    def update(self, delta, mdensity, mvectors):
        event = pygame.event.poll ()
        
        mdensity._matrix *= 0
        mvectors._u *= 0
        mvectors._v *= 0
        
        if event.type is QUIT:
          sys.exit(0)
        elif event.type is KEYDOWN:
          if event.key is K_ESCAPE:
            sys.exit(0)
          elif event.key is K_d:
              self._debug = not self._debug
        elif event.type is MOUSEMOTION    :
            right = event.buttons[2]
            left = event.buttons[0]
            if right:
                lazy = list(event.pos) + list(event.rel)
                mvectors.move_at(*lazy)
            elif left:
                mdensity.click_at(*event.pos)
        
    def draw(self, rendered):
        glClear(GL_COLOR_BUFFER_BIT)
        for r in rendered:
            r.render(self._debug)
        glFlush()
        pygame.display.flip()


def main(args):
    
    width, height = args.size
    bs_size = args.boids
    ns_size = args.navierstrokes
    
    renderer = Renderer(width, height)
    fps = TextDisplay("fps:", 0, 30)
    
    rendered = []

    bs = Boids(bs_size, 0, 0, width, height)
    nats = LazyNavier(NavierStrokes, size=ns_size)
    #nats = LazyNavier(NavierStrokesOrig, size=size)
    
    mdensity = MatrixDensity(nats.me.density_prev, 0, 0, width, height)
    mvectors = MatrixVectors(nats.me.u_prev, nats.me.v_prev, 0, 0, width, height)
    
    if ns_size > 0:
        rendered += [mdensity, mvectors]
    if bs_size > 0:
        rendered.append(bs)        
    rendered.append(fps)
        
    clock = pygame.time.Clock()
    clock.tick()
    
    while True:
        delta = clock.get_time() / 1000.0
        
        renderer.update(delta, mdensity, mvectors)
        
        if ns_size > 0:
            nats.velocity_step(delta)
            nats.density_step(delta)
        if bs_size > 0:
            bs.update(delta)
        
        fps.text = "fps:" + "%.2f" % (clock.get_fps())        
        renderer.draw(rendered)
        
        clock.tick()

if __name__ == "__main__":
    main(sys.argv[1:])
