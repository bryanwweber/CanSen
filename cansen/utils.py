# Standard libraries
import os
from math import pi
from tempfile import NamedTemporaryFile
from warnings import warn
from argparse import ArgumentParser
from multiprocessing import cpu_count
from typing import Optional

# Third-party modules
from cantera import ck2cti

# Local imports
from .printer import divider
from .exceptions import (KeywordError,
                         MultipleProblemError,
                         UnsupportedKeyword,
                         UndefinedKeywordError,
                         MissingReqdKeywordError,
                         MissingKeyword,
                         CanSenError,
                         )

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


def convert_mech(mech_filename: str, thermo_filename: Optional[str] = None) -> str:
    """Convert a mechanism and return a string with the filename.

    Convert a CHEMKIN format mechanism to the Cantera CTI format using
    the Cantera built-in script ``ck2cti``.

    :param mech_filename:
        Filename of the input CHEMKIN format mechanism. The converted
        CTI file will have the same name, but with ``.cti`` extension.
    :param thermo_filename:
        Filename of the thermodynamic database. Optional if the
        thermodynamic database is present in the mechanism input.
    """
    arg = ['--input=' + mech_filename]
    if thermo_filename is not None:
        arg.append('--thermo=' + thermo_filename)

    # Convert the mechanism
    ck2cti.main(arg)
    mech_filename = mech_filename[:-4] + '.cti'
    print('Mechanism conversion successful, written to '
          '{}'.format(mech_filename))
    return mech_filename


def process_multi_input(input_filename):
    """Process a formatted input file into multiple cases.

    Processes a formatted input file that contains multiple cases into
    separate temporary files, for individual reading of keywords.

    :param input_filename:
        Filename of the SENKIN input file.
    :return filenames:
        List of temporary filenames.
    """
    filenames = []

    temp_file = NamedTemporaryFile(delete=False)

    with open(input_filename) as input_file:
        for line in input_file:

            if (line.startswith('!') or line.startswith('.') or
                    line.startswith('/') or line.strip() == ''):
                # skip comment or blank lines
                continue
            elif line.upper().startswith('END'):
                temp_file.write(line)

                # store temporary file and create new
                temp_file.seek(0)
                filenames.append(temp_file.name)

                temp_file = NamedTemporaryFile(delete=False)

                continue
            else:
                # just print line
                temp_file.write(line)

    # check if last file actually written to; if not, close
    if os.stat(temp_file.name).st_size == 0:
        temp_file.close()

    return filenames


def read_input_file(input_filename):
    """Read a formatted input file and return a dictionary of keywords.

    :param input_filename:
        Filename of the SENKIN input file.
    """
    # Initialize the dictionaries and lists that will be filled by
    # the parsing.
    keywords = {}
    reactants = []
    oxidizer = {}
    fuel = {}
    complete_products = []
    additional_species = {}

    # problem_type is a boolean indicating whether a problem selection
    # has been made.
    problem_type = False

    # unsupported_keys is a list of keywords that are not supported
    # yet.
    unsupported_keys = [
        'ADAP',   'AEXT',   'AFRA', 'AGGA',  'AGGB',  'AGGD',  'AGGE',
        'AGGFD',  'AGGMN',  'AINT', 'AREA',  'AREAQ', 'AROP',  'ASEN',
        'ASTEPS', 'AVALUE', 'AVAR', 'BETA',  'BLKEQ', 'BULK',  'CLSC',
        'CNTN',   'CNTT',   'COLR', 'DIST',  'ENRG',  'EPSG',  'EPSR', 'CLSM',
        'EPSS',   'EPST',   'ETCH', 'GFAC',  'GMHTC', 'HTC',   'HTRN', 'IPSR',
        'IRET',   'ISTP',   'KLIM', 'MAXIT', 'MCUT',  'MMASS', 'NADAP',
        'NEWRUN', 'NMOM',   'NNEG', 'NOCG',  'NSOL',  'PNDE',  'PPRO', 'PRNT',
        'PROE',   'PVFE',   'QFUN', 'QLOS',  'QPRO',  'QRGEQ', 'QRSEQ',
        'RELAXC', 'ROP',    'RSTR', 'SCLM',  'SCLS',  'SCOR',  'SENG', 'SENT',
        'SFAC',   'SIZE',   'SOLUTION_TECHNIQUE',     'SSTT',  'SURF', 'TAMB',
        'TGIV',   'TIFP',   'TRAN', 'TRES',  'TRST',  'TSRF',  'TSTR', 'UIGN',
        'USET',   'WENG',   'XMLI'
        ]

    with open(input_filename) as input_file:
        print(divider)
        print('Keyword Input:\n')
        for line in input_file:
            # Echo the input back to the output file.
            print(' '*10, line, end='')
            if (line.startswith('!') or line.startswith('.') or
                    line.startswith('/') or line.strip() == ""):
                continue
            elif line.upper().startswith('CONV'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 1
                    problem_type = True
            elif line.upper().startswith('CONP'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 2
                    problem_type = True
            elif line.upper().startswith('VPRO'):
                if not problem_type:
                    keywords['problemType'] = 3
                    vproTime = [float(line.split()[1])]
                    vproVol = [float(line.split()[2])]
                    problem_type = True
                elif problem_type and keywords.get('problemType') != 3:
                    raise MultipleProblemError(line, keywords['problemType'])
                elif problem_type and keywords.get('problemType') == 3:
                    vproTime.append(float(line.split()[1]))
                    vproVol.append(float(line.split()[2]))
            elif line.upper().startswith('CONT'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 4
                    problem_type = True
            elif line.upper().startswith('COTV'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 5
                    problem_type = True
            elif line.upper().startswith('VTIM'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 6
                    problem_type = True
            elif line.upper().startswith('TTIM'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 7
                    problem_type = True
            elif line.upper().startswith('TPRO'):
                if not problem_type:
                    keywords['problemType'] = 8
                    TproTime = [float(line.split()[1])]
                    TproTemp = [float(line.split()[2])]
                    problem_type = True
                elif problem_type and keywords.get('problemType') != 8:
                    raise MultipleProblemError(line, keywords['problemType'])
                elif problem_type and keywords.get('problemType') == 8:
                    TproTime.append(float(line.split()[1]))
                    TproTemp.append(float(line.split()[2]))
            elif line.upper().startswith('ICEN'):
                if problem_type:
                    raise MultipleProblemError(line, keywords['problemType'])
                else:
                    keywords['problemType'] = 9
                    problem_type = True
            elif line.upper().startswith('TEMP'):
                keywords['temperature'] = float(line.split()[1])
            elif line.upper().startswith('REAC'):
                species = line.split()[1]
                molefrac = line.split()[2]
                reactants.append(':'.join([species, molefrac]))
            elif line.upper().startswith('PRES'):
                keywords['pressure'] = float(line.split()[1])
            elif line.upper().startswith('TIME'):
                keywords['endTime'] = float(line.split()[1])
            elif line.upper().startswith('TLIM'):
                keywords['tempLimit'] = float(line.split()[1])
            elif line.upper().startswith('DTIGN'):
                keywords['tempThresh'] = float(line.split()[1])
            elif line.upper().startswith('ATOL'):
                keywords['abstol'] = float(line.split()[1])
            elif line.upper().startswith('RTOL'):
                keywords['reltol'] = float(line.split()[1])
            elif line.upper().startswith('DELT'):
                keywords['prntTimeInt'] = float(line.split()[1])
            elif line.upper().startswith('DTSV'):
                keywords['saveTimeInt'] = float(line.split()[1])
            elif line.upper().startswith('STPT'):
                keywords['maxTimeStep'] = float(line.split()[1])
            elif line.upper().startswith('EQUI'):
                keywords['eqRatio'] = float(line.split()[1])
            elif line.upper().startswith('OXID'):
                species = line.split()[1]
                molefrac = float(line.split()[2])
                oxidizer[species] = molefrac
            elif line.upper().startswith('FUEL'):
                species = line.split()[1]
                molefrac = float(line.split()[2])
                fuel[species] = molefrac
            elif line.upper().startswith('CPROD'):
                species = line.split()[1]
                complete_products.append(species)
            elif line.upper().startswith('ADD'):
                species = line.split()[1]
                molefrac = float(line.split()[2])
                additional_species[species] = molefrac
            elif line.upper().startswith('SENS'):
                keywords['sensitivity'] = True
            elif line.upper().startswith('VOL '):
                # The default units of volume in SENKIN are cm**3, but
                # the default in Cantera is m**3 so we have to convert.
                keywords['reactorVolume'] = float(line.split()[1])/1.0E6
            elif line.upper().startswith('RTLS'):
                keywords['sensRelTol'] = float(line.split()[1])
            elif line.upper().startswith('ATLS'):
                keywords['sensAbsTol'] = float(line.split()[1])
            elif line.upper().startswith('IGNBREAK'):
                keywords['break_on_ignition'] = True
            elif line.upper().startswith('CMPR'):
                keywords['comp_ratio'] = float(line.split()[1])
            elif line.upper().startswith('DEG0'):
                keywords['start_crank_angle'] = float(line.split()[1])
            elif line.upper().startswith('VOLD'):
                keywords['swept_volume'] = float(line.split()[1])/1.0E6
            elif line.upper().startswith('VOLC'):
                keywords['clear_volume'] = float(line.split()[1])/1.0E6
            elif line.upper().startswith('LOLR'):
                keywords['rod_radius_ratio'] = float(line.split()[1])
            elif line.upper().startswith('RPM'):
                keywords['rev_per_min'] = float(line.split()[1])
            elif line.upper().startswith('BORE'):
                keywords['cyl_bore'] = float(line.split()[1])/1.0E2
            elif line.upper().startswith('STROKE'):
                keywords['stroke_length'] = float(line.split()[1])/1.0E2
            elif line.upper().startswith('RODL'):
                keywords['connect_rod_len'] = float(line.split()[1])/1.0E2
            elif line.upper().startswith('CRAD'):
                keywords['crank_radius'] = float(line.split()[1])/1.0E2
            elif line.upper()[0:3] in unsupported_keys:
                raise UnsupportedKeyword(line)
                continue
            elif line.upper().startswith('END'):
                continue
            else:
                raise UndefinedKeywordError(line)
        print('\n', divider, '\n', sep='')

    # The endTime, temperature, pressure, and problemType are required
    # input. Exit if any of them are not found.
    if 'endTime' not in keywords:
        raise MissingReqdKeywordError('TIME')

    if 'temperature' not in keywords:
        raise MissingReqdKeywordError('TEMP')

    if 'pressure' not in keywords:
        raise MissingReqdKeywordError('PRES')

    if 'problemType' not in keywords:
        raise MissingReqdKeywordError(
            'CONP', 'CONV', 'VPRO',
            'CONT', 'ICEN', 'TPRO',
            'COTV', 'TTIM', 'VTIM',
        )
    elif keywords.get('problemType') == 3:
        keywords['vproTime'] = vproTime
        keywords['vproVol'] = vproVol
    elif keywords.get('problemType') == 8:
        keywords['TproTime'] = TproTime
        keywords['TproTemp'] = TproTemp
    elif keywords.get('problemType') == 9:
        # Variables needed to calculate piston velocity and other
        # quantities for the IC Engine model: Stroke length, rod
        # length to crank radius ratio, rpm, starting angle, initial
        # volume

        if 'rev_per_min' not in keywords:
            raise MissingReqdKeywordError('RPM')

        # Handle the various ways to calculate the stroke length
        if 'stroke_length' in keywords:
            print("Info: 'STROKE' was specified, and will be used for the "
                  "stroke length regardless of other parameters.")
        elif all(key in keywords for key in ('swept_volume', 'cyl_bore')):
            print("Info: Using swept volume and cylinder bore to "
                  "calculate stroke length.")
            keywords['stroke_length'] = (keywords['swept_volume']*4 /
                                         (pi*keywords['cyl_bore']**2))
        elif all(key in keywords for key in ('comp_ratio',
                                             'clear_volume',
                                             'cyl_bore')):
            print("Info: Using compression ratio, clearance volume, and "
                  "cylinder bore to calculate stroke length.")
            keywords['swept_volume'] = (keywords['clear_volume'] *
                                        (keywords['comp_ratio'] - 1))
            keywords['stroke_length'] = (keywords['swept_volume']*4 /
                                         (pi*keywords['cyl_bore']**2))
        elif 'crank_radius' in keywords:
            print("Info: Using crank radius to compute the stroke length.")
            keywords['stroke_length'] = 2*keywords['crank_radius']
        else:
            raise MissingReqdKeywordError(
                'STROKE', 'VOLD', 'BORE',
                'CMPR', 'VOLC', 'CRAD',
            )

        # Handle the various ways to calculate the initial volume
        if 'reactorVolume' in keywords:
            print("Info: The inital reactor volume was specified by the VOL "
                  "keyword and this value will be used regardless of other "
                  "settings.")
        elif all(key in keywords for key in ('swept_volume', 'clear_volume',
                                             'comp_ratio')):
            raise KeywordError("Only two of 'VOLD', 'VOLC', and 'CMPR' may be "
                               "specified.")
        elif all(key in keywords for key in ('swept_volume', 'clear_volume')):
            print("Info: Computing initial reactor volume from the swept "
                  "volume and the clearance volume.")
            keywords['reactorVolume'] = (keywords['swept_volume'] +
                                         keywords['clear_volume'])
        elif all(key in keywords for key in ('comp_ratio', 'clear_volume')):
            print("Info: Computing initial reactor volume from the "
                  "compression ratio and clearance volume.")
            keywords['reactorVolume'] = (keywords['comp_ratio'] *
                                         keywords['clear_volume'])
        elif all(key in keywords for key in ('comp_ratio', 'swept_volume')):
            print("Info: Computing initial reactor volume from the "
                  "compression ratio and swept volume.")
            keywords['reactorVolume'] = (keywords['swept_volume'] *
                                         (1 + 1/(keywords['comp_ratio'] - 1)))
        elif all(key in keywords for key in ('clear_volume', 'cyl_bore')):
            print("Info: Computing initial reactor volume from the cylinder "
                  "bore, stroke length, and clearance volume.")
            keywords['reactorVolume'] = (pi/4*keywords['cyl_bore']**2 *
                                         keywords['stroke_length'] +
                                         keywords['clear_volume'])
        else:
            raise MissingReqdKeywordError('VOLD', 'VOLC', 'CMPR', 'BORE',
                                          'VOL')

        # Handle the ways to calculate the rod length to radius ratio
        if 'rod_radius_ratio' in keywords:
            print("Info: The connecting rod length to crank radius ratio was "
                  "specified by the 'LOLR' keyword and this value will be "
                  "used regardless of other settings.")
        elif all(key in keywords for key in ('connect_rod_len',
                                             'crank_radius')):
            print("Info: Using given connecting rod length and crank radius "
                  "to compute the ratio.")
            keywords['rod_radius_ratio'] = (keywords['connect_rod_len'] /
                                            keywords['crank_radius'])
        else:
            raise MissingReqdKeywordError('LOLR', 'CRAD', 'RODL')

    # Set the default reactor volume, if it is not specified
    if 'reactorVolume' not in keywords:
        keywords['reactorVolume'] = 1.0E-6
        raise MissingKeyword('No reactor volume specified, assuming '
                             '1.0 cm**3.')

    # The reactants can be specified by REAC or EQUI + FUEL + OXID +
    # CPROD. One or the other of these must be present; if neither or
    # both are present, exit.
    if (reactants and
            (oxidizer or fuel or complete_products or additional_species or
             ('eqRatio' in keywords))):
        raise KeywordError('REAC and EQUI cannot both be specified.')
    elif ('eqRatio' in keywords and not
            (oxidizer and fuel and complete_products)):
        raise KeywordError('If EQUI is specified, all of FUEL, OXID and '
                           'CPROD must be as well.')
    elif reactants:
        keywords['reactants'] = reactants
    elif 'eqRatio' in keywords:
        keywords['oxidizer'] = oxidizer
        keywords['fuel'] = fuel
        keywords['completeProducts'] = complete_products
        keywords['additionalSpecies'] = additional_species
    else:
        raise MissingReqdKeywordError('REAC', 'EQUI')

    # Set the default temperature threshold to determine ignition
    # delay.
    if 'tempThresh' not in keywords:
        keywords['tempThresh'] = 400

    return keywords


def equivalence_ratio(gas, eq_ratio, fuel, oxidizer, complete_products,
                      additional_species):
    """Calculate the mixture mole fractions from the equivalence ratio.

    Given the equivalence ratio, fuel mixture, oxidizer mixture,
    the products of complete combustion, and any additional species for
    the mixture, return a string containing the mole fractions of the
    species, suitable for setting the state of the input :py:class:`~cantera.ThermoPhase`.
    Note that we can't use the :py:function:`~cantera.ThermoPhase.set_equivalence_ratio`
    because we need to handle the cases of complete products that aren't CO2 and H2O
    and because we can specify additional species in the mixture.

    :param gas:
        Cantera :py:class:`~cantera.ThermoPhase` object containing the desired species.
    :param eq_ratio:
        Equivalence ratio
    :param fuel:
        Dictionary of molecules in the fuel mixture and the fraction of
        each molecule in the fuel mixture
    :param oxidizer:
        Dictionary of molecules in the oxidizer mixture and the
        fraction of each molecule in the oxidizer mixture.
    :param complete_products:
        List of species in the products of complete combustion.
    :param additional_species:
        Dictionary of molecules that will be added to the mixture.
        The mole fractions given in this dictionary are as a fraction
        of the total mixture.
    """
    cprod_elems = {}
    fuel_elems = {}
    oxid_elems = {}

    fuel_sum = sum(fuel.values())
    fuel = {sp: x/fuel_sum for sp, x in fuel.items()}

    oxid_sum = sum(oxidizer.values())
    oxidizer = {sp: x/oxid_sum for sp, x in oxidizer.items()}

    for el in gas.element_names:
        cprod_tot = sum([int(gas.n_atoms(sp, el)) for sp in complete_products])
        fuel_tot = sum([gas.n_atoms(sp, el) * fuel[sp] for sp in fuel.keys()])
        oxid_tot = sum([gas.n_atoms(sp, el) * oxidizer[sp] for sp in oxidizer.keys()])

        # Check that all of the elements specified in the fuel and oxidizer
        # are present in the complete products and vice versa.
        if ((cprod_tot > 0 and fuel_tot == 0 and oxid_tot == 0) or
           (cprod_tot == 0 and (fuel_tot > 0 or oxid_tot > 0))):
            raise CanSenError('Must specify all elements in the fuel + oxidizer '
                              'in the complete products and vice-versa')

        cprod_elems[el.upper()] = cprod_tot
        fuel_elems[el.upper()] = fuel_tot
        oxid_elems[el.upper()] = oxid_tot

    num_C_cprod = cprod_elems.get('C', 0)
    num_H_cprod = cprod_elems.get('H', 0)
    num_O_cprod = cprod_elems.get('O', 0)

    # Check oxidation state of complete products
    oxid_state = 4*num_C_cprod + num_H_cprod - 2*num_O_cprod
    if oxid_state != 0:
        warn("One or more products of incomplete combustion were specified.")

    num_C_fuel = fuel_elems.get('C', 0)
    num_H_fuel = fuel_elems.get('H', 0)
    num_O_fuel = fuel_elems.get('O', 0)

    num_O_oxid = oxid_elems.get('O', 0)

    # Compute the amount of oxidizer required to consume all the
    # carbon and hydrogen in the complete products
    C_ox = 0
    H_ox = 0
    for species in complete_products:
        if gas.n_atoms(species, 'C') > 0:
            C_ox += int(gas.n_atoms(species, 'O'))
        if gas.n_atoms(species, 'H') > 0:
            H_ox += int(gas.n_atoms(species, 'O'))

    if num_C_cprod > 0:
        C_multiplier = C_ox/num_C_cprod
    else:
        C_multiplier = 0

    if num_H_cprod > 0:
        H_multiplier = H_ox/num_H_cprod
    else:
        H_multiplier = 0

    # Compute how many O atoms are required to oxidize everybody
    num_O_req = (num_C_fuel * C_multiplier +
                 num_H_fuel * H_multiplier - num_O_fuel)
    O_mult = num_O_req/num_O_oxid

    # Find the total number of moles in the fuel + oxidizer mixture
    total_oxid_moles = sum([O_mult * amt for amt in oxidizer.values()])
    total_fuel_moles = sum([eq_ratio * amt for amt in fuel.values()])
    total_reactant_moles = total_oxid_moles + total_fuel_moles

    # Handle the case where additional species are specified separately
    if additional_species:
        total_additional_species = sum(additional_species.values())
        if total_additional_species >= 1.0:
            raise CanSenError('Additional species must sum to less than 1')
        remain = 1.0 - total_additional_species
        reactants = additional_species.copy()
    else:
        remain = 1.0
        reactants = {}

    # Compute the mole fractions of the fuel and oxidizer components
    # given that a certain portion of the mixture will have been taken
    # up by the additional species, if any.
    for species, ox_amt in oxidizer.items():
        molefrac = ox_amt * O_mult/total_reactant_moles * remain
        reactants[species] = molefrac

    for species, fuel_amt in fuel.items():
        molefrac = fuel_amt*eq_ratio/total_reactant_moles * remain
        reactants[species] = molefrac

    return reactants
