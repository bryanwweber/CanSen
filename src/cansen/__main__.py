"""Process command line arguments and pass control to run the simulation."""
import sys
import os
from typing import List, Optional, TYPE_CHECKING

from .utils import convert_mech, parser
from ._version import __version__
from .cansen import main as c_main

if TYPE_CHECKING:
    import argparse  # noqa: F401 # typing import only


def main(argv: Optional[List[str]] = None) -> 'argparse.Namespace':
    """Process command line arguments and return the Namespace.

    Process arguments from the command line, printing the version
    and exiting if requested, or doing a mechanism conversion and
    exiting if requested. Otherwise, return the `argparse.Namespace`.
    """
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv)

    if args.version:
        print(
            "CanSen {version} from {path} ()".format(
                version=__version__, path=os.path.abspath(os.path.dirname(__file__))
            )
        )
        sys.exit(0)

    if args.convert:
        if not os.path.isfile(args.chem):
            raise FileNotFoundError(
                'The chemistry file "{}" could not be found'.format(args.chem)
            )
        if args.thermo is not None and not os.path.isfile(args.thermo):
            raise FileNotFoundError(
                'The thermodynamic database "{}" '
                "could not be found".format(args.thermo)
            )

        convert_mech(args.chem, args.thermo)
        sys.exit(0)

    return args


if __name__ == "__main__":

    args = main()
    c_main(
        input_filename=args.input,
        multi=args.multi,
        mech_filename=args.chem,
        output_filename=args.output,
        save_filename=args.save,
        thermo_filename=args.thermo,
    )
