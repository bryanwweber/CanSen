#! /usr/bin/python3
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
         
def read_input_file(inputFilename):
    reactants = []
    with open(inputFilename) as inputFile:
        for line in inputFile:
            if line.upper().startswith('CONV'):
                problemType = 1
            elif line.upper().startswith('CONP'):
                problemType = 2
            elif line.upper().startswith('TEMP'):
                temperature = float(line.split()[1])
            elif line.upper().startswith('REAC'):
                species = line.split()[1]
                molefrac = line.split()[2]
                reactants.append(':'.join([species,molefrac]))
            elif line.upper().startswith('PRES'):
                pressure = float(line.split()[1])
            elif line.upper().startswith('TIME'):
                endTime = float(line.split()[1])
            elif line.upper().startswith('TLIM'):
                tempLimit = float(line.split()[1])
            elif line.upper() == 'END':
                break
            else:
                print('Keyword not found',line)
                sys.exit(1)
    return problemType,temperature,pressure,reactants,endTime,tempLimit,

def cli_parser(argv):
    import getopt
    help = "Haven't written the help yet, sorry!"
    try:
        opts, args = getopt.getopt(argv, "hi:o:c:d:x:",
                                   ["help","convert"])
        options = {}
        for o,a in opts:
            options[o] = a
        
        if args:
            raise getopt.GetOptError('Unknown command line option' + 
                                     repr(' '.join(args))
                                    )
    except getopt.GetOptError as e:
        print('You did not enter an option properly.')
        print(e)
        print(help)
        sys.exit(1)
    if '-h' in options or '--help' in options:
        print(help)
        sys.exit(0)
        
    if '-i' in options:
        inputFilename = options['-i']
    else:
        print('Error: The input file must be specified')
        sys.exit(1)
        
    if '-o' in options:
        outputFilename = options['-o']
    else:
        outputFilename = 'output.out'
        
    if '-c' in options:
        mechFilename = options['-c']
    else:
        mechFilename = 'chem.xml'
    
    if '-x' in options:
        saveFilename = options['-x']
    else:
        saveFilename = 'save.pkl'
    
    if '-d' in options:
        thermoFilename = options['-d']
    else:
        thermoFilename = None
     
    convert = '--convert' in options
    
    return inputFilename,outputFilename,mechFilename,saveFilename,thermoFilename,convert,
    
    
def main(argv):
    import os
    version = '0.0.1'
    (inputFilename,outputFilename,mechFilename,
     saveFilename,thermoFilename,convert,) = cli_parser(argv)
    
    out = Tee(outputFilename, 'w')
    print("This is CanSen, the SENKIN equivalent for Cantera, written in \
Python.\nVersion: ",version)
    
    if mechFilename.endswith('.inp'):
        from cantera import ck2cti
        arg = list('--input='+mechFilename)
        if thermoFilename is not None:
            if os.path.isfile(thermoFilename):
                arg.append('--thermo='+thermoFilename)
            else:
                print('Error: Specify proper thermo file')
        ck2cti.main(arg)
        mechFilename = mechFilename[:-4]+'.cti'
        print(mechFilename)
    
    if convert:
        sys.exit(0)
        
    ret = read_input_file(inputFilename)
    problemType = ret[0]
    print(ret[3])
        
    if problemType == 1:
        from run_cases import constant_volume_reactor
        print("Problem Type 1")
        constant_volume_reactor(mechFilename,saveFilename,ret[1:])
    elif problemType == 2:
        print("Problem Type 2")
        #constant_pressure_reactor(mechFilename,ret[1:])
    else:
        print('Error: Unknown Problem Type')
    
    out.close()
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])


