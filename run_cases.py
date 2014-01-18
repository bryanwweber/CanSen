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

class VolumeProfile(object):
    def __init__(self,keywords):
        self.time = np.array(keywords['vproTime'])
        self.volume = np.array(keywords['vproVol'])
        self.velocity = np.diff(self.volume)/np.diff(self.time)
        self.velocity = np.append(self.velocity,0)
    def __call__(self,t):
        if t == 0:
            return 0
        if t < self.time[1]:
            tim0 = self.time[0]
            tim1 = self.time[1]
            vel0 = self.velocity[0]
            vel1 = self.velocity[1]
        elif t >= self.time[1] and t <= self.time[-1]:
            tim0 = self.time[self.time < t][-1]
            tim1 = self.time[np.where(self.time == tim0)[0][0]+1]
            vel0 = self.velocity[self.time < t][-1]
            vel1 = self.velocity[np.where(self.time == tim0)[0][0]+1]
        elif t > self.time[-1]:
            return 0
        
        interp = vel0 + (vel1-vel0)*(t-tim0)/(tim1-tim0)
        return interp
        
class TemperatureProfile(object):
    def __init__(self,keywords):
        self.time = np.array(keywords['TproTime'])
        self.temperature = np.array(keywords['TproTemp'])
    def __call__(self,t):
        if t == 0:
            return self.temperature[0]
        if t < self.time[1]:
            tim0 = self.time[0]
            tim1 = self.time[1]
            temp0 = self.temperature[0]
            temp1 = self.temperature[1]
        elif t >= self.time[1] and t <= self.time[-1]:
            tim0 = self.time[self.time < t][-1]
            tim1 = self.time[np.where(self.time == tim0)[0][0]+1]
            temp0 = self.temperature[self.time < t][-1]
            temp1 = self.temperature[np.where(self.time == tim0)[0][0]+1]
        elif t > self.time[-1]:
            return self.temperature[-1]
        
        interp = temp0 + (temp1-temp0)*(t-tim0)/(tim1-tim0)
        return interp

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
    
    env = ct.Reservoir(ct.Solution('air.xml'))
    
    #Could refactor here to put the problem setup in another function and return the
    #reactor, n_vars, wall, and tempFunc.
    tempFunc = None
    if keywords['problemType'] == 1:
        reac = ct.IdealGasReactor(gas)
        #Number of solution variables is number of species + mass, volume, temperature
        n_vars = reac.kinetics.n_species + 3
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
    elif keywords['problemType'] == 2:
        reac = ct.IdealGasConstPressureReactor(gas)
        #Number of solution variables is number of species + mass, temperature
        n_vars = reac.kinetics.n_species + 2
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
    elif keywords['problemType'] == 3:
        reac = ct.IdealGasReactor(gas)
        #Number of solution variables is number of species + mass, volume, temperature
        n_vars = reac.kinetics.n_species + 3
        wall = ct.Wall(reac,env,A=1.0,velocity=VolumeProfile(keywords))
    elif keywords['problemType'] == 4:
        reac = ct.IdealGasConstPressureReactor(gas,energy='off')
        #Number of solution variables is number of species + mass, temperature
        n_vars = reac.kinetics.n_species + 2
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
    elif keywords['problemType'] == 5:
        reac = ct.IdealGasReactor(gas,energy='off')
        #Number of solution variables is number of species + mass, volume, temperature
        n_vars = reac.kinetics.n_species + 3
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
    elif keywords['problemType'] == 6:
        from user_routines import VolumeFunctionTime
        reac = ct.IdealGasReactor(gas)
        #Number of solution variables is number of species + mass, volume, temperature
        n_vars = reac.kinetics.n_species + 3
        wall = ct.Wall(reac,env,A=1.0,velocity=VolumeFunctionTime())
    elif keywords['problemType'] == 7:
        from user_routines import TemperatureFunctionTime
        reac = ct.IdealGasConstPressureReactor(gas,energy='off')
        #Number of solution variables is number of species + mass, temperature
        n_vars = reac.kinetics.n_species + 2
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
        tempFunc = ct.Func1(TemperatureFunctionTime())
    elif keywords['problemType'] == 8:
        reac = ct.IdealGasConstPressureReactor(gas,energy='off')
        #Number of solution variables is number of species + mass, temperature
        n_vars = reac.kinetics.n_species + 2
        wall = ct.Wall(reac,env,A=1.0,velocity=0)
        tempFunc = ct.Func1(TemperatureProfile(keywords))
    
    if 'reactorVolume' in keywords:
        reac.volume = keywords['reactorVolume']
        
    netw = ct.ReactorNet([reac])
            
    if 'sensitivity' in keywords:
        sensitivity = True
        for i in range(reac.kinetics.n_reactions):
            reac.add_sensitivity_reaction(i)
        if 'sensAbsTol' in keywords:
            netw.atol_sensitivity = keywords['sensAbsTol']
        else:
            netw.atol_sensitivity = 1.0E-06
        if 'sensRelTol' in keywords:
            netw.rtol_sensitivity = keywords['sensRelTol']
        else:
            netw.rtol_sensitivity = 1.0E-04
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
    else:
        netw.atol = 1.0E-20
        
    if 'reltol' in keywords:
        netw.rtol = keywords['reltol']
    else:
        netw.rtol = 1.0E-08
        
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
        
    tableDef = {'time':tables.Float64Col(pos=0),
               'temperature':tables.Float64Col(pos=1),
               'pressure':tables.Float64Col(pos=2),
               'volume':tables.Float64Col(pos=3),
               'massfractions':tables.Float64Col(shape=(reac.thermo.n_species),pos=4),
               }
    if sensitivity:
        tableDef['sensitivity'] = tables.Float64Col(shape=(n_vars,netw.n_sensitivity_params),pos=5)
        
    species_names = reac.thermo.species_names
    
    #Use the table format of hdf instead of the array format. This way, each variable can be saved 
    #in its own column and referenced individually when read. Solution to the interpolation problem 
    #was made by saving each time step into a numpy array. The arrays are not vertically appended
    #so we should eliminate the hassle associated with that.
    with tables.open_file(saveFilename, mode = 'w', title = 'CanSen Save File') as saveFile:
        table = saveFile.create_table(saveFile.root, 'reactor', tableDef, 'Reactor State')
        
        timestep = table.row
        timestep['time'] = netw.time
        timestep['temperature'],timestep['pressure'],timestep['massfractions'] = reac.thermo.TPY
        timestep['volume'] = reac.volume
        if sensitivity:
            timestep['sensitivity'] = np.zeros((n_vars,netw.n_sensitivity_params))
        timestep.append()
        table.flush()
        
        prevTime = np.hstack((netw.time, reac.thermo.T, reac.thermo.P, reac.volume, wall.vdot(netw.time), reac.thermo.X))
        printer.reactor_state_printer(prevTime,species_names)
        
        while netw.time < tend:
        
            if tempFunc is not None:
                gas.TP = tempFunc(netw.time), None
                
            netw.step(tend)
            curTime = np.hstack((netw.time, reac.thermo.T, reac.thermo.P, reac.volume, wall.vdot(netw.time), reac.thermo.X))
            
            if netw.time > tend:
                interpState = utils.reactor_interpolate(tend,prevTime,curTime)
                printer.reactor_state_printer(interpState,species_names,end=True)
                timestep['time'] = tend
                timestep['temperature'] = interpState[1]
                timestep['pressure'] = interpState[2]
                timestep['massfractions'] = interpState[5:] * reac.thermo.molecular_weights/reac.thermo.mean_molecular_weight
                timestep['volume'] = interpState[3]
                if sensitivity:
                    #Add sensitivity interpolation here by reading from file on disk. Only have to do it once, so shouldn't be
                    #too expensive
                    pass
                break
                
            if saveTimeStep is not None:
                pass
            else:
                timestep['time'] = netw.time
                timestep['temperature'],timestep['pressure'],timestep['massfractions'] = reac.thermo.TPY
                timestep['volume'] = reac.volume
                if sensitivity:
                    timestep['sensitivity'] = netw.sensitivities()
                timestep.append()
                table.flush()
                
            if netw.time > printTime:
                interpState = utils.reactor_interpolate(printTime,prevTime,curTime)
                printer.reactor_state_printer(interpState,species_names)
                printTime += printTimeStep
            elif netw.time == printTime:
                printer.reactor_state_printer(curTime,species_names)
                printTime += printTimeStep
                
            if reac.T >= tempLimit:
                ignitionTime = netw.time
            
            prevTime = curTime
            