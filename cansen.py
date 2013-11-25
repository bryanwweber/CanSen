#! /usr/bin/python3
import parsers

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

def main(argv):
    import os
    version = '0.0.1'
    (inputFilename,outputFilename,mechFilename,
     saveFilename,thermoFilename,convert,) = parsers.cli_parser(argv)
    
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
        
    ret, = parsers.read_input_file(inputFilename)
    problemType = ret['problemType']
        
    if problemType == 1:
        from run_cases import constant_volume_reactor
        print("Problem Type 1")
        constant_volume_reactor(mechFilename,saveFilename,ret)
    elif problemType == 2:
        from run_cases import constant_pressure_reactor
        print("Problem Type 2")
        constant_pressure_reactor(mechFilename,saveFilename,ret)
    else:
        print('Error: Unknown Problem Type')
    
    out.close()
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])


