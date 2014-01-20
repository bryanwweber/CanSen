#! /usr/bin/python3

# Standard libraries
import os
import sys
import utils

#Local imports
from printer import Tee
from run_cases import SimulationCase

def main(argv):
    """The main driver function of CanSen."""
    __version__ = '0.0.1'
    
    # Parse the command line input
    filenames,convert, = utils.cli_parser(argv)
    
    # Open the text output file from the printer module
    output_filename = filenames['output_filename']
    out = Tee(output_filename, 'w')
    
    # Print version information to screen at the start of the problem
    print("This is CanSen, the SENKIN-like wrapper for Cantera, written in "
          "Python.\nVersion: {!s}\n".format(version))

    # Run the simulation
    sim = SimulationCase(filenames,convert)
    sim.run_simulation()
    
    # Clean up
    out.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])


