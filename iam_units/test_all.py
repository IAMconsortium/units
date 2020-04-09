import csv
from pathlib import Path

import pint
from pint.util import UnitsContainer
import pytest

from iam_units import registry


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


@pytest.mark.parametrize('context, value',
                         [('AR5GWP100', 28),
                          ('AR4GWP100', 25),
                          ('SARGWP100', 21)])
def test_units_emissions(context, value):
    # The registry shouldn't convert with specifying a valid context
    with pytest.raises(pint.DimensionalityError):
        registry['ch4'].to('co2')

    context = f'gwp_{context}'

    # test commonly used erived units related to emissions
    formats = ['{}', 'Mt {}', 'Mt {} / yr', '{} / yr']

    for f in formats:
        # assert that conversion to CO2 works
        assert registry[f.format('ch4')].to(f.format('co2'),
                                            context).magnitude == value

        # assert that conversion to CO2-equivalent works
        assert registry[f.format('ch4')].to(f.format('co2e'),
                                            context).magnitude == value
