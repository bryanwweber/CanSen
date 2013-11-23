#! /usr/bin/python3
import cantera as ct
gas = ct.Solution('mech.cti')
gas.TPX = 1000,101325,'H2:2,O2:1,N2:3.76'
reac = ct.Reactor(gas)
netw = ct.ReactorNet([reac])
tend = 10
time = 0
while time < tend:
    time = netw.step(tend)
    print(time,reac.T,reac.thermo.P)
    if reac.T > 1400:
        break
