#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import numpy as np

# Cuda import
import pycuda.driver as cuda
import pycuda.autoinit

import pycuda.gpuarray as gpuarray
from pycuda.compiler import SourceModule



class NavierStrokesCuda:

    def __init__(self, size):
        self.size = size
        self.debug = False

        # Initialization of the data
        self.u = np.zeros((size, size)).astype(np.float32)
        self.v = np.zeros((size, size)).astype(np.float32)
        self.u_prev = np.zeros((size, size)).astype(np.float32)
        self.v_prev = np.zeros((size, size)).astype(np.float32)

        self.density = np.zeros((size, size)).astype(np.float32)
        self.density_prev = np.zeros((size, size)).astype(np.float32)

        self.advect_mod = SourceModule("""
        __global__ void advect_gpu(float* u, float* v, float* d, float* d0,
                               int size, float dt0)
        {
            int idx = threadIdx.x + threadIdx.y * size;

            float x = threadIdx.x - dt0 * u[idx];
            float y = threadIdx.y - dt0 * v[idx];

            x = (x + 0.5 + abs(x - 0.5)) / 2;
            y = (x + size - 2 + 0.5 - abs(x - (size - 2 + 0.5))) / 2;

            int i0 = (int) threadIdx.x;
            int i1 = i0 + 1;

            int j0 = (int) threadIdx.y;
            int j1 = j0 + 1;

            int s1 = x - i0;
            int s0 = 1 - s1;

            int t1 = y - j0;
            int t0 = 1 - t1;

            d[idx] = s0 * (t0 * d0[i0 + j0 * size] + t1 * d0[i0 + j1 * size]) +
                     s1 * (t0 * d0[i1 + j0 * size] + t1 * d0[i1 + j1 * size]);
        }
        """)
        self.func_advect = self.advect_mod.get_function("advect_gpu")

        self.easy_mod = SourceModule("""
        #include <stdio.h>

        __global__ void easy_gpu(float* u, float* v, float* d, float* d0)
        {

            int size = 14;

            float dt  = 0.1;
            float dt0 = dt * size;

            int idx = threadIdx.x + threadIdx.y * size;

            float x = threadIdx.x + 1 - dt0 * u[idx];
            float y = threadIdx.y + 1 - dt0 * v[idx];

            x = (x + 0.5 + abs(x - 0.5)) / 2;
            x = (x + size + 0.5 - abs(x - (size + 0.5))) / 2;

            y = (y + 0.5 + abs(y - 0.5)) / 2;
            y = (y + size + 0.5 - abs(y - (size + 0.5))) / 2;

            int i0 = (int) x;
            int i1 = i0 + 1;

            int j0 = (int) y;
            int j1 = j0 + 1;

            int s1 = x - i0;
            int s0 = 1 - s1;

            int t1 = y - j0;
            int t0 = 1 - t1;

            d[idx] = s0 * (t0 * d0[i0 + j0 * (size + 2)] +
                           t1 * d0[i0 + j1 * (size + 2)])
                   + s1 * (t0 * d0[i1 + j0 * (size + 2)] +
                           t1 * d0[i1 + j1 * (size + 2)]);
        }
        """)
        self.func_easy = self.easy_mod.get_function("easy_gpu")

    # Add the source to the density
    def add_source(self, x, s, dt):
        x += s * dt

    def set_boundary(self, b, x):
        # Boundary lines
        if b == 1:
            x[0]  = -1 * x[1]
            x[-1] = -1 * x[-2]
        else:
            x[0] = x[1]
            x[-1] = x[-2]

        t_x = x.transpose()

        if b == 2:
            t_x[0]  = -1 * t_x[1]
            t_x[-1] = -1 * t_x[-2]
        else:
            t_x[0] = t_x[1]
            t_x[-1] = t_x[-2]

        # Corner
        x[0][0]   = 0.5 * (x[1][0] + x[0][1])
        x[0][-1]  = 0.5 * (x[1][-1] + x[0][-2])
        x[-1][0]  = 0.5 * (x[-2][0] + x[-1][1])
        x[-1][-1] = 0.5 * (x[-2][-1] + x[-1][-2])

    def linear_solve(self, b, x, x_0, a, c):
        for i in xrange(20):
            x[1:-1, 1:-1] = (x_0[1:-1, 1:-1] + a * (x[:-2, 1:-1] + x[2:, 1:-1]
                    + x[1:-1, :-2] + x[1:-1, 2:])) / c
            self.set_boundary(b, x)

    def diffuse(self, b, x, x_0, diff, dt):
        a = dt * diff * (self.size - 2)**2
        self.linear_solve(b, x, x_0, a, 1 + 4 * a)

    def advect(self, b, d, d_0, u, v, dt):
        size = self.size - 2
        dt_0 = dt * (size)

        bX = size
        bY = size
        gX = 1
        gY = 1

        u_gpu = cuda.mem_alloc(u[1:-1, 1:-1].nbytes)
        cuda.memcpy_htod(u_gpu, u[1:-1, 1:-1].reshape(size**2))

        #u_gpu = cuda.In(u[1:-1, 1:-1].reshape(size**2))

        if self.debug and not np.array_equal(u, np.zeros((self.size, self.size))):
            print ">>> U"
            print u
            print "<<< U"

        v_gpu = cuda.mem_alloc(v[1:-1, 1:-1].nbytes)
        cuda.memcpy_htod(v_gpu, v[1:-1, 1:-1].reshape(size**2))

        #v_gpu = cuda.In(v[1:-1, 1:-1].reshape(size**2))

        d_0_gpu = cuda.mem_alloc(d_0.nbytes)
        cuda.memcpy_htod(d_0_gpu, d_0.reshape(self.size**2))

        #d_0_gpu = cuda.In(d_0.reshape(self.size**2))

        #d_gpu = cuda.mem_alloc(d[1:-1, 1:-1].nbytes)
        #cuda.memcpy_htod(d_gpu, d[1:-1, 1:-1].reshape(size**2))

        d_gpu = cuda.Out(d[1:-1, 1:-1].reshape(size**2))

        if self.debug:
            print ">>> Entry >>>"
            print d[1:-1, 1:-1]
            print "<<< Kernel Launch <<<"

        self.func_easy(u_gpu, v_gpu, d_gpu, d_0_gpu,
                       block=(bX, bY, 1), grid=(gX, gY))

        #d_result = np.empty_like(d[1:-1, 1:-1]).astype(np.float32)
        #cuda.memcpy_dtod(d_result, d_gpu, d_result.nbytes)

        if self.debug:
            print ">>> Result >>>"
            print d[1:-1, 1:-1]
            print "<<< End Result <<<"

        #d[1:-1, 1:-1] = d_result
        self.set_boundary(b, d)

    def project(self, u, v, p , div):
        div[1:-1, 1:-1] = -0.5 * (u[2:, 1:-1] - u[:-2, 1:-1] + v[1:-1, 2:] -
                          v[1:-1, :-2]) / (self.size - 2)
        self.set_boundary(0, div)

        p = np.zeros((self.size, self.size))

        self.linear_solve(0, p, div, 1, 4)

        u[1:-1, 1:-1] -= 0.5 * (self.size - 2) * (p[2:, 1:-1] - p[:-2, 1:-1])
        v[1:-1, 1:-1] -= 0.5 * (self.size - 2) * (p[1:-1, 2:] - p[1:-1, :-2])

        self.set_boundary(1, u)
        self.set_boundary(2, v)


    def density_step(self, x, x_0, u, v, diff, dt):
        if self.debug:
            print "DENSITY STEP >>>"

        self.debug = False
        self.add_source(x, x_0, dt)

        x, x_0 = x_0, x # Swap
        self.diffuse(0, x, x_0, diff, dt)

        x, x_0 = x_0, x # Swap
        self.advect(0, x, x_0, u, v, dt)

        if self.debug:
            print "<<< DENSITY STEP"

    def velocity_step(self, u, v, u_0, v_0, visc, dt):
        if self.debug:
            print "VELOCITY STEP >>>"

        self.debug = False
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

        if self.debug:
            print "<<< VELOCITY STEP"


def main(argv):
    pass

if __name__ == "__main__":
    main (sys.argv[1:])
