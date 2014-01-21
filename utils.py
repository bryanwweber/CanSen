import sys
import os
import getopt

try:
    from cantera import ck2cti
except ImportError:
    print('Error: Cantera must be installed.')
    sys.exit(1)
    
from printer import divider

def convert_mech(mech_filename, thermo_filename, convert):
    """Convert a mechanism and return a string with the filename.
    
    Convert a CHEMKIN format mechanism to the Cantera CTI format using
    the Cantera built-in script `ck2cti`. 
    
    :param mech_filename: 
        Filename of the input CHEMKIN format mechanism. The converted 
        CTI file will have the same name, but with `.cti` extension.
    :param thermo_filename:
        Filename of the thermodynamic database. Optional if the 
        thermodynamic database is present in the mechanism input. 
    :param convert:
        Boolean indicating that the user wishes only to convert the 
        input mechanism and quit.
    """
    arg = ['--input='+mech_filename]
    if thermo_filename is not None:
        arg.append('--thermo='+thermo_filename)
    
    # Convert the mechanism
    ck2cti.main(arg)
    if convert:
        print('Mechanism conversion successful. Exiting.')
        sys.exit(0)
    else:
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
            elif line.upper()[0:3] in unsupported_keys:
                print('Keyword', line.upper()[0:3], 'is not supported yet',
                      'and has been ignored')
                continue
            elif line.upper() == 'END':
                print('\n')
                break
            else:
                print('Keyword not found',line)
                sys.exit(1)
        print(divider,'\n')
    
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
    num_H_fuel = 0
    num_C_fuel = 0
    num_O_fuel = 0
    num_H_oxid = 0
    num_C_oxid = 0
    num_O_oxid = 0
    num_H_cprod = 0
    num_C_cprod = 0
    num_O_cprod = 0
    reactants = ''
    
    # Find the number of H, C, and O atoms in the fuel molecules.
    for species, fuel_amt in fuel.items():
        num_H_fuel += gas.n_atoms(species,'H')*fuel_amt
        num_C_fuel += gas.n_atoms(species,'C')*fuel_amt
        num_O_fuel += gas.n_atoms(species,'O')*fuel_amt
    
    # Find the number of H, C, and O atoms in the oxidizer molecules.
    for species, oxid_amt in oxidizer.items():
        num_H_oxid += gas.n_atoms(species,'H')*oxid_amt
        num_C_oxid += gas.n_atoms(species,'C')*oxid_amt
        num_O_oxid += gas.n_atoms(species,'O')*oxid_amt
        
    num_H_req = num_H_fuel + num_H_oxid
    num_C_req = num_C_fuel + num_C_oxid
    
    for species in complete_products:
        num_H_cprod += gas.n_atoms(species,'H')
        num_C_cprod += gas.n_atoms(species,'C')
    
    if ((num_H_cprod > 0 and num_H_req == 0) or 
            (num_H_cprod == 0 and num_H_req > 0)):
        if num_H_req == 0:
            print('Error: All elements specified in the Complete Products '
                  'must be in the Fuel or Oxidizer')
            sys.exit(1)
            
        H_multiplier = num_H_req/num_H_cprod
    else:
        H_multiplier = 0
    
    if num_C_cprod > 0:
        if num_C_req == 0:
            print('Error: All elements specified in the Complete Products '
                  'must be in the Fuel or Oxidizer')
            sys.exit(1)
            
        C_multiplier = num_C_req/num_C_cprod
    else:
        C_multiplier = 0
    
    for species in complete_products:
        num_C = gas.n_atoms(species,'C')
        num_H = gas.n_atoms(species,'H')
        num_O = gas.n_atoms(species,'O')
        if num_C > 0:
            num_O_cprod += num_O * C_multiplier
        elif num_H > 0:
            num_O_cprod += num_O * H_multiplier
    
    O_mult = (num_O_cprod - num_O_fuel)/num_O_oxid
    
    total_oxid_moles = sum([O_mult * amt for amt in oxidizer.values()])
    total_fuel_moles = sum([eq_ratio * amt for amt in fuel.values()])
    total_reactant_moles = total_oxid_moles + total_fuel_moles
    
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
        
    for species,ox_amt in oxidizer.items():
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