# -*- coding: utf-8 -*-
import numpy as np
import math

class Neighborer(object):
    def __init__(self, slices):
        self._slices = slices
        
        self._grid = None
        self._precomp = None
        
        self._C = None
        self._S = None
        self._F = None
        
    def _grid_generate(self):
        # Dummy grid generation
        grid = []
        for i in range(self._slices):
            grid.append([])            
            for j in range(self._slices):
                grid[i].append([])
        return grid
        
    def _xy_to_grid(self, x, y):
        fct = lambda x: int(math.floor(x * self._slices))
        return (fct(x), fct(y))
               
    def _grid_update(self, C):
        self._count = C.shape[0]
        grid = self._grid_generate()
        for i in range(self._count):
            gx, gy = self._xy_to_grid(*C[i,:])
            grid[gx][gy].append(i)
        self._grid = grid
        return grid
        
    def update(self, C, S, F):
        slices = self._slices
        self._grid_update(C)
        
        self._C = C
        self._S = S
        self._F = F
        
        precomp = self._grid_generate()
        for i in range(slices):
            for j in range(slices):
                neighbors = self._grid[i][j]
                neighbors_count = len(neighbors)
                
                if neighbors_count == 0:
                    continue
                
                alt_C = np.zeros((neighbors_count, 2))
                alt_S = np.zeros((neighbors_count, 2))
                alt_F = np.zeros((neighbors_count, 2))

                for (local_i, global_i) in enumerate(neighbors):
                    alt_C[local_i,:] = C[global_i,:]
                    alt_S[local_i,:] = S[global_i,:]
                    alt_F[local_i,:] = F[global_i,:]
                    
                precomp[i][j] = (alt_C, alt_S, alt_F)
                
        self._precomp = precomp
        
    def within_neighbors(self, i):
        gx, gy = self._xy_to_grid(*self._C[i,:])
        return self._precomp[gx][gy]
        
    def leaving_neighbors(self, i, C, S, F):
        gx, gy = self._xy_to_grid(*self._C[i,:])
        neighbors = self._grid[gx][gy]
        
        for (local_i, global_i) in enumerate(neighbors):
            self._C[global_i,:] = C[local_i,:]
            self._S[global_i,:] = S[local_i,:]
            self._F[global_i,:] = F[local_i,:]
            
    def grab_csf(self):
        return self._C, self._S, self._F
