#! /usr/bin/python3

import os

import utils
import printer
from run_cases import run_case

def main(argv):
    (inputFilename,outputFilename,mechFilename,
     saveFilename,thermoFilename,convert,) = utils.cli_parser(argv)
    
    out = printer.Tee(outputFilename, 'w')
    
    version = '0.0.1'
    print("This is CanSen, the SENKIN equivalent for Cantera, written in \
Python.\nVersion: {!s}\n".format(version))
    
    if mechFilename.endswith('.inp'):
        from cantera import ck2cti
        arg = list('--input='+mechFilename)
        if thermoFilename is not None:
            if os.path.isfile(thermoFilename):
                arg.append('--thermo='+thermoFilename)
            else:
                print('Error: Specify proper thermo file')
        ck2cti.main(arg)
        mechFilename = mechFilename[:-4]+'.cti'
        print(mechFilename)
    
    if convert:
        sys.exit(0)
        
    ret, = utils.read_input_file(inputFilename)
    run_case(mechFilename,saveFilename,ret)
    out.close()
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])


