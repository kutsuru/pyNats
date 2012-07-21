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
    def init(self):
        pygame.init()
        pygame.display.set_mode((640, 480), OPENGL|DOUBLEBUF)
        
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glColor3f(0.0, 0.0, 0.0)
        glPointSize(4.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho (0, 640, 0, 480, -1, 1)
        
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
        elif event.type is MOUSEMOTION	:
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
            r.render()
        glFlush()
        pygame.display.flip()


def main(args):
    renderer = Renderer()
    renderer.init()
    
    bs = Boids(20, 0, 0, 640, 480)
    fps = TextDisplay("fps:", 0, 30)
    
    size = 30
    nats = LazyNavier(NavierStrokes, size=size)
    #nats = LazyNavier(NavierStrokesOrig, size=size)
    
    mdensity = MatrixDensity(nats.me.density_prev, 0, 0, 640, 480)
    mvectors = MatrixVectors(nats.me.u_prev, nats.me.v_prev, 0, 0, 640, 480)
    
    rendered = [mdensity, mvectors, bs, fps]
    
    clock = pygame.time.Clock()
    clock.tick()
    
    while True:
        delta = clock.get_time() / 1000.0
        
        renderer.update(delta, mdensity, mvectors)
        
        nats.velocity_step(delta)
        nats.density_step(delta)
        
        #bs.update(delta)
        
        fps.text = "fps:" + "%.2f" % (clock.get_fps())
        
        renderer.draw(rendered)
        
        clock.tick()

if __name__ == "__main__":
    main(sys.argv[1:])
