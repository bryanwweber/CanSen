#! /usr/bin/env python3

# Python 2 compatibility
from __future__ import print_function

# Standard libraries
import sys
import os

#Local imports
import utils
from printer import Tee
from run_cases import SimulationCase, MultiSimulationCase

def main(filenames, convert, multi, version):
    """The main driver function of CanSen.
    
    :param filenames:
        Dictionary of filenames related to the simulation.
    :param convert:
        Boolean indicating that the user wishes only to convert the 
        input mechanism and quit.
    :param multi:
        Boolean indicating multiple cases to be run.
    :param version:
        Version string of CanSen.
    """

    # Open the text output file from the printer module
    output_filename = filenames['output_filename']
    out = None
    if multi:
        out = open(output_filename, 'w')
    else:
        out = Tee(output_filename, 'w')
    
    if not multi:
        # Print version information to screen at the start of the problem
        print("This is CanSen, the SENKIN-like wrapper for Cantera, "
              "written in Python.\nVersion: {!s}\n".format(version))
    
    # Convert the mechanism if it is in CHEMKIN format. If ``convert`` 
    # is True, exit the simulation.
    mech_filename = filenames['mech_filename']
    thermo_filename = filenames['thermo_filename']
    if mech_filename.endswith('.inp'):
        mech_filename = utils.convert_mech(mech_filename, thermo_filename)
    
    if convert:
        print('User requested conversion only. Goodbye.')
        sys.exit(0)
    
    # Run the simulation
    if multi:
        # need to preprocess the input file to separate the various
        input_files = utils.process_multi_input(filenames['input_filename'])
        
        # create data list
        data_lst = [None] * len(input_files)
        
        f = open(os.devnull, 'w')
        orig_stdout = sys.stdout
        
        for i in range(len(input_files)):
            
            # avoid writing anything to screen during setup/run            
            sys.stdout = f
            
            local_names = filenames.copy()
            local_names['input_filename'] = input_files[i]
            sim = MultiSimulationCase(local_names)
            sim.run_simulation()
            
            data_lst[i] = [sim.ignition_time,
                           sim.keywords['pressure'],
                           sim.keywords['temperature']]
            
            # store equivalence ratio if possible
            if sim.keywords['eqRatio'] != None:
                data_lst[i].append(sim.keywords['eqRatio'])
            
            print('Done with ' + str(i), file = orig_stdout)
        
        # clean up
        utils.remove_files(input_files)
        sys.stdout = orig_stdout
                
        # write output
        print('# Ignition delay [s], Pressure [atm], Temperature [K], '
              'Equivalence ratio', file = out)
        
        for res in data_lst:
            if len(res) == 3:
                line = '{:.8e} {:.2f} {:.1f}'.format(*res)
            elif len(res) == 4:
                line = '{:.8e} {:.2f} {:.1f} {:.2f}'.format(*res)
            print(line, file = out)
        
    else:
        sim = SimulationCase(filenames)
        sim.run_simulation()
    
    # Clean up
    out.close()


def cansen(argv):
    """CanSen - the SENKIN-like wrapper for Cantera written in Python.
    
    Usage:
     -i:
        Specify the simulation input file in SENKIN format. Required.
     -o:
        Specify the text output file. Optional, default: ``output.out``
     -x:
        Specify the binary save output file. Optional, default: 
        ``save.hdf``
     -c:
        Specify the chemistry input file, in either CHEMKIN, Cantera
        CTI or CTML format. Optional, default: ``chem.xml``
     -d:
        Specify the thermodyanmic database. Optional if the 
        thermodyanmic database is specified in the chemistry input 
        file. Otherwise, required.
     --convert:
        Convert the input mechanism to CTI format and quit. If 
        ``--convert`` is specified, the SENKIN input file is optional.
     --multi:
        Run multiple cases from the input file. Optional.
     -h, --help:
        Print this help message and quit.
    """
    # Version number
    __version__ = '1.1.0'
    
    ret = utils.cli_parser(argv)
    if ret == -3:
        print(cansen.__doc__)
        sys.exit(1)
    elif ret == -2:
        print('Error: No command line options were specified.', 
            cansen.__doc__, sep='\n')
        sys.exit(1)
    elif ret == -1:
        print(cansen.__doc__)
        sys.exit(0)
    else:
        filenames = ret[0]
        convert = ret[1]
        multi = ret[2]
        main(filenames, convert, multi, __version__)
    
if __name__ == "__main__":
    cansen(sys.argv[1:])


