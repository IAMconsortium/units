import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
import pint
from pint.util import UnitsContainer
import pytest

from iam_units import convert_gwp, format_mass, registry


DEFAULTS = pint.get_application_registry()

# Parameters for test_units(), tuple of:
# 1. A literal string to be parsed as a unit.
# 2. Expected dimensionality of the parsed unit.
# 3. True if the units are not in pint's default_en.txt, but are defined in
#    definitions.txt.
energy = UnitsContainer({'[energy]': 1})
PARAMS = [
    ('toe', energy, False),
    ('tce', energy, True),
    ('GW a', energy, False),
    ('kWa', energy, True),
    ('EUR_2005', UnitsContainer({'[currency]': 1}), True),
]


@pytest.mark.parametrize('unit_str, dim, new_def', PARAMS,
                         ids=lambda v: v if isinstance(v, str) else '')
def test_units(unit_str, dim, new_def):
    if new_def:
        # Units defined in dimensions.txt are not recognized by base pint
        with pytest.raises(pint.UndefinedUnitError):
            DEFAULTS('1 ' + unit_str)

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


def test_emissions_internal():
    # Dummy units can be created
    registry('0.5 _gwp').dimensionality == {'[_GWP]': 1.0}

    # Context can be enabled
    with registry.context('AR5GWP100', __a=1.0) as r:
        # Context-specific values are activated
        assert r('a_CH4 * a_N2O').to_base_units().magnitude == 28 * 265

        # Context-specific conversion rules are available
        r('0.5 t').to('_gwp')


@pytest.mark.parametrize('units', [
    't {}',               # Mass
    'Mt {} / a',          # Mass rate
    'kt {} / (ha * yr)',  # Mass flux
])
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
    arr = np.array([1.0, 2.5, 0.1])
    qty = (arr, units.format('CH4'))
    expected = arr * expected_value

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


@pytest.mark.parametrize('units_in, species_str, spec, output', [
    ('Mt', 'CO2', None, 'megametric_ton CO2'),
    ('kg / year', 'CO2', None, 'kilogram CO2 / year'),
    # Compact spec: no spaces around '/'
    ('kg / year', 'CO2', ':C', 'kilogram CO2/year'),
    # Abbreviated/symbol spec AND Unicode subscript
    ('Mt', 'CO₂', ':~', 'Mt CO₂'),
    ('kg / year', 'CO₂', ':~', 'kg CO₂ / a'),
    # Abitrary string, e.g. including a hint at the metric name
    ('gram / a', 'CO₂-e (AR4)', ':~', 'g CO₂-e (AR4) / a'),
])
def test_format_mass(units_in, species_str, spec, output):
    # Quantity object can be formatted
    qty = registry.Quantity(3.5, units_in)
    assert format_mass(qty, species_str, spec) == output

    # Unit object can be formatted
    qty = registry.Unit(units_in)
    assert format_mass(qty, species_str, spec) == output
