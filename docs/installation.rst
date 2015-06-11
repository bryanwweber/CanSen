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
`Cantera documentation`_ page. Make sure to download the correct version for
your Python and 32- or 64-bit Windows, depending on which version your
OS is. If NumPy is not already installed, download the proper version
from the `Windows Binaries`_ page. From the same page, download the
installer for PyTables_ and its dependency numexpr_.

.. _Python.org page: http://www.python.org/download/
.. _Cantera documentation: http://cantera.github.io/docs/sphinx/html/install.html#windows
.. _Windows Binaries: http://www.lfd.uci.edu/~gohlke/pythonlibs/
.. _PyTables: http://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables
.. _numexpr: http://www.lfd.uci.edu/~gohlke/pythonlibs/#numexpr

Then, download the most recent release of CanSen from GitHub_.

.. _GitHub: https://github.com/bryanwweber/CanSen/releases

Wheels
------

The recommended installation procedure is to download the Wheel file
(:code:`*.whl`). The advantage of this is that the binaries of PyTables
and numexpr will also come in Wheel format. If all the Wheel files are
collected in the same directory, using :code:`pip` to install all of them
in one shot is simple::

   pip install numexpr tables cansen --no-index -f . --no-deps

Source Distribution
-------------------

Unzip the zip file, run ::

    python setup.py install

and the package should be installed properly. Then use as normal.

Development Version
-------------------

Alternatively, you can use Git to download the developer version.
**WARNING:** The developer version of CanSen is not guaranteed to be
working at any given commit. Proceed with caution.::

    git clone git://github.com/bryanwweber/CanSen.git

will download the repository into a folder called ``CanSen``.
Then follow the instructions for the source distribution.

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

Wheels
------

The recommended installation procedure is to download the Wheel file
(:code:`*.whl`). Then, use :code:`pip` to install CanSen::

   pip install cansen --no-index -f . --no-deps

Source Distribution
-------------------

Unzip the zip file, run ::

    python setup.py install

and the package should be installed properly. Then use as normal.

Development Version
-------------------

Alternatively, you can use Git to download the developer version.
**WARNING:** The developer version of CanSen is not guaranteed to be
working at any given commit. Proceed with caution.::

    git clone git://github.com/bryanwweber/CanSen.git

will download the repository into a folder called ``CanSen``.
Then follow the instructions for the source distribution.
