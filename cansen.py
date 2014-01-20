#! /usr/bin/python3

import os
import sys
import utils
import printer
from run_cases import SimulationCase

def main(argv):
    filenames,convert, = utils.cli_parser(argv)
    
    output_filename = filenames['output_filename']
    out = printer.Tee(output_filename, 'w')
    
    version = '0.0.1'
    print("This is CanSen, the SENKIN-like wrapper for Cantera, written in "
          "Python.\nVersion: {!s}\n".format(version))

    sim = SimulationCase(filenames,convert)
    sim.run_simulation()
    
    out.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])


