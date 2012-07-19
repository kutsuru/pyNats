# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 22:58:11 2012

@author: Laurent
"""
import math
import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
import math
from textdisplay import TextDisplay
from boids import Boids

def init():
    pygame.init()
    pygame.display.set_mode((640, 480), OPENGL|DOUBLEBUF)

    glClearColor(1.0, 1.0, 1.0, 0.0)
    glColor3f(0.0, 0.0, 0.0)
    glPointSize(4.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho (0, 640, 0, 480, -1, 1)

def update(delta, debug, speed):
    event = pygame.event.poll ()
    
    if event.type is QUIT:
      sys.exit(0)
    elif event.type is KEYDOWN:
      if event.key is K_ESCAPE:
          sys.exit(0)
      elif event.key is K_d:
          debug = not debug
      elif event.key is K_t:
          speed += 1
      elif event.key is K_s:
          speed -= 1
    
    return debug, speed

def draw(rendered, debug=False):
    glClearColor(0.0, 0.0, 0.0, 1.0);
    glClear(GL_COLOR_BUFFER_BIT)

    for r in rendered:
        r.render(debug=debug)
    glFlush()
    pygame.display.flip()


def main(args):
    init()
    
    bs = Boids(20, 0, 0, 640, 480)
    t = TextDisplay("fps:", 0, 30)
    rendered = [bs, t]

    clock = pygame.time.Clock()
    clock.tick()

    fps = 60
    debug = False
    speed = 0

    while True:
        time_step = (1000. - speed * 100.)
        delta = clock.get_time() / time_step
        debug, speed = update(delta, debug, speed)

        bs.update(delta)

        fps = (fps + clock.get_fps()) / 2.0
        t.text = "fps:" + "%.2f" % (fps)

        draw(rendered, debug=debug)
        clock.tick()

if __name__ == "__main__":
    main(sys.argv[1:])
