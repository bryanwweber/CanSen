# Python 2 compatibility
from __future__ import print_function

# Standard libraries
import sys
import os
import getopt
from itertools import product

# Related modules
try:
    from cantera import ck2cti
except ImportError:
    print('Error: Cantera must be installed.')
    sys.exit(1)
    
# Local imports
from printer import divider

def convert_mech(mech_filename, thermo_filename):
    """Convert a mechanism and return a string with the filename.
    
    Convert a CHEMKIN format mechanism to the Cantera CTI format using
    the Cantera built-in script `ck2cti`. 
    
    :param mech_filename: 
        Filename of the input CHEMKIN format mechanism. The converted 
        CTI file will have the same name, but with `.cti` extension.
    :param thermo_filename:
        Filename of the thermodynamic database. Optional if the 
        thermodynamic database is present in the mechanism input. 
    """
    arg = ['--input='+mech_filename]
    if thermo_filename is not None:
        arg.append('--thermo='+thermo_filename)
    
    # Convert the mechanism
    ck2cti.main(arg)
    mech_filename = mech_filename[:-4]+'.cti'
    print('Mechanism conversion successful, written to {}'.format(mech_filename))
    return mech_filename

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
            print(' '*10,line,end='')
            if (line.startswith('!') or line.startswith('.') or 
                    line.startswith('/')):
                continue
            elif line.upper().startswith('CONV'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 1
                    problem_type = True
            elif line.upper().startswith('CONP'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 2
                    problem_type = True
            elif line.upper().startswith('VPRO'):
                if problem_type and keywords.get('problemType') != 3:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                elif problem_type and keywords.get('problemType') == 3:
                    vproTime.append(float(line.split()[1]))
                    vproVol.append(float(line.split()[2]))
                else:
                    keywords['problemType'] = 3
                    vproTime = [float(line.split()[1])]
                    vproVol = [float(line.split()[2])]
                    problem_type = True
            elif line.upper().startswith('CONT'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 4
                    problem_type = True
            elif line.upper().startswith('COTV'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 5
                    problem_type = True
            elif line.upper().startswith('VTIM'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 6
                    problem_type = True
            elif line.upper().startswith('TTIM'):
                if problem_type:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 7
                    problem_type = True
            elif line.upper().startswith('TPRO'):
                if problem_type and keywords.get('problemType') != 8:
                    print('Error: More than one problem type keyword '
                          'was specified.')
                    sys.exit(1)
                elif problem_type and keywords.get('problemType') == 8:
                    TproTime.append(float(line.split()[1]))
                    TproTemp.append(float(line.split()[2]))
                else:
                    keywords['problemType'] = 8
                    TproTime = [float(line.split()[1])]
                    TproTemp = [float(line.split()[2])]
                    problem_type = True
            elif line.upper().startswith('TEMP'):
                keywords['temperature'] = float(line.split()[1])
            elif line.upper().startswith('REAC'):
                species = line.split()[1]
                molefrac = line.split()[2]
                reactants.append(':'.join([species,molefrac]))
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
            elif line.upper().startswith('VOL'):
                # The default units of volume in SENKIN are cm**3, but
                # the default in Cantera is m**3 so we have to convert.
                keywords['reactorVolume'] = float(line.split()[1])/1.0E6
            elif line.upper().startswith('RTLS'):
                keywords['sensRelTol'] = float(line.split()[1])
            elif line.upper().startswith('ATLS'):
                keywords['sensAbsTol'] = float(line.split()[1])
            elif line.upper().startswith('IGNBREAK'):
                keywords['break_on_ignition'] = True
            elif line.upper()[0:3] in unsupported_keys:
                print('Keyword', line.upper()[0:3], 'is not supported yet',
                      'and has been ignored')
                continue
            elif line.upper().startswith('END'):
                continue
            else:
                print('Keyword not found',line)
                sys.exit(1)
        print('\n', divider, '\n', sep='')
    
    # The endTime, temperature, pressure, and problemType are required
    # input. Exit if any of them are not found.
    if 'endTime' not in keywords:
        print('Error: End time must be specified with keyword TIME')
        sys.exit(1)
        
    if 'temperature' not in keywords:
        print('Error: Temperature must be specified with keyword TEMP')
        sys.exit(1)
        
    if 'pressure' not in keywords:
        print('Error: Pressure must be specified with keyword PRES')
        sys.exit(1)
        
    if 'problemType' not in keywords:
        print('Error: Problem type must be specified with the problem type '
              'keywords')
        sys.exit(1)
    elif keywords.get('problemType') == 3:
        keywords['vproTime'] = vproTime
        keywords['vproVol'] = vproVol
    elif keywords.get('problemType') == 8:
        keywords['TproTime'] = TproTime
        keywords['TproTemp'] = TproTemp
    
    # The reactants can be specified by REAC or EQUI + FUEL + OXID + 
    # CPROD. One or the other of these must be present; if neither or 
    # both are present, exit.
    if (reactants and 
            (oxidizer or fuel or complete_products or additional_species or 
            ('eqRatio' in keywords))):
        print('Error: REAC and EQUI cannot both be specified.')
        sys.exit(1)
    elif ('eqRatio' in keywords and not 
            (oxidizer and fuel and complete_products)):
        print('Error: If EQUI is specified, all of FUEL, OXID and CPROD must '
              'be as well.')
        sys.exit(1)
    elif reactants:
        keywords['reactants'] = reactants
    elif 'eqRatio' in keywords:
        keywords['oxidizer'] = oxidizer
        keywords['fuel'] = fuel
        keywords['completeProducts'] = complete_products
        keywords['additionalSpecies'] = additional_species
    else:
        print('Error: You must specify the reactants with either REAC or EQUI '
            '+ FUEL + OXID + CPROD')
        sys.exit(1)
    
    # Set the default temperature threshold to determine ignition 
    # delay. 
    if 'tempThresh' not in keywords:
        keywords['tempThresh'] = 400
            
    return keywords

def cli_parser(argv):
    """Parse command line interface input.
    
    :param argv:
        List of command line options.
    """
    try:
        opts, args = getopt.getopt(argv, "hi:o:c:d:x:",
                                   ["help","convert"])
        options = {}
        for o,a in opts:
            options[o] = a
        
        if args:
            raise getopt.GetoptError('Unknown command line option' + 
                                     repr(' '.join(args))
                                    )
    except getopt.GetoptError as e:
        print('You did not enter an option properly.')
        print(e)
        return -3
    if not options:
        return -2
    if not options or '-h' in options or '--help' in options:
        return -1
    
    filenames = {}
    if '-i' in options:
        input_filename = options['-i']
        if not os.path.isfile(input_filename):
            print(
                'Error: The specified input file '
                '"{}" does not exist'.format(input_filename)
                )
            sys.exit(1)
        filenames['input_filename'] = input_filename
    elif '-i' not in options and '--convert' not in options:
        print('Error: The input file must be specified')
        sys.exit(1)
    else:
        filenames['input_filename'] = None
        
    if '-o' in options:
        filenames['output_filename'] = options['-o']
    else:
        filenames['output_filename'] = 'output.out'

    if '-c' in options:
        mech_filename = options['-c']
        if not os.path.isfile(mech_filename):
            print(
                'Error: The specified chemistry file '
                '"{}" does not exist'.format(mech_filename)
                )
            sys.exit(1)
        filenames['mech_filename'] = options['-c']
    else:
        filenames['mech_filename'] = 'chem.xml'
    
    if '-x' in options:
        filenames['save_filename'] = options['-x']
    else:
        filenames['save_filename'] = 'save.hdf'
    
    if '-d' in options:
        thermo_filename = options['-d']
        if not os.path.isfile(thermo_filename):
            print(
                'Error: The specified thermodynamic database '
                '"{}" does not exist'.format(thermo_filename)
                )
            sys.exit(1)
        filenames['thermo_filename'] = thermo_filename
    else:
        filenames['thermo_filename'] = None
    
    convert = '--convert' in options
    
    return filenames, convert

def reactor_interpolate(interp_time, state1, state2):
    """Linearly interpolate the reactor states to the given input time.
    
    :param interp_time:
        Time at which the interpolated values should be calculated
    :param state1:
        Array of the state information at the previous time step.
    :param state2:
        Array of the state information at the current time step.
    """
    interp_state = state1 + (state2 - state1)*(interp_time - state1[0])/(state2[0] - state1[0])
    return interp_state
    

def equivalence_ratio(gas, eq_ratio, fuel, oxidizer, complete_products, 
                      additional_species):
    """Calculate the mixture mole fractions from the equivalence ratio.
    
    Given the equivalence ratio, fuel mixture, oxidizer mixture, 
    the products of complete combustion, and any additional species for 
    the mixture, return a string containing the mole fractions of the 
    species, suitable for setting the state of the input ThermoPhase.
    
    :param gas:
        Cantera ThermoPhase object containing the desired species.
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
    reactants = ''
    cprod_elems = {}
    fuel_elems = {}
    oxid_elems = {}
    
    # Check sum of fuel and oxidizer values; normalize if greater than 1
    fuel_sum = sum(fuel.values())
    if fuel_sum > 1.0:
        for sp, x in fuel.items():
            fuel[sp] = x/fuel_sum
    
    oxid_sum = sum(oxidizer.values())
    if oxid_sum > 1.0:
        for sp, x in oxidizer.items():
            oxidizer[sp] = x/oxid_sum
    
    # Check oxidation state of complete products
    for sp, el in product(complete_products, gas.element_names):
        if el.upper() not in cprod_elems:
            cprod_elems[el.upper()] = {}
        
        cprod_elems[el.upper()][sp] = int(gas.n_atoms(sp, el))
    
    num_C_cprod = sum(cprod_elems.get('C', {0:0}).values())
    num_H_cprod = sum(cprod_elems.get('H', {0:0}).values())
    num_O_cprod = sum(cprod_elems.get('O', {0:0}).values())
    
    oxid_state = 4*num_C_cprod + num_H_cprod - 2*num_O_cprod
    if oxid_state != 0:
        print("Warning: One or more products of incomplete combustion "
              "were specified.")
    
    # Find the number of H, C, and O atoms in the fuel molecules.
    for sp, el in product(fuel.keys(), gas.element_names):
        if el not in fuel_elems:
            fuel_elems[el.upper()] = 0
            
        fuel_elems[el.upper()] += gas.n_atoms(sp, el) * fuel[sp]
    
    num_C_fuel = fuel_elems.get('C', 0)
    num_H_fuel = fuel_elems.get('H', 0)
    num_O_fuel = fuel_elems.get('O', 0)
    
    # Find the number of H, C, and O atoms in the oxidizer molecules.
    for sp, el in product(oxidizer.keys(), gas.element_names):
        if el not in oxid_elems:
            oxid_elems[el.upper()] = 0
            
        oxid_elems[el.upper()] += gas.n_atoms(sp, el) * oxidizer[sp]
    
    num_O_oxid = oxid_elems.get('O', 0)
    
    # Check that all of the elements specified in the fuel and oxidizer 
    # are present in the complete products and vice versa.
    for el in cprod_elems.keys():
        if ((sum(cprod_elems[el].values()) > 0 and fuel_elems[el] == 0 and 
            oxid_elems[el] == 0) or (sum(cprod_elems[el].values()) == 0 and 
           (fuel_elems[el] > 0 or oxid_elems[el] > 0))):
            print('Error: Must specify all elements in the fuel + oxidizer '
                  'in the complete products')
            sys.exit(1)
    
    # Compute the amount of oxidizer required to consume all the 
    # carbon and hydrogen in the complete products
    if num_C_cprod > 0:
        spec = cprod_elems['C'].keys()
        ox = sum([cprod_elems['O'][sp] for sp in spec if cprod_elems['C'][sp] > 0])
        C_multiplier = ox/num_C_cprod
    else:
        C_multiplier = 0
    
    if num_H_cprod > 0:
        spec = cprod_elems['H'].keys()
        ox = sum([cprod_elems['O'][sp] for sp in spec if cprod_elems['H'][sp] > 0])
        H_multiplier = ox/num_H_cprod
    else:
        H_multiplier = 0
    
    # Compute how many O atoms are required to oxidize everybody
    num_O_req = num_C_fuel * C_multiplier + num_H_fuel * H_multiplier - num_O_fuel
    O_mult = num_O_req/num_O_oxid
    
    # Find the total number of moles in the fuel + oxidizer mixture
    total_oxid_moles = sum([O_mult * amt for amt in oxidizer.values()])
    total_fuel_moles = sum([eq_ratio * amt for amt in fuel.values()])
    total_reactant_moles = total_oxid_moles + total_fuel_moles
    
    # Handle the case where additional species are specified separately 
    if additional_species:
        total_additional_species = sum(additional_species.values())
        if total_additional_species >= 1.0:
            print('Error: Additional species must sum to less than 1')
        remain = 1.0 - total_additional_species
        for species, molefrac in additional_species.items():
            add_spec = ':'.join([species,str(molefrac)])
            reactants = ','.join([reactants,add_spec])
    else:
        remain = 1.0
    
    # Compute the mole fractions of the fuel and oxidizer components 
    # given that a certain portion of the mixture will have been taken 
    # up by the additional species, if any.
    for species, ox_amt in oxidizer.items():
        molefrac = ox_amt * O_mult/total_reactant_moles * remain
        add_spec = ':'.join([species,str(molefrac)])
        reactants = ','.join([reactants,add_spec])
    
    for species, fuel_amt in fuel.items():
        molefrac = fuel_amt * eq_ratio /total_reactant_moles * remain
        add_spec = ':'.join([species,str(molefrac)])
        reactants = ','.join([reactants,add_spec])
        
    #Take off the first character, which is a comma
    reactants = reactants[1:]
        
    return reactants