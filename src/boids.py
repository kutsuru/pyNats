# -*- coding: utf-8 -*-
from neighborer import Neighborer
import numpy as np
import math
from pygame.locals import *
from OpenGL.GL import *


class Boids(object):
    def __init__(self, count, x, y, width, height, slices=1):
        count = 4
        self._count = count

        self._coordinates = np.random.rand(count, 2)
        self._speeds = np.random.rand(count, 2) - 0.5
        self._forces = np.random.rand(count, 2) - 0.5
        
        self.gravity = np.zeros((1, 2))

        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._neighborer = Neighborer(slices)
        
    def update(self, delta):
        self._forces = np.zeros(self._forces.shape)
        C, S, F = self._coordinates, self._speeds, self._forces
        
        C, S, F = self.bounding(C, S, F, delta)
        C, S, F = self.cohesion(C, S, F, delta)
        C, S, F = self.alignement(C, S, F, delta)
        
        C, S, F = self.physic(C, S, F, delta)
        self._coordinates, self._speeds, self._forces =  C, S, F
        
    def cohesion(self, C, S, F, delta):
        self._neighborer.update(C, S, F)
        
        for i in range(self._count):
            nC, nS, nF = self._neighborer.within_neighbors(i)
            
            count = nC.shape[0]
            
            if count > 1:
                g = nC.mean(0)
                G = np.tile(g, (count, 1))
                nF += (G - nC)
            
            self._neighborer.leaving_neighbors(i, nC, nS, nF)
            
        return self._neighborer.grab_csf()
        
    def alignement(self, C, S, F, delta):
        self._neighborer.update(C, S, F)
        
        for i in range(self._count):
            nC, nS, nF = self._neighborer.within_neighbors(i)
            
            count = nC.shape[0]
            
            if count > 1:
                gf = nF.mean(0)
                Gf = np.tile(gf, (count, 1))
                nF += (Gf - nF)
            
            self._neighborer.leaving_neighbors(i, nC, nS, nF)
            
        return self._neighborer.grab_csf()
                
    def bounding(self, C, S, F, delta):
        bound = 0.1
        bound_left = bound
        bound_right = 1 - bound
        bound_top = 1 - bound
        bound_bottom = bound
        
        
        for i in range(C.shape[0]):
            if C[i,0] < bound_left:
                F[i,0] += 0.9
            elif C[i,0] > bound_right:
                F[i,0] -= 0.9
                
            if C[i,1] < bound_bottom:
                F[i,1] += 0.9
            elif C[i,1] > bound_top:
                F[i,1] -= 0.9
                
        return (C, S, F)
    
    def physic(self, C, S, F, delta):
        F -= S * abs(S)
        accel = F / 1.0
        
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
