#! /usr/bin/python3
from itertools import zip_longest

keywords = {}
keywords['ADD'] = ("Mole fractions of species that should be included in the "
                   "initial composition but excluded from the calculation of "
                   "the equivalence ratio. Only valid when the equivalence "
                   "ratio option is used to specify the composition. See "
                   "|CPROD|_, |EQUI|_, |FUEL|_, |OXID|_, |REAC|_.\n\n"
                   "Example::\n\n    ADD Ar 0.1")
keywords['ATLS'] = ("Absolute tolerance of the accuracy of the sensitivity "
                    "coefficients. Optional keyword, default: 1E-06\n\n"
                    "Example::\n\n    ATLS 1E-06")
keywords['ATOL'] = ("Absolute tolerance of the accuracy of the solution. "
                    "Should be set smaller than the smallest meaningful species "
                    "mass fraction. Optional keyword, default: 1E-20\n\n"
                    "Example::\n\n    ATOL 1E-20")
keywords['CONP'] = ("Solve a constant pressure reactor with the energy "
                    "equation on. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, "
                    "|ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be "
                    "specified.")
keywords['CONT'] = ("Solve a constant pressure reactor with the energy "
                    "equation off. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, "
                    "|ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be "
                    "specified.")
keywords['CONV'] = ("Solve a constant volume reactor with the energy "
                    "equation on. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, "
                    "|ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be "
                    "specified.")
keywords['COTV'] = ("Solve a constant volume reactor with the energy "
                    "equation off. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, "
                    "|ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be "
                    "specified.")
keywords['CPROD'] = ("Complete products of stoichiometric combustion for the "
                     "given fuel and oxidizer compositions. Only valid when "
                     "the equivalence ratio option is used to specify the "
                     "composition. All of the elements specified in the "
                     "|FUEL|_ and |OXID|_ must be included in the set of "
                     "species specified in |CPROD|_. See |ADD|_, |EQUI|_, "
                     "|FUEL|_, |OXID|_, |REAC|_.\n\n"
                     "Example::\n\n    CPROD H2O\n    CPROD CO2")
keywords['DELT'] = ("Time interval for printing to the screen and the text "
                    "output file. Optional keyword, default: |TIME|_/100."
                    "Units: seconds.\n\n"
                    "Example::\n\n    DELT 1E-03")
keywords['DTIGN'] = ("Temperature threshold used to determine the ignition "
                     "delay. Ignition temperature is the initial temperature "
                     "|TEMP|_ plus this value. Will be ignored for cases with "
                     "the energy equation turned off. If both |DTIGN|_ and "
                     "|TLIM|_ are specified, |TLIM|_ will override |DTIGN|_. "
                     "See |TLIM|_. Optional keyword, default: 400. Units: K.\n\n"
                     "Example::\n\n    DTIGN 400")
keywords['DTSV'] = ("Time interval for saving to the binary save file. Values "
                    "are stored at the nearest time step to the save time "
                    "interval. Optional keyword, by default, all time points "
                    "are saved to the binary save file. Units: seconds.\n\n"
                    "Example::\n\n    DTSV 1E-05")
keywords['END'] = ("Signifies the end of the input file in SENKIN. It is "
                   "included in CanSen for compatibility with SENKIN input "
                   "files, but does not do anything. Any CanSen specific "
                   "keywords can be placed after |END|_ and the same input "
                   "file can be used with SENKIN with no changes.")
keywords['EQUI'] = ("Equivalence ratio desired for the initial mixture. If "
                    "|EQUI|_ is specified, all of |CPROD|_, |FUEL|_, and "
                    "|OXID|_ also must be specified, and |ADD|_ can be "
                    "optionally specified. If |EQUI|_ is not specified, the "
                    "reactants must be specified with |REAC|_. See |ADD|_, "
                    "|CPROD|_, |FUEL|_, |OXID|_, |REAC|_.\n\n"
                    "Example::\n\n    EQUI 1.0")
keywords['FUEL'] = ("Relative mole fractions of components in the fuel "
                    "mixture for equivalence ratio calculations. The sum of "
                    "the fuel mole fractions should be 1.0; if they are not, "
                    "they will be normalized and a warning message will be "
                    "printed. If |EQUI|_ is specified, |FUEL|_ must be "
                    "specified. See |ADD|_, |CPROD|_, |EQUI|_, |OXID|_, "
                    "|REAC|_.\n\n"
                    "Example::\n\n FUEL CH4 1.0")
keywords['IGNBREAK'] = ("CanSen specific keyword. Indicates that the "
                        "simulation should exit when ignition is encountered, "
                        "instead of continuing until the end time |TIME|_ is "
                        "reached. The criterion for ignition is specified by "
                        "|DTIGN|_ or |TLIM|_. Optional keyword.")
keywords['OXID'] = ("Relative mole fractions of components in the oxidizer "
                    "mixture for equivalence ratio calculations. The sum of "
                    "the oxidizer mole fractions should be 1.0; if they are "
                    "not, they will be normalized and a warning message will "
                    "be printed. If |EQUI|_ is specified, |OXID|_ must be "
                    "specified. See |ADD|_, |CPROD|_, |EQUI|_, |FUEL|_, "
                    "|REAC|_.\n\n"
                    "Example::\n\n    OXID O2 1.0\n    OXID N2 3.76")
keywords['PRES'] = ("Initial reactor pressure. Required keyword. Units: "
                    "atmospheres.\n\n"
                    "Example::\n\n    PRES 1.0")
keywords['REAC'] = ("Initial mole fraction of a reactant gas in the reactor. "
                    "Required keyword if |EQUI|_ is not specified; however, "
                    "only one of |REAC|_ or |EQUI|_ may be specified. If the "
                    "mole fractions of the components given on |REAC|_ lines "
                    "do not sum to 1.0, they will be normalized and a warning "
                    "message will be printed.\n\n"
                    "Example::\n\n    "
                    "REAC CH4 1.0\n    REAC O2 1.0\n    REAC N2 3.76")
keywords['RTLS'] = ("Relative tolerance of the accuracy of the sensitivity "
                    "coefficients. Optional keyword, default: 1E-04\n\n"
                    "Example::\n\n    RTLS 1E-04")
keywords['RTOL'] = ("Relative tolerance of the accuracy of the solution. "
                    "Can be interpreted roughly as the number of significant "
                    "digits expected in the solution. Optional keyword, "
                    "default: 1E-08\n\n"
                    "Example::\n\n    RTOL 1E-08")
keywords['SENS'] = ("Calculate sensitivity coefficients for the solution "
                    "variables. The sensitivity coefficients are stored in "
                    "a 2-D array, with dimensions of (number of solution "
                    "variables, number of reactions). For |CONV|_, |COTV|_, "
                    "|VPRO|_ and |VTIM|_ cases, the order of the sensitivity "
                    "coefficients (i.e. the rows) is::\n\n"
                    "- 0  - mass\n- 1  - volume\n- 2  - temperature\n- 3+ "
                    "mass fractions of the species\n\n"
                    "For |CONP|_, |CONT|_, |TPRO|_, and |TTIM|_ cases, the "
                    "order of the sensitivity coefficients (i.e. the rows) is "
                    "::\n\n"
                    "- 0  - mass\n- 1  - temperature\n- 2+ - mass fractions "
                    "of the species")
keywords['STPT'] = ("Maximum internal time step for the solver. Optional "
                    "keyword. If any of |DELT|_, |DTSV|_, or |STPT|_ are "
                    "specified, the minimum of these is used as the maximum "
                    "internal time step. Otherwise, the default maximum time "
                    "step is the end time |TIME|_/100.\n\n"
                    "Example::\n\n    STPT 1E-5")
keywords['TEMP'] = ("Initial reactor temperature. Required keyword. Units: "
                    "K.\n\n"
                    "Example::\n\n    TEMP 800")
keywords['TIME'] = ("End time for the integration. Unless, |IGNBREAK|_ is "
                    "specified and its condition satisfied, the solver will "
                    "integrate until |TIME|_ is reached. Required keyword. "
                    "Units: seconds.\n\n"
                    "Example::\n\n    TIME 1E-03")
keywords['TLIM'] = ("Ignition temperature. Ignition is considered to have "
                    "occurred when this temperature is exceeded. If both "
                    "|DTIGN|_ and |TLIM|_ are specified, |TLIM|_ overrides "
                    "|DTIGN|_. Optional keyword, default: |TEMP|_ + 400. "
                    "Units: K.\n\n"
                    "Example::\n\n    TLIM 1200")
keywords['TPRO'] = ("Specify the reactor temperature as a function of time. "
                    "Multiple invocations of this keyword build a profile of "
                    "the temperature over the given times. This profile is "
                    "linearly interpolated to set the reactor temperature at "
                    "any solver time step. When the end time of the profile "
                    "is exceeded, the temperature remains constant at the "
                    "last specified value. One of |CONP|_, |CONT|_, |CONV|_, "
                    "|COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ "
                    "must be specified. Units: seconds, K.\n\n"
                    "Example::\n\n    TPRO 0.0 800\n    TPRO 0.1 900")
keywords['TTIM'] = ("Specify the reactor temperature as a user-provided "
                    "function of time. To use this keyword, the user must "
                    "edit the :class:`~user_routines.TemperatureFunctionTime` class in the "
                    ":mod:`user_routines` file. Any parameters to be read "
                    "from external files should be loaded in the "
                    ":meth:`~user_routines.TemperatureFunctionTime.__init__` method so that "
                    "they are not read on every time step. The parameters "
                    "should be stored in the ``self`` instance of the class "
                    "so that they can be accessed in the "
                    ":meth:`~user_routines.TemperatureFunctionTime.__call__` method. The "
                    ":meth:`~user_routines.TemperatureFunctionTime.__call__` method should "
                    "contain the actual calculation and return of the "
                    "temperature given the input ``time``.One of |CONP|_, "
                    "|CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, "
                    "|VPRO|_, or |VTIM|_ must be specified. Units: K.")
keywords['VOL'] = ("Initial volume of the reactor. Optional keyword, default: "
                   "1E6 cm**3. Units: cm**3.\n\n"
                   "Example::\n\n    VOL 1.0")
keywords['VPRO'] = ("Specify the reactor volume as a function of time. "
                    "Multiple invocations of this keyword build a profile of "
                    "the volume over the given times. This profile is "
                    "linearly interpolated to set the reactor volume at "
                    "any solver time step. When the end time of the profile "
                    "is exceeded, the volume remains constant at the "
                    "last specified value. One of |CONP|_, |CONT|_, |CONV|_, "
                    "|COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ "
                    "must be specified. Units: seconds, m**3.\n\n"
                    "Example::\n\n    VPRO 0.0 1E-5\n    VPRO 0.1 1E-6")
keywords['VTIM'] = ("Specify the reactor volume as a user-provided "
                    "function of time. To use this keyword, the user must "
                    "edit the :class:`~user_routines.VolumeFunctionTime` class in the "
                    ":mod:`user_routines` file. Any parameters to be read "
                    "from external files should be loaded in the "
                    ":meth:`~user_routines.VolumeFunctionTime.__init__` method so that "
                    "they are not read on every time step. The parameters "
                    "should be stored in the ``self`` instance of the class "
                    "so that they can be accessed in the "
                    ":meth:`~user_routines.VolumeFunctionTime.__call__` method. The "
                    ":meth:`~user_routines.VolumeFunctionTime.__call__` method should "
                    "contain the actual calculation and must return the "
                    "velocity of the wall given the input ``time``. One of "
                    "|CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, "
                    "|TTIM|_, |VPRO|_, or |VTIM|_ must be specified. Units: "
                    "m/s.")
keywords['ICEN'] = ("Specify the internal combustion engine model be used. See "
                    ":doc:`the documentation for the model </icengine>` for "
                    "information on the derivation. See also |BORE|_, |CMPR|_, "
                    "|CRAD|_, |DEG0|_, |LOLR|_, |RODL|_, |RPM|_, |STROKE|_, "
                    "|VOLD|_, and |VOLC|_. One of |CONP|_, |CONT|_, |CONV|_, "
                    "|COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ "
                    "must be specified.")
keywords['CMPR'] = ("Specify the compression ratio for the internal combustion "
                    "engine model. Defined as the maximum total volume in the "
                    "cylinder divided by the clearance volume. See the "
                    ":ref:`documentation <compression-ratio>`. See also: "
                    "|VOLC|_, |VOLD|_.\n\nExample::\n\n    CMPR 10.0")
keywords['DEG0'] = ("Specify the initial crank angle of the simulation. "
                    "Units: degrees. Default: 180 deg.\n\nExample::\n\n    "
                    "DEG0 180")
keywords['VOLD'] = ("Specify the swept or displaced volume, :math:`V_d`. "
                    "Units: cm**3. See |CMPR|_, |VOLC|_.\n\n"
                    "Example::\n\n    VOLD 10.0")
keywords['VOLC'] = ("Specify the clearance volume, :math:`V_c`.  Units: "
                    "cm**3. See |CMPR|_, |VOLD|_.\n\n"
                    "Example::\n\n    VOLC 1.0")
keywords['LOLR'] = ("Specify the ratio of the connecting rod length, "
                    ":math:`\\ell`, to the crank radius, :math:`a`. See "
                    "|RODL|_, |CRAD|_.\n\nExample::\n\n    LOLR 3.5")
keywords['RPM'] = ("Specify the rotation rate of the engine in revolutions "
                   "per minute.\n\nExample::\n\n    RPM 1500")
keywords['BORE'] = ("CanSen specific keyword. Bore diameter of the engine "
                    "cylinder. Units: cm.\n\nExample::\n\n    BORE 1.0")
keywords['STROKE'] = ("CanSen specific keyword. Specify the stroke length "
                      "of the engine, :math:`L`. Units: cm.\n\nExample::\n\n"
                      "    STROKE 7.0")
keywords['RODL'] = ("CanSen specific keyword. Specify the connecting rod "
                    "length, :math:`\\ell`. Units: cm.\n\nExample::\n\n"
                    "    RODL 5.0")
keywords['CRAD'] = ("CanSen specific keyword. Specify the crank radius. "
                    "Units: cm.\n\nExample::\n\n    CRAD 3.5")
                    
sorted_keys = sorted(keywords.keys())
print(sorted_keys)
out_list = []
for key in sorted_keys:
    out_list.append('|' + key + '|_ ')
    
grouped = zip_longest(*[iter(out_list)]*7, fillvalue = '')
    
preamble = """.. _sec-keywords:

=========================
Supported SENKIN Keywords
=========================

The following is a list of the currently supported keywords in the 
SENKIN-format input file:"""

with open('keywords.rst','wb') as out_file:
    out_file.write(preamble.encode('utf-8'))
    out_file.write('\n\n'.encode('utf-8'))
    for items in grouped:
        out_file.write('| '.encode('utf-8'))
        for item in items:
            out_file.write(item.encode('utf-8'))
        out_file.write('\n'.encode('utf-8'))
    out_file.write('\n====\n\n'.encode('utf-8'))
    for key in sorted_keys[:-1]:
        out_file.write(bytes('.. |' + key + '| replace:: ``' + key + '``\n','utf-8'))
        out_file.write(bytes('.. _' + key + ':\n\n','utf-8'))
        out_file.write(bytes('``' + key + '``: ' + keywords[key] + '\n\n====\n\n','utf-8'))
    key = sorted_keys[-1]
    out_file.write(bytes('.. |' + key + '| replace:: ``' + key + '``\n','utf-8'))
    out_file.write(bytes('.. _' + key + ':\n\n','utf-8'))
    out_file.write(bytes('``' + key + '``: ' + keywords[key] + '\n\n','utf-8'))