import csv
from pathlib import Path

import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
import pint
from pint.util import UnitsContainer
import pytest

from iam_units import convert_gwp, registry


DATA_PATH = Path(__file__).parent / 'data'
defaults = pint.get_application_registry()


# Read units to check from file
PARAMS = []
with open(DATA_PATH / 'checks.csv') as f:
    for row in csv.reader(f, skipinitialspace=True, quoting=csv.QUOTE_MINIMAL):
        try:
            unit_str, dims, new_def = row
        except ValueError:
            continue  # Comment or malformed row; skip
        else:
            if unit_str.startswith('#'):
                continue  # Comment; skip

        # Convert second column to a dimensionality object
        dims = {dims: 1} if dims.startswith('[') else eval(dims)
        dims = UnitsContainer(dims)

        # Convert third column to boolean
        new_def = len(new_def) > 0

        # Store
        PARAMS.append((unit_str, dims, new_def))


@pytest.mark.parametrize('unit_str, dim, new_def', PARAMS,
                         ids=lambda v: v if isinstance(v, str) else '')
def test_units(unit_str, dim, new_def):
    if new_def:
        # Units defined in dimensions.txt are not recognized by base pint
        with pytest.raises(pint.UndefinedUnitError):
            defaults('1 ' + unit_str)

    # Physical quantity of units is recognized
    dim = registry.get_dimensionality(dim)

    # Units can be parsed and have the correct dimensionality
    assert registry('1 ' + unit_str).dimensionality == dim


def test_orders_of_magnitude():
    # The registry recognizes units prefixed by an order of magnitude
    assert registry('1.2 billion EUR').to('million EUR').magnitude == 1.2e3


def test_kt():
    # The registry should correctly interpret `kt` as a weight (not velocity)
    assert str(registry('1000 kt').to('Mt')) == '1.0 megametric_ton'

    # A default UnitRegistry should interpret `kt` as velocity
    with pytest.raises(pint.DimensionalityError):
        pint.UnitRegistry()('kt').to('Mt')


# 1 tonne of CH4 converted to CO2 equivalent by different metrics
EMI_DATA = [
    ('AR5GWP100', 28),
    ('AR4GWP100', 25),
    ('SARGWP100', 21)
]


@pytest.mark.parametrize('context, value', EMI_DATA)
def test_units_emissions(context, value):
    # The registry shouldn't convert with specifying a valid context
    with pytest.raises(pint.DimensionalityError):
        registry['ch4'].to('co2')

    context = f'gwp_{context}'

    # test commonly used derived units related to emissions
    formats = ['{}', 'Mt {}', 'Mt {} / yr', '{} / yr']

    for f in formats:
        # assert that conversion to CO2 works
        assert registry[f.format('ch4')].to(f.format('co2'),
                                            context).magnitude == value

        # assert that conversion to CO2-equivalent works
        assert registry[f.format('ch4')].to(f.format('co2e'),
                                            context).magnitude == value


def test_emissions_internal():
    # Dummy units can be created
    registry('0.5 _gwp').dimensionality == {'[_GWP]': 1.0}

    # Context can be enabled
    with registry.context('AR5GWP100', __a=1.0) as r:
        # Context-specific values are activated
        assert r('a_CH4 * a_N2O').to_base_units().magnitude == 28 * 265

        # Context-specific conversion rules are available
        r('0.5 t').to('_gwp')


@pytest.mark.parametrize('units', ['t {}', 'Mt {}', 'Mt {} / yr'])
@pytest.mark.parametrize('metric, expected_value', EMI_DATA)
@pytest.mark.parametrize('species_out', ['CO2', 'CO2e'])
def test_convert_gwp(units, metric, expected_value, species_out):
    # Bare masses can be converted
    qty = registry.Quantity(1.0, units.format(''))
    expected = registry(f'{expected_value} {units}')
    assert convert_gwp(metric, qty, 'CH4', species_out) == expected

    # '[mass] [speciesname] (/ [time])' can be converted; the input species is
    # extracted from the *qty* argument
    qty = f'1.0 ' + units.format('CH4')
    expected = registry(f'{expected_value} {units}')
    assert convert_gwp(metric, qty, species_out) == expected

    # Tuple of (vector magnitude, unit expression) can be converted where the
    # the unit expression contains the input species name
    arr = [1.0, 2.5, 0.1]
    qty = (arr, units.format('CH4'))
    expected = np.array(arr) * expected_value

    # Conversion works
    result = convert_gwp(metric, qty, species_out)
    # Magnitudes are as expected
    assert_array_almost_equal(result.magnitude, expected)


def test_convert_gwp_carbon():
    # CO2 can be converted to C
    qty = (44. / 12, 'tonne CO2')
    result = convert_gwp('AR5GWP100', qty, 'C')
    assert result.units == registry('tonne')
    assert_almost_equal(result.magnitude, 1.0)

    # C can be converted to CO2
    qty = (1, 'tonne C')
    expected = registry.Quantity(44. / 12, 'tonne')
    assert convert_gwp('AR5GWP100', qty, 'CO2e') == expected
