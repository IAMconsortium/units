from pathlib import Path

import pint
from pint.formatting import format_unit
from pint.util import to_units_container

from . import emissions


__all__ = [
    'SPECIES',
    'convert_gwp',
    'registry',
]


# Package registry using definitions.txt
registry = pint.UnitRegistry()
registry.load_definitions(
    str(Path(__file__).parent / 'data' / 'definitions.txt'))


def convert_gwp(metric, quantity, *species):
    """Convert *quantity* between emissions *species* with a GWP *metric*.

    Parameters
    ----------
    metric : 'SARGWP100' or 'AR4GWP100' or 'AR5GWP100'
        Metric conversion factors to use.
    quantity : str or pint.Quantity or tuple
        Quantity to convert. If a tuple, the arguments are passed to the
        :class:`pint.Quantity` constructor.
    species : sequence of str, length 1 or 2
        Output, or input and output emissions species, e.g. ('CH4', 'CO2') to
        convert mass of CH₄ to GWP-equivalent mass of CO₂. If only the output
        species is provided, *quantity* must contain the name of the input
        species in some location, e.g. 'tonne CH4 / year'.

    Returns
    -------
    pint.Quantity
        `quantity` converted from the input to output species.
    """
    # Handle *species*
    try:
        # Split a 2-tuple
        species_in, species_out = species
    except ValueError:
        if len(species) != 1:
            raise ValueError('Must provide (from, to) or (to,) species')
        # Only output emissions species provided
        species_in, species_out = None, species[0]

    # Split *quantity* if it is a tuple:
    # - *mag* is the magnitude, or None.
    # - *expr* is a string expression for either just the units, or the entire
    #   quantity including magnitude.
    mag, expr = quantity if isinstance(quantity, tuple) else (None, quantity)

    if not species_in:
        # *expr* must contain the input species; extract it using the regex
        q0, species_in, q1 = emissions.pattern.split(expr, maxsplit=1)
        # Re-assemble the expression for the units or whole quantity
        expr = q0 + q1

    # Ensure a pint.Quantity object:
    # - If tuple input was given, use the 2-arg constructor.
    # - If not, use the 1-arg form to convert a string.
    # - If the input was already a Quantity, this is a no-op.
    args = (expr,) if mag is None else (mag, expr)
    quantity = registry.Quantity(*args)

    # Intermediate units with the same dimensionality as *quantity*, except
    # '[mass]' replaced with the dummy unit '_gwp'
    dummy = quantity.units / registry.Unit('tonne / _gwp')

    # Convert to GWP dummy units using 'a' for the input species; then back to
    # the input units using 'a' for the output species.
    return quantity.to(dummy, metric, _a=f'a_{species_in}') \
                   .to(quantity.units, metric, _a=f'a_{species_out}')


def format_mass(obj, info, spec=None):
    """Format the units of *obj* with *info* inserted after its mass unit.

    Parameters
    ----------
    obj : pint.Quantity or pint.Unit
    info : str
        Any information, e.g. the symbol of a GHG species.
    spec : str, optional
        Pint formatting specifier such as ':H' (HTML format), ':~' (compact
        format with symbols), etc.
    """
    spec = spec or obj.default_format

    try:
        # Use only the units of a Quantity object
        obj = obj.units
    except AttributeError:
        pass  # Already a Unit object

    # Use the symbol for a ':~' spec
    method = registry._get_symbol if '~' in spec else lambda k: k
    # Collect the pieces of the unit expression
    units = [[method(key), value] for key, value in obj._units.items()]

    # Index of the mass component
    mass_index = list(obj.dimensionality.keys()).index('[mass]')
    # Append the information to the mass component
    units[mass_index][0] += f' {info}'

    # Hand off to pint's formatting
    return format_unit(to_units_container(dict(units), registry=registry),
                       spec)
