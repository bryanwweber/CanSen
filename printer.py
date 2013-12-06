import sys
import numpy as np
from itertools import zip_longest

divider = '*'*120

class Tee(object):
     def __init__(self, name, mode):
         self.file = open(name, mode)
         self.stdout = sys.stdout
         sys.stdout = self
     def close(self):
         if self.stdout is not None:
             sys.stdout = self.stdout
             self.stdout = None
         if self.file is not None:
             self.file.close()
             self.file = None
     def write(self, data):
         self.file.write(data)
         self.stdout.write(data)
     def flush(self):
         self.file.flush()
         self.stdout.flush()
     def __del__(self):
         self.close()
         
def reactor_state_printer(time,reactor,numPrintCols = 3,):
    print(divider)
    print('Solution time = {:E}'.format(time))
    print('Reactor Temperature (K) = {0:.4f}\n\
Reactor Pressure (Pa)   = {1:.4f}'.format(reactor.T,reactor.thermo.P))
    print('Gas Phase Mole Fractions:')
    outlist = []
    for speciesName, x in zip(reactor.thermo.species_names, reactor.thermo.X):
            outlist.append('%(spec)15s = %(molefrac)10E' % {'spec':speciesName, 'molefrac':x})
    grouped = zip_longest(*[iter(outlist)]*numPrintCols, fillvalue = '')
    for items in grouped:
        for item in items:
            print(item, end='')
        print('\n',end='')
    print(divider,'\n')