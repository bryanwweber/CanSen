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
                continue
            elif line.upper().startswith('CONV'):
                if 'problemType' in keywords:
                     print('Error: More than one problem type keyword was specified.')
                     sys.exit(1)
                else:
                    keywords['problemType'] = 1
            elif line.upper().startswith('CONP'):
                if 'problemType' in keywords:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 2
            elif line.upper().startswith('VPRO'):
                if 'problemType' in keywords and keywords.get('problemType') != 3:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                elif 'problemType' in keywords and keywords.get('problemType') == 3:
                    vproTime.append(float(line.split()[1]))
                    vproVol.append(float(line.split()[2]))
                else:
                    keywords['problemType'] = 3
                    vproTime = [float(line.split()[1])]
                    vproVol = [float(line.split()[2])]
            elif line.upper().startswith('CONT'):
                if 'problemType' in keywords:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 4
            elif line.upper().startswith('COTV'):
                if 'problemType' in keywords:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 5
            elif line.upper().startswith('VTIM'):
                if 'problemType' in keywords:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 6
            elif line.upper().startswith('TTIM'):
                if 'problemType' in keywords:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                else:
                    keywords['problemType'] = 7
            elif line.upper().startswith('TPRO'):
                if 'problemType' in keywords and keywords.get('problemType') != 8:
                    print('Error: More than one problem type keyword was specified.')
                    sys.exit(1)
                elif 'problemType' in keywords and keywords.get('problemType') == 8:
                    TproTime.append(float(line.split()[1]))
                    TproTemp.append(float(line.split()[2]))
                else:
                    keywords['problemType'] = 8
                    TproTime = [float(line.split()[1])]
                    TproTemp = [float(line.split()[2])]
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
        print('Error: End time must be specified with keyword TIME')
        sys.exit(1)
        
    if 'temperature' not in keywords:
        print('Error: Temperature must be specified with keyword TEMP')
        sys.exit(1)
        
    if 'pressure' not in keywords:
        print('Error: Pressure must be specified with keyword PRES')
        sys.exit(1)
        
    if 'problemType' not in keywords:
        print('Error: Problem type must be specified with the problem type keywords')
        sys.exit(1)
    elif keywords.get('problemType') == 3:
        keywords['vproTime'] = vproTime
        keywords['vproVol'] = vproVol
    elif keywords.get('problemType') == 8:
        keywords['TproTime'] = TproTime
        keywords['TproTemp'] = TproTemp
    
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
            raise getopt.GetoptError('Unknown command line option' + 
                                     repr(' '.join(args))
                                    )
    except getopt.GetoptError as e:
        print('You did not enter an option properly.')
        print(e)
        print(help)
        sys.exit(1)
    if '-h' in options or '--help' in options:
        print(help)
        sys.exit(0)

    if '-i' in options:
        inputFilename = options['-i']
    elif '-i' not in options and '--convert' not in options:
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
     
    if '--convert' in options:
        return None,outputFilename,mechFilename,saveFilename,thermoFilename,True,
    
    return inputFilename,outputFilename,mechFilename,saveFilename,thermoFilename,False,

def reactor_interpolate(interpTime,State2,State1,):
    interpState = State1 + (State2 - State1)*(interpTime - State1[0])/(State2[0] - State1[0])
    return interpState
    

def equivalence_ratio(gas,eqRatio,fuel,oxidizer,completeProducts,additionalSpecies,):
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
    #fuel_tot = sum(fuel.values())
    for species, fuel_amt in fuel.items():
        num_H_fuel += gas.n_atoms(species,'H')*fuel_amt
        num_C_fuel += gas.n_atoms(species,'C')*fuel_amt
        num_O_fuel += gas.n_atoms(species,'O')*fuel_amt
    
    #oxid_tot = sum(oxidizer.values())
    for species, oxid_amt in oxidizer.items():
        num_H_oxid += gas.n_atoms(species,'H')*oxid_amt
        num_C_oxid += gas.n_atoms(species,'C')*oxid_amt
        num_O_oxid += gas.n_atoms(species,'O')*oxid_amt
        
    num_H_req = num_H_fuel + num_H_oxid
    num_C_req = num_C_fuel + num_C_oxid
    
    for species in completeProducts:
        num_H_cprod += gas.n_atoms(species,'H')
        num_C_cprod += gas.n_atoms(species,'C')
    
    if num_H_cprod > 0:    
        if num_H_req == 0:
            print('Error: All elements specified in the Complete Products must be in the Fuel or Oxidizer')
            sys.exit(1)
            
        H_multiplier = num_H_req/num_H_cprod
    else:
        H_multiplier = 0
    
    if num_C_cprod > 0:
        if num_C_req == 0:
            print('Error: All elements specified in the Complete Products must be in the Fuel or Oxidizer')
            sys.exit(1)
            
        C_multiplier = num_C_req/num_C_cprod
    else:
        C_multiplier = 0
    
    for species in completeProducts:
        num_C = gas.n_atoms(species,'C')
        num_H = gas.n_atoms(species,'H')
        num_O = gas.n_atoms(species,'O')
        if num_C > 0:
            num_O_cprod += num_O * C_multiplier
        elif num_H > 0:
            num_O_cprod += num_O * H_multiplier
    
    O_mult = (num_O_cprod - num_O_fuel)/num_O_oxid
    
    totalOxidMoles = sum([O_mult * amt for amt in oxidizer.values()])
    totalFuelMoles = sum([eqRatio * amt for amt in fuel.values()])
    totalReactantMoles = totalOxidMoles + totalFuelMoles
    
    if additionalSpecies:
        totalAdditionalSpecies = sum(additionalSpecies.values())
        if totalAdditionalSpecies >= 1:
            print('Error: Additional species must sum to less than 1')
        remain = 1 - totalAdditionalSpecies
        for species, molefrac in additionalSpecies.items():
            qwer = ':'.join([species,str(molefrac)])
            reactants = ','.join([reactants,qwer])
    else:
        remain = 1
    for species,ox_amt in oxidizer.items():
        molefrac = ox_amt * O_mult/totalReactantMoles * remain
        qwer = ':'.join([species,str(molefrac)])
        reactants = ','.join([reactants,qwer])
    
    for species, fuel_amt in fuel.items():
        molefrac = fuel_amt * eqRatio /totalReactantMoles * remain
        qwer = ':'.join([species,str(molefrac)])
        reactants = ','.join([reactants,qwer])
        
    #Take off the first character, which is a comma
    reactants = reactants[1:]
        
    return reactants,