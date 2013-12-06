import sys

def read_input_file(inputFilename):
    from printer import divider
    keywords = {}
    reactants = []
    oxidizer = {}
    fuel = {}
    completeProducts = []
    additionalSpecies = {}
    with open(inputFilename) as inputFile:
        print(divider)
        print('Keyword Input:\n')
        for line in inputFile:
            print(' '*10,line,end='')
            if line.startswith('!') or line.startswith('.') or line.startswith('/'):
                pass
            elif line.upper().startswith('CONV'):
                keywords['problemType'] = 1
            elif line.upper().startswith('CONP'):
                keywords['problemType'] = 2
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
                completeProducts.append(species)
            elif line.upper().startswith('ADD'):
                species = line.split()[1]
                molefrac = float(line.split()[2])
                additionalSpecies[species] = molefrac
            elif line.upper().startswith('SENS'):
                keywords['sensitivity'] = True
            elif line.upper() == 'END':
                print('\n')
                break
            else:
                print('Keyword not found',line)
                sys.exit(1)
        print(divider,'\n')
        
    if 'endTime' not in keywords:
        print('Error: End time must be specified with keyword TEND')
        sys.exit(1)
        
    if 'temperature' not in keywords:
        print('Error: Temperature must be specified with keyword TEMP')
        sys.exit(1)
        
    if 'pressure' not in keywords:
        print('Error: Pressure must be specified with keyword PRES')
        sys.exit(1)
        
    if 'problemType' not in keywords:
        print('Error: Problem type must be specified with the problem type keyword')
        sys.exit(1)
    
    if reactants and (oxidizer or fuel or completeProducts or additionalSpecies or ('eqRatio' in keywords)):
        print('Error: REAC and EQUI cannot both be specified.')
        sys.exit(1)
    elif 'eqRatio' in keywords and not (oxidizer and fuel and completeProducts):
        print('Error: If EQUI is specified, all of FUEL, OXID and CPROD must be as well')
        sys.exit(1)
    elif reactants:
        keywords['reactants'] = reactants
    elif 'eqRatio' in keywords:
        keywords['oxidizer'] = oxidizer
        keywords['fuel'] = fuel
        keywords['completeProducts'] = completeProducts
        keywords['additionalSpecies'] = additionalSpecies
    else:
        print('Error: You must specify the reactants with either REAC or EQUI')
        sys.exit(1)
    
    if 'tempThresh' not in keywords:
        keywords['tempThresh'] = 400
            
    return keywords,

def cli_parser(argv):
    import getopt
    help = "Haven't written the help yet, sorry!"
    try:
        opts, args = getopt.getopt(argv, "hi:o:c:d:x:",
                                   ["help","convert"])
        options = {}
        for o,a in opts:
            options[o] = a
        
        if args:
            raise getopt.GetOptError('Unknown command line option' + 
                                     repr(' '.join(args))
                                    )
    except getopt.GetOptError as e:
        print('You did not enter an option properly.')
        print(e)
        print(help)
        sys.exit(1)
    if '-h' in options or '--help' in options:
        print(help)
        sys.exit(0)
        
    if '-i' in options:
        inputFilename = options['-i']
    else:
        print('Error: The input file must be specified')
        sys.exit(1)
        
    if '-o' in options:
        outputFilename = options['-o']
    else:
        outputFilename = 'output.out'
        
    if '-c' in options:
        mechFilename = options['-c']
    else:
        mechFilename = 'chem.xml'
    
    if '-x' in options:
        saveFilename = options['-x']
    else:
        saveFilename = 'save.hdf'
    
    if '-d' in options:
        thermoFilename = options['-d']
    else:
        thermoFilename = None
     
    convert = '--convert' in options
    
    return inputFilename,outputFilename,mechFilename,saveFilename,thermoFilename,convert,

def reactor_interpolate(interpTime,State2,State1,):
    interpState = State1 + (State2 - State1)*(interpTime - State1[0])/(State2[0] - State1[0])
    return interpState