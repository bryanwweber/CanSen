import cantera as ct

def constant_volume_reactor(mechFilename,saveFilename,keywords):
    gas = ct.Solution(mechFilename)
    initialTemp = keywords['temperature']
    initialPres = keywords['pressure']*ct.one_atm
    reactants = ','.join(keywords['reactants'])
    gas.TPX = initialTemp, initialPres, reactants
    reac = ct.Reactor(gas)
    netw = ct.ReactorNet([reac])
    if 'abstol' in keywords:
        netw.atol = keywords['abstol']
    if 'reltol' in keywords:
        netw.rtol = keywords['reltol']
    tend = keywords['endTime']
    time = 0
    tempLimit = keywords['tempLimit'] + keywords['temperature']
    while time < tend:
        time = netw.step(tend)
        #print(time,reac.T,reac.thermo.P)
        if reac.T > tempLimit:
            print(time,reac.T,reac.thermo.P)
            break
            
def constant_pressure_reactor(mechFilename,saveFilename,keywords):
    gas = ct.Solution(mechFilename)
    initialTemp = keywords['temperature']
    initialPres = keywords['pressure']*ct.one_atm
    reactants = ','.join(keywords['reactants'])
    gas.TPX = initialTemp, initialPres, reactants
    reac = ct.ConstPressureReactor(gas)
    netw = ct.ReactorNet([reac])
    tend = keywords['endTime']
    tempLimit = keywords['tempLimit'] + keywords['temperature']
    time = 0
    while time < tend:
        time = netw.step(tend)
        if reac.T > tempLimit:
            print(time,reac.T, reac.thermo.P)
            break
#gas = ct.Solution('mech.cti')
#gas.TPX = 1000,101325,'H2:2,O2:1,N2:3.76'
#reac = ct.Reactor(gas)
#netw = ct.ReactorNet([reac])
#tend = 10
#time = 0
#while time < tend:
#    time = netw.step(tend)
#    print(time,reac.T,reac.thermo.P)
#    if reac.T > 1400:
#        break

