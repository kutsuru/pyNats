# -*- coding: utf-8 -*-

import multiprocessing
from multiprocessing import Pool
import sys
import time

import pylab as pl

def fibo(n):
    if (n < 2):
        return 1
    else:
        return fibo(n - 1) + fibo(n - 2)

def long_function(n):
    return fibo(20)

def long_function_on_list(ns):
    return sum(map(long_function, ns))
    
def bench_sequential(range_max, result, name):
    t = time.time()
    r = long_function_on_list(xrange(0, range_max))
    elapsed = time.time() - t
    
    if not range_max in result:
        result[range_max] = {}
    result[range_max][name] = {"result": r, "elapsed": elapsed}
    return result

def bench_pool(pool, range_max, result, name):
    
    t = time.time()
    
    step = len(pool._pool) # split for processes
    
    ranges = []
    for i in range(step):
        ranges.append(xrange(i, range_max, step))
    
    r = pool.map(long_function_on_list, ranges)
    r = sum(r)
    elapsed = time.time() - t
    
    if not range_max in result:
        result[range_max] = {}
    result[range_max][name] = {"result": r, "elapsed": elapsed}
    return result    

def main(args):
    p_count = multiprocessing.cpu_count()
    
    results = {}
    print "== Bench on:", p_count, "processors"
    
    pools = [Pool(processes=p_count), Pool(processes=p_count * 2), Pool(processes=p_count / 2)]
    
    for i in range(1000, 3000, 500):
        
        name = "sequential-%imax" % i
        print "* bench:", name
        results = bench_sequential(i, results, name)
        
        for p in pools:
            name = "pool-%imax-%iprocesses" % (i, len(p._pool))
            print "* bench:", name
            results = bench_pool(p, i, results, name)
    
    for (rmax, tests) in results.items():
        r = [v["result"] for v in tests.values()]
        for i in range(1, len(r)):
            if r[i - 1] != r[i]:
                raise Exception("different results!")
    print results
    
    plottable = {}
    plottable["labels"] = []
    plottable["y"] = []

    fig = pl.figure()
    
    for (rmax, tests) in results.items():
        for (name, values) in tests.items():
            elapsed = values["elapsed"]
            
            plottable["labels"].append(name)
            plottable["y"].append(elapsed)
            
    ax = fig.add_subplot(1,1,1)
    y = plottable["y"]
    x = range(len(y))
    
    ax.bar(x, y, facecolor="#EE5555",align="center")
    ax.set_ylabel = time
    ax.set_xticks(x)
    ax.set_xticklabels(plottable["labels"])
    fig.autofmt_xdate()
    
    pl.show()
    
if __name__ == "__main__":
    main(sys.argv)