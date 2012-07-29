# -*- coding: utf-8 -*-
import sys
from src.renderer import main as renderer_main
import argparse

def parser():
    parser = argparse.ArgumentParser(description='pyNats simulator.')
    
    parser.add_argument('--size', nargs=2, type=int, default=[640, 480],
                        help="set the rendering size (width x height)")
    parser.add_argument("-b", "--boids", type=int, default=0,
                        help="activate boids simulation, with the given number")
    parser.add_argument("-n", "--navierstrokes", type=int, default=20,
                        help="activate Navier Strokes simulation, with the given count")
    return parser

def main(args):

    p = parser()
    parsed = p.parse_args()
    renderer_main(parsed)

if __name__ == "__main__":
    main(sys.argv[1:])