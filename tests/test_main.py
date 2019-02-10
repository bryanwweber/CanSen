"""Test the main CanSen module."""
import os
from pathlib import Path

import pytest

from cansen.__main__ import main
from cansen._version import __version__


# Tests of the CLI parser in the main function.
# These tests are for things that won't be covered by various integration tests.
def test_no_args():
    """Test that running the parser without arguments raises an error."""
    with pytest.raises(SystemExit) as e:
        main([])
    assert str(e.value) == "1"

def test_version_output(capsys):
    """Test that the version output is printed properly."""
    loc = Path(__file__).parent.parent.joinpath('cansen')

    with pytest.raises(SystemExit) as e:
        main(['-V'])
    assert str(e.value) == '0'
    captured = capsys.readouterr()
    assert captured.out == f"CanSen {__version__} from {loc} ()\n"

    with pytest.raises(SystemExit) as e:
        main(['--version'])
    assert str(e.value) == '0'
    captured = capsys.readouterr()
    assert captured.out == f"CanSen {__version__} from {loc} ()\n"

def test_convert_mech_w_thermo(datadir):
    """Test conversion when thermo is in the input file.

    This case is the single argument to ``convert_mech``.
    """
    input_file = datadir / 'test-w-thermo.inp'
    blessed_file = datadir / 'test-blessed.cti'
    os.chdir(datadir)
    output_file = datadir / 'test-w-thermo.cti'
    with pytest.raises(SystemExit) as e:
        main(['--convert', '--chem', str(input_file)])
    assert str(e.value) == '0'
    assert output_file.read_text() == blessed_file.read_text()

def test_convert_mech_wo_thermo(datadir):
    """Test conversion when thermo is in a separate file.

    This is the two argument case for ``convert_mech``.
    """
    input_file = datadir / 'test-wo-thermo.inp'
    dat_file = datadir / 'test-wo-thermo.dat'
    blessed_file = datadir / 'test-blessed.cti'
    os.chdir(datadir)
    output_file = datadir / 'test-wo-thermo.cti'
    with pytest.raises(SystemExit) as e:
        main(['--convert', '--chem', str(input_file), '--thermo', str(dat_file)])
    assert str(e.value) == '0'
    assert output_file.read_text() == blessed_file.read_text()

def test_convert_mech_missing_chem_file():
    """Test that a missing mechanism file raises a FileNotFoundError."""
    input_file = 'this-file-does-not-exist.inp'
    with pytest.raises(FileNotFoundError) as e:
        main(['--convert', '--chem', input_file])

    assert str(e.value) == f'The chemistry file "{input_file}" could not be found'

def test_convert_mech_missing_thermo_file(datadir):
    """Test that a missing mechanism file raises a FileNotFoundError."""
    input_file = datadir / 'test-wo-thermo.inp'
    dat_file = datadir / 'this-file-does-not-exist.dat'
    os.chdir(datadir)
    with pytest.raises(FileNotFoundError) as e:
        main(['--convert', '--chem', str(input_file), '--thermo', str(dat_file)])

    assert str(e.value) == f'The thermodynamic database "{dat_file}" could not be found'
