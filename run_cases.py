import sys
try:
    import cantera as ct
except ImportError:
    print("Cantera must be installed")
    sys.exit(1)
    
try:    
    import numpy as np
except ImportError:
    print('Numpy must be installed')
    sys.exit(1)

try:
    import tables
except ImportError:
    print('PyTables must be installed')
    sys.exit(1)

import printer
import utils

def run_case(mechFilename,saveFilename,keywords):
    gas = ct.Solution(mechFilename)

    initialTemp = keywords['temperature']
    initialPres = keywords['pressure']*ct.one_atm
    if 'eqRatio' in keywords:
        reactants, = utils.equivalence_ratio(gas,keywords['eqRatio'],keywords['fuel'],
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

    netw = ct.ReactorNet([reac])
            
    if keywords.get('sensitivity') is not None:
        sensitivity = True
        n_vars = reac.kinetics.n_species + 3
        for i in range(reac.kinetics.n_reactions):
            reac.add_sensitivity_reaction(i)
    else:
        sensitivity = False
    
    print(printer.divider)
    print('Kinetic Mechanism Details:\n')
    print('Total Gas Phase Species     = {0}\n\
Total Gas Phase Reactions   = {1}'.format(reac.kinetics.n_species,reac.kinetics.n_reactions))
    if sensitivity:
        print('Total Sensitivity Reactions = {}'.format(netw.n_sensitivity_params))
    print(printer.divider,'\n')
    
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
        
    #tableDef = {'time':tables.Float64Col(),
    #            'temperature':tables.Float64Col(),
    #            'pressure':tables.Float64Col(),
    #            'massfractions':tables.Float64Col(shape=(reac.thermo.n_species)),
    #           }
    
    try:
    #with tables.open_file(saveFilename, mode = 'w', title = 'CanSen Save File') as saveFile:
        #table = saveFile.create_table(saveFile.root, 'reactor', tableDef, 'Reactor State')
        #
        #timestep = table.row
        #timestep['time'] = netw.time
        #timestep['temperature'],timestep['pressure'],timestep['massfractions'] = reac.thermo.TPY
        #timestep.append()
        #table.flush()
        
        printer.reactor_state_printer(netw.time,(reac.thermo.TPX,reac.thermo.species_names))

        outArray = np.array([[netw.time,reac.T,reac.thermo.P]])
        outArray = np.hstack((outArray,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
        if sensitivity:
            outArray = np.hstack((outArray,np.zeros((1,n_vars*netw.n_sensitivity_params))))
            
        while netw.time < tend:
            netw.step(tend)
            
            if saveTimeStep is not None:
                if netw.time >= saveTime:
                    temp = np.array([[netw.time,reac.T,reac.thermo.P]])
                    temp = np.hstack((temp,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
                    if sensitivity:
                        temp = np.hstack((temp,netw.sensitivities().reshape(1,netw.n_vars*netw.n_sensitivity_params)))
                    outArray = np.vstack((outArray,temp))
                    saveTime += saveTimeStep
            else:
                temp = np.array([[netw.time,reac.T,reac.thermo.P]])
                temp = np.hstack((temp,reac.thermo.Y.reshape(1,reac.thermo.n_species)))
                if sensitivity:
                    temp = np.hstack((temp,netw.sensitivities().reshape(1,netw.n_vars*netw.n_sensitivity_params)))
                    
                outArray = np.vstack((outArray,temp))
                #timestep['time'] = netw.time
                #timestep['temperature'],timestep['pressure'],timestep['massfractions'] = reac.thermo.TPY
                #timestep.append()
                #table.flush()
                
            if netw.time > printTime:
                interpState = utils.reactor_interpolate(printTime,outArray[-1,:reac.kinetics.n_species+3],outArray[-2,:reac.kinetics.n_species+3])
                printer.reactor_state_printer(printTime,((interpState[1],interpState[2],interpState[3:reac.kinetics.n_species+3]),reac.thermo.species_names))
                printTime += printTimeStep
            elif netw.time == printTime:
                printer.reactor_state_printer(netw.time,(reac.thermo.TPX,reac.thermo.species_names))
                printTime += printTimeStep
                
            if reac.T >= tempLimit:
                print('Ignition found by exceeding temperature limit:\n\
Temperature limit = {0:.4f}\n\
Temperature       = {1:.4f}'.format(tempLimit,reac.T))
                printer.reactor_state_printer(netw.time,(reac.thermo.TPX,reac.thermo.species_names),end=True)
                break
    finally:
        with tables.open_file(saveFilename, mode = 'w', title = 'CanSen Save File') as saveFile:
            saveFile.create_array(saveFile.root,'reactor',outArray,'Reactor State')