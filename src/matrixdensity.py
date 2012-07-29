# -*- coding: utf-8 -*-

import numpy as np
import math

from OpenGL.GL import *
from OpenGL.GL.EXT.framebuffer_object import *

class MatrixDensity(object):
    def __init__(self, matrix, x, y, width, height):
        self._matrix = matrix
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        self._matrix_width = matrix.shape[0]

        self._case_width = width / float(matrix.shape[0])
        self._case_height = height / float(matrix.shape[1])

        # Generate the vertex and color array for opengl
        nb_squares = matrix.size

        x, y = 0, 0
        step_x = self._case_width
        step_y = self._case_height

        self._m_width = matrix.shape[0]
        self._m_height = matrix.shape[1]

        print "init"
        # Framebuffer's creation
        self._fbo = glGenFramebuffersEXT(1)
        glEnable(GL_TEXTURE_RECTANGLE_ARB)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self._fbo)
        glDisable(GL_TEXTURE_RECTANGLE_ARB)

        # Texture's creation
        self._id_texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_RECTANGLE_ARB, self._id_texture)

        glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Texture initialization
        glTexImage2D(GL_TEXTURE_RECTANGLE_ARB, 0, GL_RED, self._m_width,
                     self._m_height, 0, GL_RGB, GL_FLOAT, self._matrix)

        # Attach the texture to the framebuffer
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                                  GL_TEXTURE_RECTANGLE_ARB, self._id_texture, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
        print "init end"

    def render(self):

        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self._fbo)
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self._width, self._height)

        glClearDepth(1) # just for completeness
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity()

        glEnable(GL_TEXTURE_2D)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindTexture(GL_TEXTURE_RECTANGLE_ARB, self._id_texture)
        glTexSubImage2D(GL_TEXTURE_RECTANGLE_ARB, 0, 0, 0, self._m_width,
                        self._m_height, GL_RGB, GL_FLOAT, self._matrix)

        glBegin(GL_QUADS);
        glTexCoord2f(0, 0);
        glVertex2f(0, 0);
        glTexCoord2f(self._m_width, 0);
        glVertex2f(self._m_width, 0);
        glTexCoord2f(self._m_width, self._m_height);
        glVertex2f(self._m_width, self._m_height);
        glTexCoord2f(0,self._m_height);
        glVertex2f(0, self._m_height);
        glEnd();

        glDisable(GL_TEXTURE_2D)

        print ">>>DENSITY>>>"
        print self._matrix
        print "<<<DENSITY<<<"

        d = glReadPixels(0, 0, self._m_width, self._m_height, GL_RED, GL_FLOAT)

        print ">>>TEXBUF>>>"
        print d
        print "<<<TEXBUF<<<"

        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        """
        Varray = np.array([[0,0],[0,1],[1,1],[1,0]], np.float32)
        glVertexPointer(2,GL_FLOAT,0,Varray)
        glTexCoordPointer(2,GL_FLOAT,0,Varray)
        indices = [0,1,2,3]
        glDrawElements(GL_QUADS,1,GL_UNSIGNED_SHORT,indices)
        """

    def click_at(self, x, y):
        X = int(math.floor((x - self._x) / self._case_width))
        Y = (-1
             + self._matrix.shape[1]
             - int(math.floor((y - self._y) / self._case_height)))

        self._matrix[X, Y] = 0.9

