from pathlib import Path

import pint
from pint.formatting import format_unit
from pint.util import to_units_container

from . import emissions

__all__ = [
    "convert_gwp",
    "format_mass",
    "registry",
]


# Package registry using definitions.txt
registry = pint.UnitRegistry()
registry.load_definitions(str(Path(__file__).parent / "data" / "definitions.txt"))


def convert_gwp(metric, quantity, *species):
    """Convert *quantity* between GHG *species* with a GWP *metric*.

    Parameters
    ----------
    metric : 'SARGWP100' or 'AR4GWP100' or 'AR5GWP100' or None
        Metric conversion factors to use. May be :obj:`None` if the input and
        output species are the same.
    quantity : str or pint.Quantity or tuple
        Quantity to convert. If a tuple of (magnitude, unit), these are passed
        as arguments to :class:`pint.Quantity`.
    species : sequence of str, length 1 or 2
        Output, or (input, output) species symbols, e.g. ('CH4', 'CO2') to
        convert mass of CH₄ to GWP-equivalent mass of CO₂. If only the output
        species is provided, *quantity* must contain the symbol of the input
        species in some location, e.g. '1.0 tonne CH4 / year'.

    Returns
    -------
    pint.Quantity
        `quantity` converted from the input to output species.
    """
    # Handle *species*: either (in, out) or only out
    try:
        species_in, species_out = species
    except ValueError:
        if len(species) != 1:
            raise ValueError("Must provide (from, to) or (to,) species")
        species_in, species_out = None, species[0]

    # Split *quantity* if it is a tuple. After this step:
    # - *mag* is the magnitude, or None.
    # - *expr* is a string expression for either just the units, or the entire
    #   quantity, including magnitude, as a str or pint.Quantity.
    mag, expr = quantity if isinstance(quantity, tuple) else (None, quantity)

    # If species_in wasn't provided, then *expr* must contain it
    if not species_in:
        # Extract it using the regex, then re-assemble the expression for the
        # units or whole quantity
        q0, species_in, q1 = emissions.pattern.split(expr, maxsplit=1)
        expr = q0 + q1

    # *metric* can only be None if the input and output species symbols are
    # identical or equivalent
    if metric is None:
        if species_in == species_out or any(
            {species_in, species_out} <= g for g in emissions.EQUIV
        ):
            metric = "AR5GWP100"
        elif species_in in species_out:
            # Eg. 'CO2' in 'CO2 / a'. This is both a DimensionalityError and a
            # ValueError (no metric); raise the former for pyam compat
            raise pint.DimensionalityError(species_in, species_out)
        else:
            msg = f"Must provide GWP metric for ({species_in}, {species_out})"
            raise ValueError(msg)

    # Ensure a pint.Quantity object:
    # - If *quantity* was a tuple, use the 2-arg constructor.
    # - If a str, use the 1-arg form to parse it.
    # - If already a pint.Quantity, this is a no-op.
    args = (expr,) if mag is None else (mag, expr)
    quantity = registry.Quantity(*args)

    # Construct intermediate units with the same dimensionality as *quantity*,
    # except '[mass]' replaced with the dummy unit '_gwp'
    dummy = quantity.units / registry.Unit("tonne / _gwp")

    # Convert to dummy units using 'a' for the input species; then back to the
    # input units using 'a' for the output species.
    return quantity.to(dummy, metric, _a=f"a_{species_in}").to(
        quantity.units, metric, _a=f"a_{species_out}"
    )


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
    method = registry._get_symbol if "~" in spec else lambda k: k
    # Collect the pieces of the unit expression
    units = [[method(key), value] for key, value in obj._units.items()]

    # Index of the mass component
    mass_index = list(obj.dimensionality.keys()).index("[mass]")
    # Append the information to the mass component
    units[mass_index][0] += f" {info}"

    # Hand off to pint's formatting
    return format_unit(to_units_container(dict(units), registry=registry), spec)
