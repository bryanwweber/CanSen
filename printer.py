import sys
import os
import math
from itertools import zip_longest

# Create a string to use as a divider. Use a default column width of 
# 80 chars.
divider = '*'*80

class Tee(object):
    """Write to screen and text output file"""
    def __init__(self, name, mode):
        """Initialize output.
        
        :param name:
        Output file name.
        :param mode:
            Read/Write mode of the output file.
        """
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
    def close(self):
        """Close output file and restore standard behavior"""
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
        
def reactor_state_printer(reactor, species_names, ignition_time=None, end=False):
    """Produce pretty-printed output from the input reactor state.
    
    :param reactor:
        Vector of reactor state information.
    :param species_names:
        List of strings of species names.
    :param end:
        Boolean to tell the printer this is the final print operation.
    """
    time = reactor[0]
    temperature = reactor[1]
    pressure = reactor[2]
    volume = reactor[3]
    vdot = reactor[4]
    molefracs = reactor[5:]
    
    # Begin printing
    print(divider)
    if not end:
        print('Solution time = {:E}'.format(time))
    else:
        print('End time reached = {:E}'.format(time))
        if ignition_time is not None:
            print('Ignition time = {:E}'.format(ignition_time))
        else:
            print('Ignition was not found.')
    print("Reactor Temperature (K) = {:>13.4f}\n".format(temperature),
          "Reactor Pressure (Pa)   = {:>13.4f}\n".format(pressure),
          "Reactor Volume (m**3)   = {:>13.4f}\n".format(volume),
          "Reactor Vdot (m**3/s)   = {:>13.4f}".format(vdot),
          sep='')
    print('Gas Phase Mole Fractions:')
    
    # Here we calculate the number of columns of species mole fractions 
    # that will best fill the available number of columns in the 
    # terminal.
    #
    # Add one to the max_species_length to ensure that there is at 
    # least one space between species.
    max_species_length = len(max(species_names, key=len)) + 1
    # Set the precision of the printed mole fractions. This is the
    # number of columns that the number itself will take up, including 
    # the decimal separator. It is not the field width.
    mole_frac_precision = 8
    # Calculate how much space each species print will take. It is the
    # max_species length + len(' = ') + the mole_frac_precision + 
    # len('E+00').
    part_length = max_species_length + 3 + mole_frac_precision + 4
    # Set the default number of columns in the terminal. Choose 80
    # because it is the preferred width of Python source code, and 
    # putting a bigger number may make the output text file harder
    # to read.
    cols = 80
    # Calculate the optimum number of columns as the floor of the 
    # quotient of the print columns and the part_length
    num_print_cols = math.floor(cols/part_length)
    # Create a list to store the values to be printed.
    outlist = []
    for species_name, mole_frac in zip(species_names, molefracs):
            outlist.append('{0:>{1}s} = {2:{3}E}'.format(species_name, 
                                                         max_species_length, 
                                                         mole_frac, 
                                                         mole_frac_precision)
                                                         )
    grouped = zip_longest(*[iter(outlist)]*num_print_cols, fillvalue = '')
    for items in grouped:
        for item in items:
            print(item, end='')
        print('\n',end='')
    print(divider,'\n')