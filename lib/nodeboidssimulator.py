# -*- coding: utf-8 -*-
from node import Node
import numpy as np
import pygame
import boids_rules
from neighborer import Neighborer

class NodeBoidsSimulator(Node):
    def __init__(self, boids_count, slices=4):
        Node.__init__(self, "simulator.boids")

        self._boids_count = boids_count
        self._slices = slices
        self._wait_ack = False
        
    def event_init(self):
        #create matrix
        boids_count, slices = self._boids_count, self._slices
        self._C = np.random.rand(boids_count, 2)
        self._S = (np.random.rand(boids_count, 2) - 0.5) * 0.1
        self._clock = pygame.time.Clock()
        self._clock.tick()
        
        self._neighborer = Neighborer(slices, boids_count)
        
        self.send_spawn()
        
    def event_update(self):
        delta = self._clock.get_time() / 1000.0
        
        F = np.zeros(self._C.shape)
        self._neighborer.update(self._C, self._S, F)

        rules = [boids_rules.rule_cohesion, boids_rules.rule_separation,
                 boids_rules.rule_alignement]        
        for i in xrange(self._C.shape[0]):
            data = self._neighborer.neighbors_data(i)
            for r in rules:
                F[i,:] += r(*data)
        
        self._F = F
        
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
        if self._wait_ack:
            return
            
        mess = []
        C, S = self._C, self._S
        for i in range(self._boids_count):
            mess.append((i, (C[i,0],C[i,1],S[i,0],S[i,1])))
        self.send("boids_update", "renderer", self._name, mess)
        self._wait_ack = True
        
    def msg_ack_boids_update(self, name_from, *args):
        self._wait_ack = False
        
        
        