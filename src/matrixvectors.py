# -*- coding: utf-8 -*-
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
import math

class MatrixVectors(object):
    """Speed vectors interaction and rendering"""
    def __init__(self, u, v, x, y, width, height):
        self._u = u
        self._v = v
        self._x = x
        self._y= y
        self._width = width
        self._height = height
        
        self._case_width = width / float(u.shape[0])
        self._case_height = height / float(v.shape[1])
    
    def render(self):
        
        w = self._case_width
        h = self._case_height
        
        it = np.nditer(self._u, flags=['multi_index'])
        
        glColor3f (1.0, 0.0, 0.0);
        glLineWidth(1.0);

        glBegin(GL_LINES)
        while not it.finished:
            value_u, (X, Y) = it[0], it.multi_index
            value_v = self._v[X, Y]
            
            x = self._x + (X + 0.5) * w
            y = self._y + (Y + 0.5) * h
            
            glVertex2f(x, y)
            glVertex2f(x + value_u * w, y + value_v * h)
            
            it.iternext()
        glEnd()
        
    def move_at(self, x, y, rel_x, rel_y):    
        X = int(math.floor((x - self._x) / self._case_width))
        Y = (-1
             + self._u.shape[1]
             - int(math.floor((y - self._y) / self._case_height)))
        
        REL_X = rel_x / self._case_width
        REL_Y = rel_y / self._case_height
        
        self._u[X, Y] = REL_X
        self._v[X, Y] = -REL_Y

        self._u[X+1, Y] = REL_X / 2.0
        self._v[X+1, Y] = -REL_Y / 2.0
        self._u[X-1, Y] = REL_X / 2.0
        self._v[X-1, Y] = -REL_Y / 2.0
        self._u[X, Y+1] = REL_X / 2.0
        self._v[X, Y+1] = -REL_Y / 2.0        
        self._u[X, Y-1] = REL_X / 2.0
        self._v[X, Y-1] = -REL_Y / 2.0
