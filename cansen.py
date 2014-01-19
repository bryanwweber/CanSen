#! /usr/bin/python3

import os

import utils
import printer
from run_cases import SimulationCase

def main(argv):
    (inputFilename,outputFilename,mechFilename,
     saveFilename,thermoFilename,convert,) = utils.cli_parser(argv)
    
    out = printer.Tee(outputFilename, 'w')
    
    version = '0.0.1'
    print("This is CanSen, the SENKIN-like wrapper for Cantera, written in \
Python.\nVersion: {!s}\n".format(version))

    keywords, = utils.read_input_file(inputFilename)
    reac,netw,wall,n_vars,sensitivity,tempFunc = setup_case(mechFilename,keywords)
    run_case(reac,netw,wall,n_vars,sensitivity,tempFunc,saveFilename,keywords)
    out.close()
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])


