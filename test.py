import csv
from pathlib import Path

import pint
from pint.util import UnitsContainer

import pytest


defaults = pint.get_application_registry()


# Read units to check from file
PARAMS = []
with open(Path(__file__).with_name('checks.csv')) as f:
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
        dims = defaults.get_dimensionality(UnitsContainer(dims))

        # Convert third column to boolean
        new_def = len(new_def) > 0

        # Store
        PARAMS.append((unit_str, dims, new_def))


@pytest.fixture(scope='session')
def registry():
    """UnitRegistry including definitions from definitions.txt."""
    reg = pint.UnitRegistry()
    reg.load_definitions(str(Path(__file__).with_name('definitions.txt')))
    yield reg


@pytest.mark.parametrize('unit_str, dim, new_def', PARAMS,
                         ids=lambda v: v if isinstance(v, str) else '')
def test_units(registry, unit_str, dim, new_def):
    if new_def:
        # Units defined in dimensions.txt are not recognized by base pint
        with pytest.raises(pint.UndefinedUnitError):
            defaults('1 ' + unit_str)

    # Units can be parsed and have the correct dimensionality
    assert registry('1 ' + unit_str).dimensionality == dim
