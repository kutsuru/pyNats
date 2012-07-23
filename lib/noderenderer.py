# -*- coding: utf-8 -*-

import sys
import time
import pygame
from node import Node
import math

from pygame.locals import *
from OpenGL.GL import *

class NodeRenderer(Node):
    def __init__(self, width, height):
        Node.__init__(self, "renderer")
        self._boids_count = 0
        self._boids_coordinates = {}
        self.width, self.height = width, height
        
    def event_init(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), OPENGL|DOUBLEBUF)
        
        glClearColor(0.1, 0.1, 0.1, 0.1)
        glColor3f(0.0, 0.0, 0.0)
        glPointSize(4.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho (0, self.width, 0, self.height, -1, 1)
        
        self._clock = pygame.time.Clock()
        self.mean_fps = 60.0
        
        self._debug = False
        
    def event_update(self):
        self.update_events()
        self.draw()
        
        self.mean_fps = (self.mean_fps + self._clock.get_fps()) / 2.0        
        self._clock.tick()
        
    def msg_sysexit(self, *args):
        print self.mean_fps
        Node.msg_sysexit(self, *args)
        
    def msg_boid_spawn(self, name_from, (boid_id, coords)):        
        self._boids_count += 1
        self._boids_coordinates[boid_id] = coords
        
    def msg_boids_update(self, name_from, sender, boids):
        for (boid_id, coords) in boids:
            self._boids_coordinates[boid_id] = coords
        self.send("ack_boids_update", sender)
        
    def update_events(self):        
        event = pygame.event.poll()
        if event.type is QUIT:
            self.send("sysexit", self._master)
        elif event.type is KEYDOWN:
            if event.key is K_ESCAPE:
                self.send("sysexit", self._master)
            elif event.key is K_d:
                self._debug = not self._debug

        
    def draw(self):        
        glClear(GL_COLOR_BUFFER_BIT)
        
        self._render_boids()
        glFlush()
        pygame.display.flip()

        
    def _render_boids(self):
        glPushMatrix()
        
        for (b_id, (x, y, dir_x, dir_y)) in self._boids_coordinates.items():
            x *= self.width
            y *= self.height
            self._render_boid(x, y, dir_x, dir_y)
            
        glPopMatrix()

        
    def _render_boid(self, x, y, dir_x, dir_y):
        
        color = (0.2, 1.0, 0.2)
        wd2, h = 10 / 2., 10.
        direction = math.degrees(math.atan2(dir_y, dir_x))
        
        glPushMatrix()
        glTranslatef(x, y, 0.)
        
        if self._debug:
            glBegin(GL_LINES)
            glColor3f(*(0.2, 0.8, 0.8))
            glVertex2f(0, 0)
            glColor3f(*(0.2, 0.8, 0.8))
            glVertex2f(200 * dir_x, 200 * dir_y)
            glEnd()

        glRotatef(direction, 0.0, 0.0, 1.0)
        glBegin(GL_TRIANGLES)
        glColor3f(*color)
        glVertex2f(h, 0)
        glColor3f(*color)
        glVertex2f(0, wd2)
        glColor3f(*color)
        glVertex2f(0, -wd2)
        glEnd()

        glPopMatrix()
        

