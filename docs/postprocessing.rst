.. _sec-postprocessing:

==============
Postprocessing
==============

CanSen saves the solution information to a binary save file in a 
standard format called `HDF5`_. Many programming and scripting 
languages have interfaces for HDF5 files, including `C++`_, `MATLAB`_, 
`Fortran 90`_ and Python. Notably, these are all of the interfaces that
Cantera supports. The Python interface will be demonstrated in this 
tutorial, but the structure of the data and thus the main content of 
this tutorial will remain the same for all of the interfaces.

.. _HDF5: http://www.hdfgroup.org/HDF5/
.. _C++: http://ftp.hdfgroup.org/HDF5/doc/cpplus_RM/index.html
.. _MATLAB: http://www.mathworks.com/help/matlab/hdf5-files.html;jsessionid=a596eeee2bf156629abd647818b6
.. _Fortran 90: http://www.hdf5.com/HDF5/doc/fortran/index.html

There are several Python interfaces for HDF5, but the one we will be 
using is called PyTables. The documentation for PyTables can be found 
on `their GitHub`_ page. 

.. _their GitHub: http://pytables.github.io/usersguide/index.html

Note that on the following lines, the ``>>>`` indicates that you should 
type the text at a Python prompt, not including the ``>>>``. First, we 
will import the necessary libraries::

    >>> import tables
    >>> import cantera as ct
    
If either of these don't work, make sure that PyTables and Cantera are 
both properly installed. 

To print information about the save file, just type the name of 
its variable

    >>> save_file

The data is saved in the save file with the Table format. Each
Row in the Table represents one time step. Each Row further
consists of a number of Columns where the data is stored. The
Columns can be of arbitrary shape - thus, the entire 2-D 
sensitivity array is saved in one Column on each time step (i.e.
in each row).

The format of the save file is hierarchical. The Table with each
time step is stored in a Group, which is stored in the Root. It
can be thought of as nested directories, with the Root as the top 
directory, then the Group, then the Table, like so::
  
  Root
      |-Group
            |-Table

To access the information in the Table, it should be stored in a 
variable for quick access. The name of the Group in the save 
files from CanSen is ``reactor``. 

    >>> table = save_file.root.reactor

The Table can now be used like any other class instance. In 
particular, the Table class defines a number of useful functions 
and attributes, such as ``nrows``, which prints the number of 
rows in the Table.

    >>> table.nrows

PyTables provides a method to iterate over the rows in a table
automatically, called ``iterrows``. Here we introduce one way to 
access information in a particular Column in the Table, by using 
natural name indexing. In this case, we print the value of the 
time at each time step.

    >>> for row in table.iterrows():
            print(row['time'])

Note that numerical indexing is also supported. The following is
equivalent to the above:

    >>> for row in table.iterrows():
            print(row[0])
    
The information stored by CanSen is written into case-sensitive 
columns named:

0. ``time``
1. ``temperature``
2. ``pressure``
3. ``volume``
4. ``massfractions``
5. ``sensitivity``

Columns 0-3 have a single value in each row. Column 4 
(``massfractions``) contains a vector with length of the number of
species in the mechanism. Column 5 is optional and included only
if the user requested sensitivity analysis during the simulation. 
The dimensions of Column 5 are ``(n_vars, n_sensitivity_params)``.

In addition to the method of iterating through Rows, entire 
Columns can be accessed and stored in variables. First, all of 
the Columns can be stored in a variable.

    >>> all_cols = table.cols

In this method, different Columns are accessed by their numerical 
index. The first index to ``all_cols`` gives the row and the 
second index gives the column number. Remembering that Python is
zero-based, to access the mass fractions on the 4th time step, do

    >>> mass_fracs_4 = all_cols[3][4]

Individual Columns can be stored in variables as well. This is 
done by the natural naming scheme.

    >>> all_mass_fracs = table.cols.massfractions

This stores an instance of the Column class in ``all_mass_fracs``.
It may be more useful to store the data in a particular column in 
a variable. To do that, get a slice of the column by using the
index and the colon operator. For instance, to store all of the
mass fraction data in a variable

    >>> all_mass_fracs = table.cols.massfractions[:]

Or, to store the fifth through tenth time steps

    >>> mass_fracs_5_10 = table.cols.massfractions[4:9]

Or, to store every other time step from the sixth through the 
20th
    
    >>> mass_fracs_alt = table.cols.massfractions[5:19:2]

Once the data has been extracted from the save file, we need to 
actually be able to do something with it. Fortunately, Cantera
offers a simple way to do this, by initializing a Solution to the 
desired conditions. 

    >>> gas = ct.Solution('mech.xml')
    >>> for row in table.iterrows():
            gas.TPY = row['temperature'], row['pressure'], row['massfractions']
            print(gas.creation_rates)
    
This will print the creation rates of each species at each time 
step. Any method or parameter supported by the Solution class 
can be used to retrieve data at any given time step.

Further information about the PyTables package can be found at 
http://pytables.github.io/usersguide/index.html and information
about Cantera can be found at 
http://cantera.github.io/docs/sphinx/html/index.html