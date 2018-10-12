"""Test the main CanSen module."""

import os
import shutil

import pytest

from ..cansen import main


@pytest.fixture()
def datafiles(tmpdir, request):
    """Move a folder of test files to a pytest ``tmpdir``.

    The folder should have the same name as this module.
    Similar to https://stackoverflow.com/a/29631801/2449192
    """
    test_dir, _ = os.path.splitext(request.module.__file__)
    test_dir = os.path.abspath(test_dir)
    dir_name = os.path.basename(test_dir)

    try:
        tmpdir = shutil.copytree(test_dir, os.path.join(tmpdir, dir_name))
    except OSError:
        shutil.rmtree(os.path.join(tmpdir, dir_name))
        tmpdir = shutil.copytree(test_dir, os.path.join(tmpdir, dir_name))

    return tmpdir


def test_one_complete_simulation(datafiles):
    """Run an integration test of one simulation."""
    input_file = os.path.abspath(os.path.join(datafiles, 'test_one_complete_simulation.inp'))
    chem_file = os.path.abspath(os.path.join(datafiles, 'gri30.xml'))
    os.chdir(datafiles)
    main(input_filename=input_file, mech_filename=chem_file)


def test_multi_simulation(datafiles):
    """Run an integration test of multiple simulations."""
    input_file = os.path.abspath(os.path.join(datafiles, 'test_multi_simulation.inp'))
    chem_file = os.path.abspath(os.path.join(datafiles, 'gri30.xml'))
    os.chdir(datafiles)
    main(input_filename=input_file, mech_filename=chem_file, multi=1)
