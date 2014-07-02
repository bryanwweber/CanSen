.. _sec-keywords:

=========================
Supported Input Keywords
=========================

The following is a list of the currently supported keywords in the 
input file. Keywords that include "CanSen specific keyword" 
should be placed after the 'END' keyword to maintain SENKIN compatibility, 
although CanSen has no preference for the order.


| |ADD|_ |ATLS|_ |ATOL|_ |BORE|_ |CMPR|_ |CONP|_ |CONT|_ |CONV|_ |COTV|_ |CPROD|_ 
| |CRAD|_ |DEG0|_ |DELT|_ |DTIGN|_ |DTSV|_ |END|_ |EQUI|_ |FUEL|_ |ICEN|_ |IGNBREAK|_ 
| |LOLR|_ |OXID|_ |PRES|_ |REAC|_ |RODL|_ |RPM|_ |RTLS|_ |RTOL|_ |SENS|_ |STPT|_ 
| |STROKE|_ |TEMP|_ |TIME|_ |TLIM|_ |TPRO|_ |TTIM|_ |VOL|_ |VOLC|_ |VOLD|_ |VPRO|_ 
| |VTIM|_ 

====

.. |ADD| replace:: ``ADD``
.. _ADD:

``ADD``: Mole fractions of species that should be included in the initial composition but excluded from the calculation of the equivalence ratio. Only valid when the equivalence ratio option is used to specify the composition. See |CPROD|_, |EQUI|_, |FUEL|_, |OXID|_, |REAC|_.

Example::

    ADD Ar 0.1

====

.. |ATLS| replace:: ``ATLS``
.. _ATLS:

``ATLS``: Absolute tolerance of the accuracy of the sensitivity coefficients. Optional keyword, default: 1E-06

Example::

    ATLS 1E-06

====

.. |ATOL| replace:: ``ATOL``
.. _ATOL:

``ATOL``: Absolute tolerance of the accuracy of the solution. Should be set smaller than the smallest meaningful species mass fraction. Optional keyword, default: 1E-20

Example::

    ATOL 1E-20

====

.. |BORE| replace:: ``BORE``
.. _BORE:

``BORE``: CanSen specific keyword. Bore diameter of the engine cylinder. Units: cm.

Example::

    BORE 1.0

====

.. |CMPR| replace:: ``CMPR``
.. _CMPR:

``CMPR``: Specify the compression ratio for the internal combustion engine model. Defined as the maximum total volume in the cylinder divided by the clearance volume. See the :ref:`documentation <compression-ratio>`. See also: |VOLC|_, |VOLD|_.

Example::

    CMPR 10.0

====

.. |CONP| replace:: ``CONP``
.. _CONP:

``CONP``: Solve a constant pressure reactor with the energy equation on. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified.

====

.. |CONT| replace:: ``CONT``
.. _CONT:

``CONT``: Solve a constant pressure reactor with the energy equation off. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified.

====

.. |CONV| replace:: ``CONV``
.. _CONV:

``CONV``: Solve a constant volume reactor with the energy equation on. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified.

====

.. |COTV| replace:: ``COTV``
.. _COTV:

``COTV``: Solve a constant volume reactor with the energy equation off. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified.

====

.. |CPROD| replace:: ``CPROD``
.. _CPROD:

``CPROD``: Complete products of stoichiometric combustion for the given fuel and oxidizer compositions. Only valid when the equivalence ratio option is used to specify the composition. All of the elements specified in the |FUEL|_ and |OXID|_ must be included in the set of species specified in |CPROD|_. See |ADD|_, |EQUI|_, |FUEL|_, |OXID|_, |REAC|_.

Example::

    CPROD H2O
    CPROD CO2

====

.. |CRAD| replace:: ``CRAD``
.. _CRAD:

``CRAD``: CanSen specific keyword. Specify the crank radius. Units: cm.

Example::

    CRAD 3.5

====

.. |DEG0| replace:: ``DEG0``
.. _DEG0:

``DEG0``: Specify the initial crank angle of the simulation. Units: degrees. Default: 180 deg.

Example::

    DEG0 180

====

.. |DELT| replace:: ``DELT``
.. _DELT:

``DELT``: Time interval for printing to the screen and the text output file. Optional keyword, default: |TIME|_/100.Units: seconds.

Example::

    DELT 1E-03

====

.. |DTIGN| replace:: ``DTIGN``
.. _DTIGN:

``DTIGN``: Temperature threshold used to determine the ignition delay. Ignition temperature is the initial temperature |TEMP|_ plus this value. Will be ignored for cases with the energy equation turned off. If both |DTIGN|_ and |TLIM|_ are specified, |TLIM|_ will override |DTIGN|_. See |TLIM|_. Optional keyword, default: 400. Units: K.

Example::

    DTIGN 400

====

.. |DTSV| replace:: ``DTSV``
.. _DTSV:

``DTSV``: Time interval for saving to the binary save file. Values are stored at the nearest time step to the save time interval. Optional keyword, by default, all time points are saved to the binary save file. Units: seconds.

Example::

    DTSV 1E-05

====

.. |END| replace:: ``END``
.. _END:

``END``: Signifies the end of the input file in SENKIN. It is included in CanSen for compatibility with SENKIN input files, but does not do anything. Any CanSen specific keywords can be placed after |END|_ and the same input file can be used with SENKIN with no changes.

====

.. |EQUI| replace:: ``EQUI``
.. _EQUI:

``EQUI``: Equivalence ratio desired for the initial mixture. If |EQUI|_ is specified, all of |CPROD|_, |FUEL|_, and |OXID|_ also must be specified, and |ADD|_ can be optionally specified. If |EQUI|_ is not specified, the reactants must be specified with |REAC|_. See |ADD|_, |CPROD|_, |FUEL|_, |OXID|_, |REAC|_.

Example::

    EQUI 1.0

====

.. |FUEL| replace:: ``FUEL``
.. _FUEL:

``FUEL``: Relative mole fractions of components in the fuel mixture for equivalence ratio calculations. The sum of the fuel mole fractions should be 1.0; if they are not, they will be normalized and a warning message will be printed. If |EQUI|_ is specified, |FUEL|_ must be specified. See |ADD|_, |CPROD|_, |EQUI|_, |OXID|_, |REAC|_.

Example::

 FUEL CH4 1.0

====

.. |ICEN| replace:: ``ICEN``
.. _ICEN:

``ICEN``: Specify the internal combustion engine model be used. See :doc:`the documentation for the model </icengine>` for information on the derivation. See also |BORE|_, |CMPR|_, |CRAD|_, |DEG0|_, |LOLR|_, |RODL|_, |RPM|_, |STROKE|_, |VOLD|_, and |VOLC|_. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified.

====

.. |IGNBREAK| replace:: ``IGNBREAK``
.. _IGNBREAK:

``IGNBREAK``: CanSen specific keyword. Indicates that the simulation should exit when ignition is encountered, instead of continuing until the end time |TIME|_ is reached. The criterion for ignition is specified by |DTIGN|_ or |TLIM|_. Optional keyword.

====

.. |LOLR| replace:: ``LOLR``
.. _LOLR:

``LOLR``: Specify the ratio of the connecting rod length, :math:`\ell`, to the crank radius, :math:`a`. See |RODL|_, |CRAD|_.

Example::

    LOLR 3.5

====

.. |OXID| replace:: ``OXID``
.. _OXID:

``OXID``: Relative mole fractions of components in the oxidizer mixture for equivalence ratio calculations. The sum of the oxidizer mole fractions should be 1.0; if they are not, they will be normalized and a warning message will be printed. If |EQUI|_ is specified, |OXID|_ must be specified. See |ADD|_, |CPROD|_, |EQUI|_, |FUEL|_, |REAC|_.

Example::

    OXID O2 1.0
    OXID N2 3.76

====

.. |PRES| replace:: ``PRES``
.. _PRES:

``PRES``: Initial reactor pressure. Required keyword. Units: atmospheres.

Example::

    PRES 1.0

====

.. |REAC| replace:: ``REAC``
.. _REAC:

``REAC``: Initial mole fraction of a reactant gas in the reactor. Required keyword if |EQUI|_ is not specified; however, only one of |REAC|_ or |EQUI|_ may be specified. If the mole fractions of the components given on |REAC|_ lines do not sum to 1.0, they will be normalized and a warning message will be printed.

Example::

    REAC CH4 1.0
    REAC O2 1.0
    REAC N2 3.76

====

.. |RODL| replace:: ``RODL``
.. _RODL:

``RODL``: CanSen specific keyword. Specify the connecting rod length, :math:`\ell`. Units: cm.

Example::

    RODL 5.0

====

.. |RPM| replace:: ``RPM``
.. _RPM:

``RPM``: Specify the rotation rate of the engine in revolutions per minute.

Example::

    RPM 1500

====

.. |RTLS| replace:: ``RTLS``
.. _RTLS:

``RTLS``: Relative tolerance of the accuracy of the sensitivity coefficients. Optional keyword, default: 1E-04

Example::

    RTLS 1E-04

====

.. |RTOL| replace:: ``RTOL``
.. _RTOL:

``RTOL``: Relative tolerance of the accuracy of the solution. Can be interpreted roughly as the number of significant digits expected in the solution. Optional keyword, default: 1E-08

Example::

    RTOL 1E-08

====

.. |SENS| replace:: ``SENS``
.. _SENS:

``SENS``: Calculate sensitivity coefficients for the solution variables. The sensitivity coefficients are stored in a 2-D array, with dimensions of (number of solution variables, number of reactions). For |CONV|_, |COTV|_, |VPRO|_ and |VTIM|_ cases, the order of the sensitivity coefficients (i.e. the rows) is::

- 0  - mass
- 1  - volume
- 2  - temperature
- 3+ mass fractions of the species

For |CONP|_, |CONT|_, |TPRO|_, and |TTIM|_ cases, the order of the sensitivity coefficients (i.e. the rows) is ::

- 0  - mass
- 1  - temperature
- 2+ - mass fractions of the species

====

.. |STPT| replace:: ``STPT``
.. _STPT:

``STPT``: Maximum internal time step for the solver. Optional keyword. If any of |DELT|_, |DTSV|_, or |STPT|_ are specified, the minimum of these is used as the maximum internal time step. Otherwise, the default maximum time step is the end time |TIME|_/100.

Example::

    STPT 1E-5

====

.. |STROKE| replace:: ``STROKE``
.. _STROKE:

``STROKE``: CanSen specific keyword. Specify the stroke length of the engine, :math:`L`. Units: cm.

Example::

    STROKE 7.0

====

.. |TEMP| replace:: ``TEMP``
.. _TEMP:

``TEMP``: Initial reactor temperature. Required keyword. Units: K.

Example::

    TEMP 800

====

.. |TIME| replace:: ``TIME``
.. _TIME:

``TIME``: End time for the integration. Unless, |IGNBREAK|_ is specified and its condition satisfied, the solver will integrate until |TIME|_ is reached. Required keyword. Units: seconds.

Example::

    TIME 1E-03

====

.. |TLIM| replace:: ``TLIM``
.. _TLIM:

``TLIM``: Ignition temperature. Ignition is considered to have occurred when this temperature is exceeded. If both |DTIGN|_ and |TLIM|_ are specified, |TLIM|_ overrides |DTIGN|_. Optional keyword, default: |TEMP|_ + 400. Units: K.

Example::

    TLIM 1200

====

.. |TPRO| replace:: ``TPRO``
.. _TPRO:

``TPRO``: Warning: |TPRO|_ is broken in CanSen v1.1 due to incompatibilities with Cantera 2.1. Specify the reactor temperature as a function of time. Multiple invocations of this keyword build a profile of the temperature over the given times. This profile is linearly interpolated to set the reactor temperature at any solver time step. When the end time of the profile is exceeded, the temperature remains constant at the last specified value. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified. Units: seconds, K.

Example::

    TPRO 0.0 800
    TPRO 0.1 900

====

.. |TTIM| replace:: ``TTIM``
.. _TTIM:

``TTIM``: Warning: |TTIM|_ is broken in CanSen v1.1 due to incompatibilities with Cantera 2.1. Specify the reactor temperature as a user-provided function of time. To use this keyword, the user must edit the :class:`~user_routines.TemperatureFunctionTime` class in the :mod:`user_routines` file. Any parameters to be read from external files should be loaded in the :meth:`~user_routines.TemperatureFunctionTime.__init__` method so that they are not read on every time step. The parameters should be stored in the ``self`` instance of the class so that they can be accessed in the :meth:`~user_routines.TemperatureFunctionTime.__call__` method. The :meth:`~user_routines.TemperatureFunctionTime.__call__` method should contain the actual calculation and return of the temperature given the input ``time``.One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified. Units: K.

====

.. |VOL| replace:: ``VOL``
.. _VOL:

``VOL``: Initial volume of the reactor. Optional keyword, default: 1E6 cm**3. Units: cm**3.

Example::

    VOL 1.0

====

.. |VOLC| replace:: ``VOLC``
.. _VOLC:

``VOLC``: Specify the clearance volume, :math:`V_c`.  Units: cm**3. See |CMPR|_, |VOLD|_.

Example::

    VOLC 1.0

====

.. |VOLD| replace:: ``VOLD``
.. _VOLD:

``VOLD``: Specify the swept or displaced volume, :math:`V_d`. Units: cm**3. See |CMPR|_, |VOLC|_.

Example::

    VOLD 10.0

====

.. |VPRO| replace:: ``VPRO``
.. _VPRO:

``VPRO``: Specify the reactor volume as a function of time. Multiple invocations of this keyword build a profile of the volume over the given times. This profile is linearly interpolated to set the reactor volume at any solver time step. When the end time of the profile is exceeded, the volume remains constant at the last specified value. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified. Units: seconds, m**3.

Example::

    VPRO 0.0 1E-5
    VPRO 0.1 1E-6

====

.. |VTIM| replace:: ``VTIM``
.. _VTIM:

``VTIM``: Specify the reactor volume as a user-provided function of time. To use this keyword, the user must edit the :class:`~user_routines.VolumeFunctionTime` class in the :mod:`user_routines` file. Any parameters to be read from external files should be loaded in the :meth:`~user_routines.VolumeFunctionTime.__init__` method so that they are not read on every time step. The parameters should be stored in the ``self`` instance of the class so that they can be accessed in the :meth:`~user_routines.VolumeFunctionTime.__call__` method. The :meth:`~user_routines.VolumeFunctionTime.__call__` method should contain the actual calculation and must return the velocity of the wall given the input ``time``. One of |CONP|_, |CONT|_, |CONV|_, |COTV|_, |ICEN|_, |TPRO|_, |TTIM|_, |VPRO|_, or |VTIM|_ must be specified. Units: m/s.

