.. _sec-usage:

=====
Usage
=====

.. toctree::
    :maxdepth: 1

The following are instructions for usage of CanSen.

Windows
=======

CanSen can be run from the command line (``cmd.exe``) or from within 
`IPython`_. From the command line, change into the directory with the
CanSen script, and run::
    
    py cansen.py [options]
    
In IPython, type::

    In [1]: %run cansen.py [options]

.. _IPython: http://ipython.org/

Ubuntu
======

CanSen can be run either as an executable, or as a script with Python (2 or 3)
or `IPython`_. To run as an executable, change to the directory where
CanSen is located, add the execute bit to cansen.py, and run::

    chmod +x cansen.py
    ./cansen.py [options]
    
To run as a script, change to the directory where CanSen is located and::

    python3 cansen.py [options]
    
    or
    
    python cansen.py [options]
    
Or, in IPython::

    In [1]: %run cansen.py [options]
    
Options
=======

All of the previous commands have shown ``[options]`` to indicate where 
command line options should be specified. The following options are 
available, and can also be seen by using the ``-h`` or ``--help`` 
options::

     -i:
        Specify the simulation input file in SENKIN format. Required.
     -o:
        Specify the text output file. Optional, default: ``output.out``
     -x:
        Specify the binary save output file. Optional, default: 
        ``save.hdf``
     -c:
        Specify the chemistry input file, in either CHEMKIN, Cantera
        CTI or CTML format. Optional, default: ``chem.xml``
     -d:
        Specify the thermodyanmic database. Optional if the 
        thermodyanmic database is specified in the chemistry input 
        file. Otherwise, required.
     --convert:
        Convert the input mechanism to CTI format and quit. If 
        ``--convert`` is specified, the SENKIN input file is optional.
     -h, --help:
        Print this help message and quit.
