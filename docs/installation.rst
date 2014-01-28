.. _sec-installation:

=========================
CanSen Installation Guide
=========================

.. toctree::
    :maxdepth: 1

CanSen can be installed on any platform that supports Python and 
Cantera. This guide contains instructions for Windows and Ubuntu 12.04.

CanSen has several dependencies, including:

* `Cantera <http://code.google.com/p/cantera>`_
* `NumPy <http://www.numpy.org>`_
* `PyTables <http://www.pytables.org/moin>`__

Windows
=======

Python can be downloaded and installed from the `Python.org page`_.
Installation instructions for Cantera on Windows can be found on the
`Google code`_ page. Make sure to download the correct version for 
your Python and 32- or 64-bit Windows, depending on which version your
OS is. If NumPy is not already installed, download the proper version
from the `Windows Binaries`_ page. From the same page, download the 
installer for PyTables_ and its dependency numexpr_.

.. _Python.org page: http://www.python.org/download/
.. _Google code: https://code.google.com/p/cantera/wiki/WindowsInstallation
.. _Windows Binaries: http://www.lfd.uci.edu/~gohlke/pythonlibs/
.. _PyTables: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables
.. _numexpr: http://www.lfd.uci.edu/~gohlke/pythonlibs/#numexpr

Then, download the most recent release of CanSen from GitHub_. Unzip 
the zip file, and you're ready to go!

.. _GitHub: https://github.com/bryanwweber/CanSen/releases

Alternatively, you can use Git to download the developer version. 
**WARNING:** The developer version of CanSen is not guaranteed to be
working at any given commit. Proceed with caution.::

    git clone git://github.com/bryanwweber/CanSen.git

will download the repository into a folder called ``CanSen``.

Ubuntu
======

These instructions are for Ubuntu 12.04, but should work with only slight 
changes for most major releases of Linux. Optionally, download Python 3
from the apt repositories. At the same time, it is good to download
some other dependencies::
    
    sudo apt-get install python3 python3-dev libhdf5-serial-dev
    
Then, install ``distribute`` and ``pip``::
    
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py \
    -O - | sudo python3.2
    sudo easy_install-3.2 pip
    
    or
    
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py \
    -O - | sudo python
    sudo easy_install pip
    
Finally, with ``pip`` installed, install NumPy, Cython, numexpr, and finally, 
PyTables::

    sudo pip-3.2 install numpy cython numexpr
    sudo pip-3.2 install pytables
    
    or
    
    sudo pip install numpy cython numexpr
    pip install pytables

Instructions for more complicated cases can be found on the `PyTables documentation`_. 

.. _PyTables documentation: http://pytables.github.io/usersguide/installation.html

Compilation/installation instructions for Cantera can be found in the 
Cantera `documentation`_.

.. _documentation: http://cantera.github.io/docs/sphinx/html/compiling.html

Finally, get the most recent stable release of CanSen from `GitHub`_. Untar
the tarball, and you're ready to go!

    tar -xzf CanSen-X.Y.Z.tar.gz
    
Alternatively, you can use Git to download the developer version. 
**WARNING:** The developer version of CanSen is not guaranteed to be
working at any given commit. Proceed with caution.::

    git clone git://github.com/bryanwweber/CanSen.git

will download the repository into a folder called ``CanSen``.