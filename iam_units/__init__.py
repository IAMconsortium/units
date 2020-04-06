from pathlib import Path

import pint

from . import emissions


__all__ = ['SPECIES', 'convert_gwp', 'registry']


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
    quantity : str or pint.Quantity
        Quantity to convert.
    species : sequence of str, length 1 or 2
        Output, or input and output emissions species, e.g. ('CH4', 'CO2') to
        convert mass of CH₄ to GWP-equivalent mass of CO₂. If only the output
        species is provided, *quantity* must contain the name of the input
        species in some location, e.g. 'tonne CH4'.

    Returns
    -------
    pint.Quantity
        `quantity` converted from the input to output species.
    """
    try:
        species_in, species_out = species
    except ValueError:
        if len(species) != 1:
            raise ValueError('Must provide (from, to) or (to,) species')

        # Only output emissions species provided
        species_out = species[0]

        # *quantity* contains the input species; extract it
        q0, species_in, q1 = emissions.pattern.split(quantity, maxsplit=1)

        # Re-assemble the quantity
        quantity = q0 + q1

    # Maybe convert a string to Quantity; if it's already Quantity, a no-op
    quantity = registry.Quantity(quantity)

    # Units with the same dimensionality as *quantity*, except '[mass]'
    # replaced with the dummy units '[_GWP]'
    dummy = quantity.units / registry.Unit('tonne / _gwp')

    # Convert to GWP dummy units using 'a' for the input species; then back to
    # the input units using 'a' for the output species.
    return quantity.to(dummy, metric, _a=f'a_{species_in}') \
                   .to(quantity.units, metric, _a=f'a_{species_out}')
