import os
import shutil

import pytest

from ..__main__ import main
from .._version import __version__

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


class TestCliParser():
    """Tests of the CLI parser in the main function.

    These tests are for things that won't be covered by various integration tests.
    """

    def test_no_args(self):
        """Test that running the parser without arguments raises an error."""
        with pytest.raises(SystemExit) as e:
            main([])
        assert str(e.value) == "1"

    def test_version_output(self, capsys):
        """Test that the version output is printed properly."""
        with pytest.raises(SystemExit) as e:
            main(['-V'])
        assert str(e.value) == '0'
        captured = capsys.readouterr()
        loc = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assert captured.out == f"CanSen {__version__} from {loc} ()\n"

        with pytest.raises(SystemExit) as e:
            main(['--version'])
        assert str(e.value) == '0'
        captured = capsys.readouterr()
        loc = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assert captured.out == f"CanSen {__version__} from {loc} ()\n"

    def test_convert_mech_w_thermo(self, datafiles):
        """Test conversion when thermo is in the input file.

        This case is the single argument to ``convert_mech``.
        """
        input_file = os.path.join(datafiles, 'test-w-thermo.inp')
        blessed_file = os.path.join(datafiles, 'test-blessed.cti')
        os.chdir(datafiles)
        output_file = 'test-w-thermo.cti'
        output_file = os.path.join(datafiles, output_file)
        with pytest.raises(SystemExit) as e:
            main(['--convert', '--chem', input_file])
        assert str(e.value) == '0'
        with open(output_file, 'r') as o_file, open(blessed_file, 'r') as b_file:
            assert o_file.read() == b_file.read()

    def test_convert_mech_wo_thermo(self, datafiles):
        """Test conversion when thermo is in a separate file.

        This is the two argument case for ``convert_mech``.
        """
        input_file = os.path.join(datafiles, 'test-wo-thermo.inp')
        dat_file = os.path.join(datafiles, 'test-wo-thermo.dat')
        blessed_file = os.path.join(datafiles, 'test-blessed.cti')
        os.chdir(datafiles)
        output_file = 'test-wo-thermo.cti'
        output_file = os.path.join(datafiles, output_file)
        with pytest.raises(SystemExit) as e:
            main(['--convert', '--chem', input_file, '--thermo', dat_file])
        assert str(e.value) == '0'
        with open(output_file, 'r') as o_file, open(blessed_file, 'r') as b_file:
            assert o_file.read() == b_file.read()

    def test_convert_mech_missing_chem_file(self):
        """Test that a missing mechanism file raises a FileNotFoundError."""
        input_file = 'this-file-does-not-exist.inp'
        with pytest.raises(FileNotFoundError) as e:
            main(['--convert', '--chem', input_file])

        assert str(e.value) == 'The chemistry file "{}" could not be found'.format(input_file)

    def test_convert_mech_missing_thermo_file(self, datafiles):
        """Test that a missing mechanism file raises a FileNotFoundError."""
        input_file = os.path.join(datafiles, 'test-wo-thermo.inp')
        dat_file = 'this-file-does-not-exist.dat'
        os.chdir(datafiles)
        with pytest.raises(FileNotFoundError) as e:
            main(['--convert', '--chem', input_file, '--thermo', dat_file])

        assert str(e.value) == 'The thermodynamic database "{}" could not be found'.format(dat_file)  # noqa: E501
