# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 14:56:34 2012

@author: Laurent
"""
import numpy as np

def rule_separation(C, neighbors_C, neighbors_S, neighbors_count):
    
    vectors = C - neighbors_C
    lengths = np.sum(vectors ** 2, axis=1) ** 0.5
    coefs = 1 / (1 + 500 * lengths)
    F = np.zeros(1, 2)
    
    for i in xrange(vectors.shape[0]):
        if lengths[i] < 0.1:
            F += (vectors[i,:] / lengths[i]) * coefs[i]
    return F


def rule_bounding(C, neighbors_C, neighbors_S, neighbors_count):
    bound = 0.1
    bound_left = bound
    bound_right = 1 - bound
    bound_top = 1 - bound
    bound_bottom = bound
    
    F = np.zeros(2)
    
    if C[0] < bound_left:
        F[0] += 0.9
    elif C[0] > bound_right:
        F[0] -= 0.9
        
    if C[1] < bound_bottom:
        F[1] += 0.9
    elif C[1] > bound_top:
        F[1] -= 0.9
            
    return F
    
    