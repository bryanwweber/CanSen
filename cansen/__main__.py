import sys
import os
from argparse import ArgumentParser
from multiprocessing import cpu_count

from .utils import convert_mech
from ._version import __version__


parser = ArgumentParser(
    prog='cansen',
    description='CanSen - the SENKIN-like wrapper for Cantera written in Python.'
)

parser.add_argument('-V', '--version',
                    action='store_true',
                    help='Show the version of CanSen and quit')

parser.add_argument('-i', '--input',
                    type=str,
                    help='The simulation input file in SENKIN format.')

output_filename = parser.add_argument('-o', '--output',
                                      type=str,
                                      default='output.out',
                                      help='The text output file.')

save_filename = parser.add_argument('-x', '--save',
                                    type=str,
                                    default='save.hdf',
                                    help='The binary save output file.')

mech_filename = parser.add_argument('-c', '--chem',
                                    type=str,
                                    default='chem.xml',
                                    help='The chemistry input file, in either CHEMKIN,'
                                         ' Cantera CTI or CTML format.')

parser.add_argument('-d', '--thermo',
                    type=str,
                    help='The thermodynamic database. Optional if the'
                         ' thermodynamic database is specified in the'
                         ' chemistry input file. Otherwise, required.')

parser.add_argument('--convert',
                    action='store_true',
                    help='Convert the input mechanism to CTI format '
                         'and quit. If ``--convert`` is specified, '
                         'the SENKIN input file is optional.')

parser.add_argument('-m', '--multi',
                    type=int,
                    nargs='?',
                    const=cpu_count(),
                    default=False,
                    help='Run multiple cases from the input file. '
                         'Optional. If ``-m`` is used, must specify '
                         'number of processors to be used (e.g., '
                         '``-m 4``). If ``--multi`` is specified, '
                         'CanSen uses the available number of '
                         'processors by default.')


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv)

    if args.version:
        print('CanSen {version} from {path} ()'.format(
            version=__version__,
            path=os.path.abspath(os.path.dirname(__file__))))
        sys.exit(0)

    if args.convert:
        if not os.path.isfile(args.chem):
            raise FileNotFoundError('The chemistry file "{}" could not be found'.format(args.chem))
        if args.thermo is not None and not os.path.isfile(args.thermo):
            raise FileNotFoundError('The thermodynamic database "{}" '
                                    'could not be found'.format(args.thermo))

        convert_mech(args.chem, args.thermo)
        sys.exit(0)

    return args


if __name__ == '__main__':

    # This import has to be here to avoid a circular import from the cansen module
    from .cansen import main as c_main
    args = main()
    sys.exit(c_main(input_filename=args.input, multi=args.multi,
                    mech_filename=args.chem, output_filename=args.output,
                    save_filename=args.save, thermo_filename=args.thermo,
                    ))
