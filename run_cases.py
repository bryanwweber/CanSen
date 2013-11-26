import cantera as ct
import sys

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

def run_case(mechFilename,saveFilename,keywords):
    gas = ct.Solution(mechFilename)
    initialTemp = keywords['temperature']
    initialPres = keywords['pressure']*ct.one_atm
    if 'eqRatio' in keywords:
        reactants, = equivalence_ratio(gas,keywords['eqRatio'],keywords['fuel'],
                                      keywords['oxidizer'],
                                      keywords['completeProducts'],
                                      keywords['additionalSpecies'],
                                      )
    else:
        reactants = ','.join(keywords['reactants'])
    gas.TPX = initialTemp, initialPres, reactants
    
    if keywords['problemType'] == 1:
        reac = ct.Reactor(gas)
    elif keyworkds['problemType'] == 2:
        reac = ct.ConstPressureReactor(gas)
        
    netw = ct.ReactorNet([reac])
    if 'abstol' in keywords:
        netw.atol = keywords['abstol']
    if 'reltol' in keywords:
        netw.rtol = keywords['reltol']
    tend = keywords['endTime']
    time = 0
    if 'tempLimit' in keywords:
        tempLimit = keywords['tempLimit']
    else:
        tempLimit = keywords['tempThresh'] + keywords['temperature']
    if 'prntTimeInt' in keywords and 'saveTimeInt' in keywords:
        timeStep = min(keywords['prntTimeInt'],keywords['saveTimeInt'])
        timeStepPrint = keywords['prntTimeInt']
        timeStepSave = keywords['saveTimeInt']
    elif 'prntTimeInt' in keywords and 'saveTimeInt' not in keywords:
        timeStep = keywords['prntTimeInt']
        timeStepPrint = keywords['prntTimeInt']
        timeStepSave = 0
    elif 'saveTimeInt' in keywords and 'prntTimeInt' not in keywords:
        timeStep = keywords['saveTimeInt']
        timeStepPrint = tend/100
        timeStepSave = keywords['saveTimeInt']
    else:
        timeStep = tend/100
        timeStepPrint = tend/100
        timeStepSave = tend/100
    
    #while time < tend:
    #    nextTime = time + timeStep
    #    netw.advance(nextTime)
    #    time = netw.time
    #    print(time,reac.T,reac.thermo.P)
    #    if reac.T > tempLimit:
    #        print(time,reac.T,reac.thermo.P)
    #        break
    while time < tend:
        time = netw.step(tend)
        if reac.T > tempLimit:
            print(time,reac.T,reac.thermo.P)
            break