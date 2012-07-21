# -*- coding: utf-8 -*-
import numpy as np
import math

class Neighborer(object):
    """Compute the neighbor matrix for boids."""
    def __init__(self, slices):
        self._slices = slices
        
        self._grid = None
        self._precomp = None
        
        self._C = None
        self._S = None
        self._F = None

        
    def _xy_to_grid(self, x, y):
        """conversion from global to grid space coordinates."""
        fct = lambda x: int(math.floor(x * self._slices))
        return (fct(x), fct(y))
        
    def _grid_construct(self):
        """Dummy grid generation."""
        return [[[] for i in range(self._slices)] for j in range(self._slices)]

    def _grid_boids_fill(self, C, grid):
        """Construct the boids grid"""
        for i in xrange(C.shape[0]):
            x, y = self._xy_to_grid(*C[i,:])
            grid[x][y].append(i)
        return grid
        
    def _build_neighborhoods(self, x, y, grid_boids):
        """Grab the boids at (x, y), (x - 1, y), (x, y - 1),..."""
        coord_max = self._slices - 1
        neighbors = list(grid_boids[x][y])
            
        if x > 0:
            neighbors += grid_boids[x - 1][y]
        if x < coord_max:
            neighbors += grid_boids[x + 1][y]
            
        if y > 0:
            neighbors += grid_boids[x][y - 1]
        if y < coord_max:
            neighbors += grid_boids[x][y + 1]
            
        return neighbors
        
    def _grid_neighborhoods(self, C, grid_boids):
        """Construct the neighborshoods grid (4 connectivity on grid_boids)."""
        grid = []
        for i in range(self._slices):
            n = []
            for j in range(self._slices):
                n.append(self._build_neighborhoods(i, j, grid_boids))
            grid.append(n)
        return grid
        
    def _map_visible(self, C, S, grid_neighborhoods):
        """Compute the [id1 -> [neighbor11,...]] map."""
        
        visible = []
        for i in range(C.shape[0]):
            gx, gy = self._xy_to_grid(*C[i,:])
            
            neighbors = grid_neighborhoods[gx][gy]
            # Keep neighbors that i can see:
            # (speed & neighbor_vector with the same direction)
            neighbors = filter(lambda n: (n != i) 
                                         and (np.dot(C[n] - C[i], S[i]) > 0),
                               neighbors)
            visible.append(neighbors)
            
        return visible

    def _map_data(self, C, S, F, map_visible):
        """Compute the C, S for each neighborhoods."""
        
        data = []
        
        for i in xrange(C.shape[0]):
            neighbors = map_visible[i]
            neighbors_count = len(neighbors)
            neighbors_C = np.zeros((neighbors_count, 2))
            neighbors_S = np.zeros((neighbors_count, 2))
            
            for j in xrange(neighbors_count):
                neighbors_id = neighbors[j]
                neighbors_C[j,:] = C[neighbors_id,:]
                neighbors_S[j,:] = S[neighbors_id,:]
                
            data.append((C[i,:], neighbors_C, neighbors_S, neighbors_count))      
        return data
                        
    def update(self, C, S, F):
        self._C, self._S, self._F = C, S, F
        
        # Spatial organization
        grid_boids = self._grid_construct()
        grid_boids = self._grid_boids_fill(C, grid_boids)
        
        # Neighborhoods constructions
        grid_neighborhoods = self._grid_neighborhoods(C, grid_boids)
        
        # Grid visible
        map_visible = self._map_visible(C, S, grid_neighborhoods)
        
        # Neighbors data construction
        map_data = self._map_data(C, S, F, map_visible)
        
        self._boids = grid_boids
        self._neighborhoods = grid_neighborhoods
        self._visible = map_visible
        self._data = map_data
        
    def neighbors_data(self, i):
        """Return the i coordinates,
           and it's neighbors data: C, S, count."""
        return self._data[i]
        
    def grab_csf(self):
        return self._C, self._S, self._F
