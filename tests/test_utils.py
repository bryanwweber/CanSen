"""Test the CanSen utilities."""

import pytest
import cantera as ct

from cansen.utils import equivalence_ratio
from cansen.exceptions import CanSenError


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
