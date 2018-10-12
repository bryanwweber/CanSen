"""Test the CanSen utilities."""

import os
import shutil

import pytest
import cantera as ct

from ..utils import convert_mech, equivalence_ratio
from ..exceptions import CanSenError


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
    def test_equivalence_ratio_simple(phi):
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
    def test_equivalence_ratio_fuel_oxid_gt_one(phi):
        """Test the equivalence ratio function when fuel and oxidizers sum to more than 1.0."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 1.0, 'C2H6': 1.0}
        oxidizer = {'O2': 1.0, 'N2': 3.76}
        complete_prod = ['CO2', 'H2O', 'N2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_fuel_oxid_lt_one(phi):
        """Test the equivalence ratio function when fuel and oxidizers sum to more than 1.0."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CH4': 0.25, 'C2H6': 0.25}
        oxidizer = {'O2': 0.1, 'N2': 0.7}
        complete_prod = ['CO2', 'H2O', 'N2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_no_C(phi):
        """Test the equivalence ratio when there's no C in the fuel."""
        gas = ct.Solution('gri30.xml')
        fuel = {'H2': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['H2O']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_no_H(phi):
        """Test the equivalence ratio when there's no H in the fuel."""
        gas = ct.Solution('gri30.xml')
        fuel = {'CO': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2']
        reactants = equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})
        gas.set_equivalence_ratio(phi, fuel, oxidizer)
        assert reactants == pytest.approx(gas.mole_fraction_dict())

    @pytest.mark.parametrize('phi', [0.5, 1.0, 1.1, 3.5])
    def test_equivalence_ratio_addl_species(phi):
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
    def test_equivalence_ratio_o_in_fuel(phi):
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

    def test_eq_ratio_incomplete_prods():
        """Test that specifying incompletely oxidized produces raises a warning."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO', 'H2O']
        with pytest.warns(Warning, match="One or more products of incomplete combustion were"):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})

    def test_eq_ratio_raise_missing_elem_cprod():
        """Test that missing elements in the complete products raises an exception."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0, 'N2': 1.0}
        complete_prod = ['CO2', 'H2O']  # Missing N
        with pytest.raises(CanSenError, match=r'Must specify all elements in the fuel \+ oxidizer'):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, {})

    def test_eq_ratio_raise_addl_too_big():
        """Test that additional species that sum to greater than 1.0 raises an exception."""
        gas = ct.Solution('gri30.xml')
        phi = 1.0
        fuel = {'CH4': 1.0}
        oxidizer = {'O2': 1.0}
        complete_prod = ['CO2', 'H2O']
        additional_species = {'AR': 1.5}
        with pytest.raises(CanSenError, match='Additional species must sum to less than 1'):
            equivalence_ratio(gas, phi, fuel, oxidizer, complete_prod, additional_species)
