# -*- coding: utf-8 -*-
from node import Node
import numpy as np
import pygame

class NodeBoidsSimulator(Node):
    def __init__(self, boids_count):
        Node.__init__(self, "simulator.boids")

        self._boids_count = boids_count
        
    def event_init(self):
        #create matrix
        boids_count = self._boids_count
        self._C = np.random.rand(boids_count, 2)
        self._S = (np.random.rand(boids_count, 2) - 0.5) * 0.1
        self._F = np.zeros((boids_count, 2))
        self._clock = pygame.time.Clock()
        self._clock.tick()
        
        self.send_spawn()
        
    def event_update(self):
        delta = self._clock.get_time() / 1000.0
        
        self.physic(delta)
        self.send_coordinates()
        self._clock.tick()
    
    def physic(self, delta):
        """Physic, update speeds and coordinates, add friction force."""
        # Friction
        #F -= S * abs(S)
        
        # Autospeed
        #F += (0.5 / ((S + 0.001) * 100))
        
        self._S += self._F * delta
        self._C += self._S * delta
        self._C %= 1
        
    def send_spawn(self):
        C, S = self._C, self._S
        for i in range(self._boids_count):
            data = (i, (C[i,0],C[i,1],S[i,0],S[i,1]))
            self.send("boid_spawn", "renderer", data)
        
    def send_coordinates(self):
        mess = []
        C, S = self._C, self._S
        for i in range(self._boids_count):
            mess.append((i, (C[i,0],C[i,1],S[i,0],S[i,1])))
        self.send("boids_update", "renderer", mess)
        
        