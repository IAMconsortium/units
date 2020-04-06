from pathlib import Path

import pandas as pd
import sys


# Base path for package code
BASE_PATH = Path(__file__).parent

# Base path for package data
DATA_PATH = BASE_PATH / 'data'


# Format strings for emissions()
_EMI_HEADER = """# This file was generated using:
#    python -m iam_units.update emissions
# DO NOT ALTER THIS FILE MANUALLY!
"""

_EMI_DATA = f"""{_EMI_HEADER}
@context(_a=NaN) {{metric}}
    [mass] -> [_GWP]: value * (_a * _gwp / kg)
    [_GWP] -> [mass]: value / (_a * _gwp / kg)
    [mass] / [time] -> [_GWP] / [time]: value * (_a * _gwp / kg)
    [_GWP] / [time] -> [mass] / [time]: value / (_a * _gwp / kg)

    {{defs}}
@end
"""

_EMI_CODE = f"""{_EMI_HEADER}
import re

SPECIES = [
    '{{symbols}}',
    ]

pattern = re.compile('(?<=[ -])(' + '|'.join(SPECIES) + ')(?=[ -/]?)')
"""


def emissions():
    """Update emissions definitions files."""
    data_path = DATA_PATH / 'emissions'

    # - Load data.
    # - Sort by symbol.
    # - Convert to long form with 'metric' and 'value' columns.
    # - Drop missing values.
    data = pd.read_csv(data_path / 'metric_conversions.csv') \
             .sort_values('Symbol') \
             .melt(id_vars=['Species', 'Symbol'], var_name='metric') \
             .dropna(subset=['value'])

    # Write the file containing the species defs
    symbols = sorted(data['Symbol'].unique())
    with open(data_path / 'species.txt', 'w') as f:
        f.write(_EMI_HEADER + '\n')
        [f.write(f'a_{symbol} = NaN\n') for symbol in symbols]

    # Write a regular expression containing the species names
    symbols = "',\n    '".join(symbols)
    (BASE_PATH / 'emissions.py').write_text(_EMI_CODE.format(**locals()))

    # Write one file containing a context for each metric
    for metric, _data in data.groupby('metric'):
        # Conversion factor definitions
        defs = []
        for _, row in _data.iterrows():
            defs.append(f'a_{row.Symbol} = {row.value}')

        # Join to a single string
        defs = '\n    '.join(defs)

        # Write to file
        (data_path / f'{metric}.txt').write_text(
            # Format the template with the definitions
            _EMI_DATA.format(**locals())
        )


if __name__ == '__main__':
    # Invoked using 'python -m iam_units.update'
    # For each additional argument, call the function of the same name
    for module in sys.argv[1:]:
        locals()[module]()
