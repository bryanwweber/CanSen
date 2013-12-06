import cantera as ct
import numpy as np
import sys
import tables
import printer

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
    elif keywords['problemType'] == 2:
        reac = ct.ConstPressureReactor(gas)
    
    print(printer.divider)
    print('Kinetic Mechanism Details:\n')
    print('Total Gas Phase Species   = {0}\n\
Total Gas Phase Reactions = {1}'.format(reac.kinetics.n_species,reac.kinetics.n_reactions))
    print(printer.divider,'\n')
    
    netw = ct.ReactorNet([reac])
    
    if 'abstol' in keywords:
        netw.atol = keywords['abstol']
        
    if 'reltol' in keywords:
        netw.rtol = keywords['reltol']
        
    tend = keywords['endTime']
    
    if 'tempLimit' in keywords:
        tempLimit = keywords['tempLimit']
    else:
        #tempThresh is set in the parser even if it is not present in the input file
        tempLimit = keywords['tempThresh'] + keywords['temperature']
    
    printTimeInt = keywords.get('prntTimeInt')
    saveTimeInt = keywords.get('saveTimeInt')
    maxTimeInt = keywords.get('maxTimeStep')
    
    timeInts = [value for value in [printTimeInt,saveTimeInt,maxTimeInt] if value is not None]
    
    if timeInts:
        netw.set_max_time_step(min(timeInts))
    else:
        netw.set_max_time_step(tend/100)
    
    if printTimeInt is not None:
        printTimeStep = printTimeInt
    else:
        printTimeStep = tend/100
        
    saveTimeStep = saveTimeInt

    printTime = printTimeStep
    
    if saveTimeStep is not None:
        saveTime = saveTimeStep
    
    try:
        printer.reactor_state_printer(netw.time,reac)
        
        outArray = np.array([[netw.time,reac.T,reac.thermo.P]])
        outArray = np.hstack((outArray,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
        
        while netw.time < tend:
            netw.step(tend)
            
            if saveTimeStep is not None:
                if netw.time >= saveTime:
                    temp = np.array([[netw.time,reac.T,reac.thermo.P]])
                    temp = np.hstack((temp,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
                    outArray = np.vstack((outArray,temp))
                    saveTime += saveTimeStep
            else:
                temp = np.array([[netw.time,reac.T,reac.thermo.P]])
                temp = np.hstack((temp,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
                outArray = np.vstack((outArray,temp))
                                
            if netw.time >= printTime:
                printer.reactor_state_printer(netw.time,reac)
                printTime += printTimeStep
                
            if reac.T >= tempLimit:
                printer.reactor_state_printer(netw.time,reac)
                break
    finally:
        with tables.open_file(saveFilename, mode = 'w', title = 'CanSen Save File') as saveFile:
            saveFile.create_array(saveFile.root,'reactor',outArray,'Reactor State')