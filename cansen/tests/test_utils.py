"""Test the CanSen utilities."""

import os
import shutil

import pytest

from ..utils import convert_mech


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


def test_convert_mech_w_thermo(datafiles):
    """Test conversion when thermo is in the input file.

    This case is the single argument to ``convert_mech``.
    """
    input_file = os.path.join(datafiles, 'test-w-thermo.inp')
    blessed_file = os.path.join(datafiles, 'test-blessed.cti')
    os.chdir(datafiles)
    output_file = convert_mech(input_file)
    output_file = os.path.join(datafiles, output_file)
    with open(output_file, 'r') as o_file, open(blessed_file, 'r') as b_file:
        assert o_file.read() == b_file.read()


def test_convert_mech_wo_thermo(datafiles):
    """Test conversion when thermo is in a separate file.

    This is the two argument case for ``convert_mech``.
    """
    input_file = os.path.join(datafiles, 'test-wo-thermo.inp')
    dat_file = os.path.join(datafiles, 'test-wo-thermo.dat')
    blessed_file = os.path.join(datafiles, 'test-blessed.cti')
    os.chdir(datafiles)
    output_file = convert_mech(input_file, dat_file)
    output_file = os.path.join(datafiles, output_file)
    with open(output_file, 'r') as o_file, open(blessed_file, 'r') as b_file:
        assert o_file.read() == b_file.read()
