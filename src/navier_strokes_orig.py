#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import numpy as np

class NavierStrokesOrig:

    def __init__(self, size):

        self.size = size
        
        self.u = np.zeros((self.size, self.size))
        self.v = np.zeros((self.size, self.size))
        self.u_prev = np.zeros((self.size, self.size))
        self.v_prev = np.zeros((self.size, self.size))

        self.density = np.zeros((self.size, self.size))
        self.density_prev = np.zeros((self.size, self.size))

    def add_source(self, x, s, dt):
        for i in xrange(self.size):
            for j in xrange(self.size):
                x[i][j] += s[i][j] * dt

    def set_boundary(self, b, x):

        for i in xrange(1, self.size - 1):

            if b == 1:
                x[0][i]  = -1 * x[1][i]
                x[-1][i] = -1 * x[-2][i]
            else:
                x[0][i] = x[1][i]
                x[-1][i] = x[-2][i]

            if b == 2:
                x[i][0]  = -1 * x[i][1]
                x[i][-1] = -1 * x[i][-2]
            else:
                x[i][0] = x[i][1]
                x[i][-1] = x[i][-2]

        # Corner
        x[0][0]   = 0.5 * (x[1][0] + x[0][1])
        x[0][-1]  = 0.5 * (x[1][-1] + x[0][-2])
        x[-1][0]  = 0.5 * (x[-2][0] + x[-1][1])
        x[-1][-1] = 0.5 * (x[-2][-1] + x[-1][-2])

    def linear_solve(self, b, x, x_0, a, c):
        for k in xrange(20):
            for i in xrange(1, self.size - 1):
                for j in xrange(1, self.size - 1):
                    x[i][j] = (x_0[i][j] + a * (x[i - 1][j] + x[i + 1][j]
                            + x[i][j - 1] + x[i][j + 1])) / c
            self.set_boundary(b, x)

    def diffuse(self, b, x, x_0, diff, dt):
        a = dt * diff * (self.size - 2)**2
        self.linear_solve(b, x, x_0, a, 1 + 4 * a)

    def advect(self, b, d, d_0, u, v, dt):
        dt_0 = dt * (self.size - 2)

        for i in xrange(1, self.size - 1):
            for j in xrange(1, self.size - 1):
                x = i - dt_0 * u[i][j]
                y = j - dt_0 * v[i][j]

                if x < 0.5:
                    x = 0.5
                elif x > (self.size - 2 + 0.5):
                    x = self.size - 2 + 0.5

                if y < 0.5:
                    y = 0.5
                elif y > (self.size - 2 + 0.5):
                    y = self.size - 2 + 0.5

                i_0 = int(x)
                i_1 = i_0 + 1

                j_0 = int(y)
                j_1 = j_0 + 1

                s_1 = x - i_0
                s_0 = 1 - s_1

                t_1 = y - j_0
                t_0 = 1 - t_1

                d[i][j] = s_0 * (t_0 * d_0[i_0, j_0] + t_1 * d_0[i_0][j_1]) +\
                          s_1 * (t_0 * d_0[i_1][j_0] + t_1 * d_0[i_1][j_1])

        self.set_boundary(b, d)

    def project(self, u, v, p , div):

        h = 1. / (self.size - 2)        
        
        for i in xrange(1, self.size - 1):
            for j in xrange(1, self.size - 1):
                div[i][j] = -0.5 * h * (u[i + 1][j] - u[i - 1][j] + v[i][j + 1]
                        - v[i, j - 1])
                p[i][j] = 0
        self.set_boundary(0, div)
        self.set_boundary(0, p)
        
        self.linear_solve(0, p, div, 1, 4)

        for i in xrange(1, self.size - 1):
            for j in xrange(1, self.size - 1):
                u[i][j] -= 0.5 * (p[i + 1][j] - p[i - 1][j]) / h
                v[i][j] -= 0.5 * (p[i][j + 1] - p[i][j - 1]) / h

        self.set_boundary(1, u)
        self.set_boundary(2, v)

    def density_step(self, x, x_0, u, v, diff, dt):
        self.add_source(x, x_0, dt)

        x, x_0 = x_0, x # Swap
        self.diffuse(0, x, x_0, diff, dt)

        x, x_0 = x_0, x # Swap
        self.advect(0, x, x_0, u, v, dt)

    def velocity_step(self, u, v, u_0, v_0, visc, dt):
        self.add_source(u, u_0, dt)
        self.add_source(v, v_0, dt)

        u, u_0 = u_0, u #Swap
        self.diffuse(1, u, u_0, visc, dt)
        v, v_0 = v_0, v #Swap
        self.diffuse(2, v, v_0, visc, dt)

        self.project(u, v, u_0, v_0)

        u, u_0 = u_0, u #Swap
        v, v_0 = v_0, v #Swap
        self.advect(1, u, u_0, u_0, v_0, dt)
        self.advect(2, v, v_0, u_0, v_0, dt)

        self.project(u, v, u_0, v_0)


def main(argv):
    size = 128
    dt = 0.1
    diff = 0.
    visc = 0.
    nats = NavierStrokesOrig(size + 2)

    nats.velocity_step(nats.u, nats.v, nats.u_prev, nats.v_prev, visc, dt)
    nats.density_step(nats.density, nats.density_prev, nats.u, nats.v, diff, dt)

if __name__ == "__main__":
    main (sys.argv[1:])
