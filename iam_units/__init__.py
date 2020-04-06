from pathlib import Path

import pint


__all__ = ['convert_gwp', 'registry']


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
    quantity : pint.Quantity
        Quantity to convert.
    species : (str, str)
        Input and output emissions species, e.g. ('CH4', 'CO2') to convert
        mass of CH₄ to GWP-equivalent mass of CO₂.

    Returns
    -------
    pint.Quantity
        `quantity` converted from `species[0]` to `species[1]`.
    """
    if len(species) != 2:
        raise ValueError('Must provide (from, to) species')

    # Convert
    return quantity.to('_gwp', metric, _a=f'a_{species[0]}') \
                   .to(quantity.units, metric, _a=f'a_{species[1]}')
