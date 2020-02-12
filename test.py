import pint

import pytest


D_ENERGY = {'[length]': 2.0, '[mass]': 1.0, '[time]': -2.0}

# Expected units: each tuple is (unit string, dimensionality, True if defined
# by this package)
PARAMS = [
    ('toe', D_ENERGY, False),
    ('tce', D_ENERGY, True),
    ('GW a', D_ENERGY, False),
]


# Fixtures and utilities for tests
@pytest.fixture(scope='session')
def empty_registry():
    yield pint.UnitRegistry()


@pytest.fixture(scope='session')
def registry():
    reg = pint.UnitRegistry()
    reg.load_definitions('definitions.txt')
    yield reg


def idfn(val):
    return val if isinstance(val, str) else ''


@pytest.mark.parametrize('unit_name, dims, new_def', PARAMS, ids=idfn)
def test_units(empty_registry, registry, unit_name, dims, new_def):
    if new_def:
        # Units defined in dimensions.txt are not recognized by base pint
        with pytest.raises(pint.UndefinedUnitError):
            empty_registry('1 ' + unit_name)

    # Units can be parsed and have the correct dimensionality
    assert registry('1 ' + unit_name).dimensionality == dims
