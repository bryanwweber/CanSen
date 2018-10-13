# Standard libraries
import os
from multiprocessing import Pool, set_start_method
from typing import Optional, Union, Tuple, List
from itertools import groupby

# Local imports
from .utils import convert_mech
from .printer import Tee
from .run_cases import SimulationCase, MultiSimulationCase
from ._version import __version__
from .utils import output_filename as ofarg, save_filename as sfarg, mech_filename as mfarg


def worker(sim_index_tup: Tuple[MultiSimulationCase, int]) -> List[float]:
    """Worker for multiprocessing of cases.

    :param sim_index_tup:
        Tuple containing the `MultiSimulationCase` object to be run and
        the index of current case for status messages.
    :return res:
        List of simulation results.
    """
    sim, index = sim_index_tup
    sim.run_simulation()

    res = [sim.ignition_time,
           sim.keywords['pressure'],
           sim.keywords['temperature']]

    if sim.keywords.get('eqRatio') is not None:
        res.append(sim.keywords['eqRatio'])

    print('Done with ' + str(index))

    return res


def main(input_filename: str,
         mech_filename: str = mfarg.default,
         output_filename: str = ofarg.default,
         save_filename: str = sfarg.default,
         thermo_filename: Optional[str] = None,
         multi: Union[bool, int] = False) -> None:
    """Read command line arguments and run the simulation.

    :param args:
        List of arguments to the function
    """
    if not os.path.isfile(input_filename):
        raise FileNotFoundError('The specified input file "{}"'
                                ' does not exist'.format(input_filename))

    if thermo_filename is not None and not os.path.isfile(thermo_filename):
        raise FileNotFoundError('The specified thermodynamic database "{}"'
                                ' does not exist'.format(thermo_filename))

    if not os.path.isfile(mech_filename):
        raise FileNotFoundError('The specified chemistry file "{}"'
                                ' does not exist'.format(mech_filename))
    # Convert the mechanism if it is in CHEMKIN format
    if mech_filename.endswith('.inp'):
        mech_filename = convert_mech(mech_filename, thermo_filename)

    if multi:
        out = open(output_filename, 'w')
    else:
        out = Tee(output_filename, 'w')

    if not multi:
        # Print version information to screen at the start of the problem
        print("This is CanSen, the SENKIN-like wrapper for Cantera, "
              "written in Python.\nVersion: {!s}\n".format(__version__))

    with open(input_filename, 'r') as input_file:
        input_contents = input_file.readlines()

    # Run the simulation
    if multi:
        jobs = []

        # prepare all cases
        for i, (k, g) in enumerate(groupby(input_contents, lambda x: x.strip().upper() == 'END')):
            if not k:
                sim = MultiSimulationCase(list(g), mech_filename, save_filename)

                jobs.append((sim, i))

        # Create a pool based on the number of processors
        set_start_method('spawn')
        with Pool(processes=multi) as pool:
            results = pool.map(worker, jobs)

        # ensure all finished
        pool.join()

        # write output
        print('# Ignition delay [s], Pressure [atm], Temperature [K], '
              'Equivalence ratio', file=out)

        for res in results:
            if len(res) == 3:
                line = '{:.8e} {:.2f} {:.1f}'.format(*res)
            elif len(res) == 4:
                line = '{:.8e} {:.2f} {:.1f} {:.2f}'.format(*res)
            print(line, file=out)

    else:
        sim = SimulationCase(input_contents, mech_filename, save_filename)
        sim.run_simulation()

    # Clean up
    out.close()
