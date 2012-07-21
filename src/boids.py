# -*- coding: utf-8 -*-
from neighborer import Neighborer
import numpy as np
import math
from pygame.locals import *
from OpenGL.GL import *
import boids_rules

class Boids(object):
    """Boids simulator"""
    def __init__(self, count, x, y, width, height, slices=6):
        self._count = count

        self._coordinates = np.random.rand(count, 2)
        self._speeds = (np.random.rand(count, 2) - 0.5) * 0.1
        self._forces = np.zeros((count, 2))

        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._neighborer = Neighborer(slices)
        
    def update(self, delta):
        """Update the simulation, apply forces, move the boids,..."""
        self._forces = np.zeros(self._forces.shape)
        C, S, F = self._coordinates, self._speeds, self._forces
        self._neighborer.update(C, S, F)
        
        rules = [boids_rules.rule_cohesion, boids_rules.rule_separation,
                 boids_rules.rule_alignement]
        
        for i in xrange(C.shape[0]):
            data = self._neighborer.neighbors_data(i)
            for r in rules:
                F[i,:] += r(*data)
        
        C, S, F = self.physic(C, S, F, delta)
        self._coordinates, self._speeds, self._forces =  C, S, F
        
    def physic(self, C, S, F, delta):
        """Physic, update speeds and coordinates, add friction force."""
        # Friction
        F -= S * abs(S)
        #F += (1 / ((S + 0.0001) * 1000))
        
        accel = F
        S += accel * delta
        C += S * delta
        C %= 1
        
        return (C, S, F)
        
    def render_boid(self, i, x, y, direction, color=(0.0, 1.0, 0.0), debug=False):
        wd2, h = 10 / 2., 10.
        
        glPushMatrix()
        glTranslatef(x, y, 0.)
        
        if debug:
            glBegin(GL_LINES)
            glColor3f(*(0.2, 0.2, 0.8))
            glVertex2f(0, 0)
            glColor3f(*(0.2, 0.2, 0.8))
            glVertex2f(*(self._forces[i,:] * 200))
            
            
            glColor3f(*(0.2, 0.8, 0.8))
            glVertex2f(0, 0)
            glColor3f(*(0.2, 0.8, 0.8))
            glVertex2f(*(self._speeds[i,:] * 200))
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

    def render(self, debug=False):
        glPushMatrix()
        glTranslatef(self._x, self._y, 0.)

        for i in range(self._coordinates.shape[0]):
            vx, vy = self._speeds[i, :]
            d = math.degrees(math.atan2(vy, vx))

            x, y = self._coordinates[i, :]
            x = (x * self._width)
            y = (y * self._height)
            
            self.render_boid(i, x, y, d, debug=debug)
            
        glPopMatrix()
