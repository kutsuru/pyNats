# -*- coding: utf-8 -*-
import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
import math
from navier_strokes_orig import NavierStrokesOrig
from navier_strokes import NavierStrokes
from OpenGL.arrays import vbo
import OpenGL
from OpenGL.GL import shaders
import time

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

        matrix_width = matrix.shape[0]
        matrix_height = matrix.shape[1]

        self._vertex = np.zeros((nb_squares, 2))
        for i in range(matrix_width):
            for j in range(matrix_height):
                self._vertex[i + j * matrix_width] = (i * step_x, j * step_y)

        self._colors = np.zeros((nb_squares, 3))

        self._nb_squares = nb_squares

    def render(self):

        width = self._matrix.shape[0]
#        cdef int i = 0
#        cdef int width = self._matrix.shape[0]
#        cdef int X, Y
#        cdef float value
#        
        self._colors = self._matrix.reshape(1, self._nb_squares).repeat(3, 0).transpose()

        # Update color array
        """
        it = np.nditer(self._matrix, flags=['multi_index'])
        while not it.finished:
            value, (X, Y) = it[0], it.multi_index
            i = X + width * Y;
            self._colors[i,:] = (value, value, value)
            it.iternext()
        """

        # Render vertex
        glPointSize(40.0)
        glVertexPointerd(self._vertex)
        glColorPointerd(self._colors)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glDrawArrays(GL_POINTS, 0, self._nb_squares)

    def click_at(self, x, y):
        X = int(math.floor((x - self._x) / self._case_width))
        Y = (-1
             + self._matrix.shape[1]
             - int(math.floor((y - self._y) / self._case_height)))

        self._matrix[X, Y] = 0.9
        """
        self._matrix[X + 1, Y] = 0.9
        self._matrix[X - 1, Y] = 0.9
        self._matrix[X, Y + 1] = 0.9
        self._matrix[X, Y - 1] = 0.9
        """
