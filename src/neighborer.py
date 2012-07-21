# -*- coding: utf-8 -*-
import numpy as np
import math

class Neighborer(object):
    """
    Compute the neighbor matrix for neighbors
    """
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
                precomp[i][j] = []
                
                neighbors = self._grid[i][j]
                neighbors_count = len(neighbors)
                
                if neighbors_count == 0:
                    continue
                
                for (local_i, global_i) in enumerate(neighbors):
                    
                    def is_visible(neighbor):
                        i_c = self._C[global_i,:]
                        i_s = self._S[global_i,:]
                        n_c = self._C[neighbor,:]
                        
                        v_dist = i_c - n_c
                        dot = np.dot(i_s, v_dist)
                        
                        return dot > 0
                        
                    local_neighbors = filter(is_visible, neighbors)
                    local_neighbors_count = len(local_neighbors)
                    
                    alt_C = np.zeros((local_neighbors_count, 2))
                    alt_S = np.zeros((local_neighbors_count, 2))
                    alt_F = np.zeros((local_neighbors_count, 2))
                    
                    for (local_n, global_n) in enumerate(local_neighbors):
                        alt_C[local_n,:] = C[global_n,:]
                        alt_S[local_n,:] = S[global_n,:]
                        alt_F[local_n,:] = F[global_n,:]
                        
                    precomp[i][j].append((local_neighbors, alt_C, alt_S, alt_F))
                
        self._precomp = precomp
        
    def within_neighbors(self, i):
        gx, gy = self._xy_to_grid(*self._C[i,:])
        
        local_i = self._grid[gx][gy].index(i)
        
        return (self._precomp[gx][gy][local_i][1:], 
                self._grid[gx][gy].index(i))
        
    def leaving_neighbors(self, i, C, S, F):
        gx, gy = self._xy_to_grid(*self._C[i,:])
        neighbors = self._grid[gx][gy][i]
        
        for (local_i, global_i) in enumerate(neighbors):
            self._C[global_i,:] = C[local_i,:]
            self._S[global_i,:] = S[local_i,:]
            self._F[global_i,:] = F[local_i,:]
            
    def grab_csf(self):
        return self._C, self._S, self._F
