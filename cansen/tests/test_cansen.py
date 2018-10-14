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

def test_one_complete_simulation(datafiles, capsys):
    """Run an integration/regression test of one simulation."""
    input_file = os.path.abspath(os.path.join(datafiles, 'test_one_complete_simulation.inp'))
    chem_file = os.path.abspath(os.path.join(datafiles, 'gri30.xml'))
    save_file = os.path.abspath(os.path.join(datafiles, 'save.hdf'))
    output_file = os.path.abspath(os.path.join(datafiles, 'output.out'))
    main(input_filename=input_file, mech_filename=chem_file, save_filename=save_file,
         output_filename=output_file)
    assert os.path.isfile(output_file)
    captured = capsys.readouterr()
    with open(output_file, 'r') as o:
        output_info = o.read()

    assert output_info == captured.out


def test_multi_simulation(datafiles):
    """Run an integration/regression test of multiple simulations."""
    input_file = os.path.abspath(os.path.join(datafiles, 'test_multi_simulation.inp'))
    chem_file = os.path.abspath(os.path.join(datafiles, 'gri30.xml'))
    chem_file = os.path.abspath(os.path.join(datafiles, 'gri30.xml'))
    save_file = os.path.abspath(os.path.join(datafiles, 'save.hdf'))
    output_file = os.path.abspath(os.path.join(datafiles, 'output.out'))
    main(input_filename=input_file, mech_filename=chem_file, save_filename=save_file,
         output_filename=output_file, multi=1)
    assert os.path.isfile(output_file)
