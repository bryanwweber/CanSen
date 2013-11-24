#! /usr/bin/python3
def read_input_file(inputFilename):
    print("Got to input file")
    reactants = {}
    with open(inputFilename) as inputFile:
        for line in inputFile:
            if line.upper().startswith('CONV'):
                problemType = 1
            elif line.upper().startswith('CONP'):
                problemType = 2
            elif line.upper().startswith('TEMP'):
                temperature = line.split()[1]
            elif line.upper().startswith('REAC'):
                species = line.split()[1]
                molefrac = line.split()[2]
                reactants[species] = molefrac
            elif line.upper().startswith('PRES'):
                pressure = line.split()[1]
            elif line.upper().startswith('TIME'):
                endTime = line.split()[1]
            elif line.upper().startswith('TLIM'):
                tempLimit = line.split()[1]
            elif line.upper() == 'END':
                break
            else:
                print('Keyword not found',line)
                sys.exit(1)
    return problemType,temperature,pressure,reactants,endTime,tempLimit

def main(argv):
    import getopt
    inputFilename = 'input.inp'
    outputFilename = 'output.out'
    mechFilename = 'chem.inp'
    saveFilename = 'save.pkl'
    help = "Haven't written the help yet, sorry!"
    try:
        opts, args = getopt.getopt(argv, "hi:o:c:x:",
                                   ["help", "input=", "output=", "mech=", 
                                   "save="])
    except getopt.GetOptError as e:
        print('You did not enter an option properly.')
        print(e)
        print(help)
        sys.exit(1)
    for opt, arg in opts:
        if opt in {"-h","--help"}:
            print(help)
            sys.exit(0)
        elif opt in {"-i","--input"}:
            inputFilename = arg
        elif opt in {"-o","--output"}:
            outputFilename = arg
        elif opt in {"-c","--mech"}:
            mechFilename = arg
        elif opt in {"-x","--save"}:
            saveFilename = arg
    if mechFilename.endswith('.inp'):
        from cantera import ck2cti
        arg = '--input='+mechFilename
        ck2cti.main([arg])
        mechFilename = mechFilename[:-4]+'.cti'
        print(mechFilename)
    ret = read_input_file(inputFilename)
    problemType = ret[0]
    temperature = ret[1]
    pressure = ret[2]
    reactants = ret[3]
    endTime = ret[4]
    tempLimit = ret[5]
    if len(ret) > 6:
        extraArgs = ret[6:]
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])



#import cantera as ct
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

