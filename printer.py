import sys
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
         
def reactor_state_printer(reactor,speciesNames,numPrintCols = 3,end=False,):
    time = reactor[0]
    temperature = reactor[1]
    pressure = reactor[2]
    volume = reactor[3]
    vdot = reactor[4]
    molefracs = reactor[5:]
    print(divider)
    if not end:
        print('Solution time = {:E}'.format(time))
    else:
        print('End time reached = {:E}'.format(time))
    print("Reactor Temperature (K) = {:>13.4f}\n".format(temperature),
          "Reactor Pressure (Pa)   = {:>13.4f}\n".format(pressure),
          "Reactor Volume (m**3)   = {:>13.4f}\n".format(volume),
          "Reactor Vdot (m**3/s)   = {:>13.4f}".format(vdot),
          sep='')
    print('Gas Phase Mole Fractions:')
    outlist = []
    for speciesName, x in zip(speciesNames, molefracs):
            outlist.append('%(spec)15s = %(molefrac)10E' % {'spec':speciesName, 'molefrac':x})
    grouped = zip_longest(*[iter(outlist)]*numPrintCols, fillvalue = '')
    for items in grouped:
        for item in items:
            print(item, end='')
        print('\n',end='')
    print(divider,'\n')