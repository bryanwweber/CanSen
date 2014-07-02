#! /usr/bin/env python3

# Python 2 compatibility
from __future__ import print_function
from __future__ import division

# Standard libraries
import sys
from multiprocessing import Process, Pool

#Local imports
import utils
from printer import Tee
from run_cases import SimulationCase, MultiSimulationCase


def worker(sim_index_tup):
    """Worker for multiprocessing of cases.

    :param sim_index_tup:
        Tuple containing the MultiSimulationCase object to be run and
        the index of current case for status messages.
    :return res:
        List of simulation results.
    """

    sim, index = sim_index_tup
    sim.run_simulation()

    # store results
    if sim.keywords.get('eqRatio') is None:
        res = [sim.ignition_time,
               sim.keywords['pressure'],
               sim.keywords['temperature']]
    else:
        # store equivalence ratio if possible
        res = [sim.ignition_time,
               sim.keywords['pressure'],
               sim.keywords['temperature'],
               sim.keywords['eqRatio']]

    print('Done with ' + str(index))

    return res


def main(filenames, convert, multi, num_proc, version):
    """The main driver function of CanSen.

    :param filenames:
        Dictionary of filenames related to the simulation.
    :param convert:
        Boolean indicating that the user wishes only to convert the
        input mechanism and quit.
    :param multi:
        Boolean indicating multiple cases to be run.
    :param num_proc:
        Number of processors to use for multiprocessing.
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
        # Preprocess the input file to separate the various cases.
        input_files = utils.process_multi_input(filenames['input_filename'])

        # Create a pool based on the number of processors
        if num_proc is not None:
            pool = Pool(processes = num_proc)
        else:
            # use available number of processors by default
            pool = Pool()

        jobs = []
        results = []

        # prepare all cases
        for i, temp_file in enumerate(input_files):

            local_names = filenames.copy()
            local_names['input_filename'] = temp_file
            sim = MultiSimulationCase(local_names)

            jobs.append([sim, i])

        jobs = tuple(jobs)
        results = pool.map(worker, jobs)

        # not adding more proceses
        pool.close()

        # ensure all finished
        pool.join()

        # clean up
        utils.remove_files(input_files)

        # write output
        print('# Ignition delay [s], Pressure [atm], Temperature [K], '
              'Equivalence ratio', file = out)

        for res in results:
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
     -m, --multi:
        Run multiple cases from the input file. Optional. If ``-m`` is
        used, must specify number of processors to be used (e.g.,
        ``-m 4``). If ``--multi`` is specified, CanSen uses the available
        number of processors by default.
     -h, --help:
        Print this help message and quit.
    """
    # Version number
    __version__ = '1.1.0'

    ret = utils.cli_parser(argv)

    filenames = ret[0]
    convert = ret[1]
    multi = ret[2]
    num_proc = ret[3]

    main(filenames, convert, multi, num_proc, __version__)


if __name__ == "__main__":
    cansen(sys.argv[1:])

