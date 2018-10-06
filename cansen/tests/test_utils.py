"""Test the CanSen utilities."""

import os
import shutil

import pytest
import cantera as ct

from ..utils import convert_mech, equivalence_ratio, cli_parser
from ..exceptions import CanSenError
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


class TestEquivalenceRatio():

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_simple(self, phi):
        """Test the equivalence ratio function gives appropriate results.

        Compare a simple case to the results returned from the Cantera
        set_equivalence_ratio function.
        """
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2', 'H2O']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_fuel_oxid_gt_one(self, phi):
        """Test the equivalence ratio function when fuel and oxidizers sum to more than 1.0."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 1.0, 'C2H6': 1.0}
        oxidizer = {'O2': 1.0, 'N2': 3.76}
        complete_prod = ['CO2', 'H2O', 'N2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_fuel_oxid_lt_one(self, phi):
        """Test the equivalence ratio function when fuel and oxidizers sum to more than 1.0."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 0.25, 'C2H6': 0.25}
        oxidizer = {'O2': 0.1, 'N2': 0.7}
        complete_prod = ['CO2', 'H2O', 'N2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_no_C(self, phi):
        """Test the equivalence ratio when there's no C in the fuel."""
        gas = ct.Solution('gri30.xml')
        fuel = {'H2': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['H2O']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_no_H(self, phi):
        """Test the equivalence ratio when there's no H in the fuel."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CO': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_addl_species(self, phi):
        """Test the equivalence ratio when additional species are specified."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        X_AR = 0.96
        additional_species = {'AR': X_AR}
        complete_prod = ['CO2', 'H2O']
        remain = 1.0 - X_AR
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        known = {sp: x*remain for sp, x in gas.mole_fraction_dict().items()}
        known['AR'] = X_AR

        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, additional_species)
        assert reactants == pytest.approx(known)

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_o_in_fuel(self, phi):
        """Test the equivalence ratio function gives appropriate results.

        Compare a simple case to the results returned from the Cantera
        set_equivalence_ratio function.
        """
        gas = ct.Solution('gri30.xml')
        fuel = {'CH2O': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2', 'H2O']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    def test_eq_ratio_incomplete_prods(self):
        """Test that specifying incompletely oxidized produces raises a warning."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO', 'H2O']
        with pytest.warns(Warning, match="One or more products of incomplete combustion were"):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})

    def test_eq_ratio_raise_missing_elem_cprod(self):
        """Test that missing elements in the complete products raises an exception."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0, 'N2': 1.0}
        complete_prod = ['CO2', 'H2O']  # Missing N
        with pytest.raises(CanSenError, match=r'Must specify all elements in the fuel \+ oxidizer'):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})

    def test_eq_ratio_raise_addl_too_big(self):
        """Test that additional species that sum to greater than 1.0 raises an exception."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2', 'H2O']
        additional_species = {'AR': 1.5}
        with pytest.raises(CanSenError, match='Additional species must sum to less than 1'):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, additional_species)


class TestCliParser():
    """Tests of the CLI parser.

    Not actually sure any of these are necessary, they would probably be
    covered by some integration tests.
    """

    def test_no_args(self):
        """Test that running the parser without arguments raises an error."""
        with pytest.raises(SystemExit) as e:
            cli_parser([])
        assert str(e.value) == "1"

    def test_version_output(self, capsys):
        """Test that the version output is printed properly."""
        with pytest.raises(SystemExit) as e:
            cli_parser(['-V'])
        assert str(e.value) == '0'
        captured = capsys.readouterr()
        loc = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assert captured.out == f"CanSen {__version__} from {loc} ()\n"

        with pytest.raises(SystemExit) as e:
            cli_parser(['--version'])
        assert str(e.value) == '0'
        captured = capsys.readouterr()
        loc = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assert captured.out == f"CanSen {__version__} from {loc} ()\n"

    def test_no_input_no_convert(self, capsys):
        """Test that not specifying an input file and not converting raises an error."""
        with pytest.raises(SystemExit) as e:
            cli_parser(['--thermo', 'another argument'])
        assert str(e.value) == "1"
        captured = capsys.readouterr()
        assert captured.out == 'Error: The input file must be specified\n'

    def test_input_file_doesnt_exist(self, capsys):
        """Test that specifying an input file that doesn't exist raises an error."""
        with pytest.raises(SystemExit) as e:
            cli_parser(['--input', 'this-file-does-not-exist'])
        assert str(e.value) == "1"
        captured = capsys.readouterr()
        assert captured.out == ('Error: The specified input file '
                                '"this-file-does-not-exist" does not exist\n')

    def test_input_file_when_converting(self):
        """Test that when specifying the convert function, the input_filename is None.

        Is this just testing an implementation detail? Does it matter that the filename is None?
        Pretty sure this test won't be necessary when actually testing the --convert option.
        """
        filenames, _, _, _ = cli_parser(['--convert', '-c', os.path.abspath(__file__)])
        assert filenames['input_filename'] is None

    def test_input_file_exists(self):
        """Test that a good input file gives appropriate output.

        Test that the input filename is stored in the dictionary that is the first element
        of the tuple returned by the cli_parser. Pretty sure this is just testing an
        implementation detail, probably don't need it.
        """
        filenames, _, _, _ = cli_parser(['-i', os.path.abspath(__file__), '-c', os.path.abspath(__file__)])
        assert filenames['input_filename'] == os.path.abspath(__file__)
