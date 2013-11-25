import cantera as ct

def constant_volume_reactor(mechFilename,saveFilename,keywords):
    gas = ct.Solution(mechFilename)
    gas.TPX = keywords['temperature'],keywords['pressure'],','.join(keywords['reactants'])
    reac = ct.Reactor(gas)
    netw = ct.ReactorNet([reac])
    tend = keywords['endTime']
    time = 0
    while time < tend:
        time = netw.step(tend)
        if reac.T > keywords['tempLimit']:
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

