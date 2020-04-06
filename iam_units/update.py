from pathlib import Path

import pandas as pd
import sys


DATA_PATH = Path(__file__).parent / 'data'


def emissions():
    # list of contexts
    contexts = ['SARGWP100', 'AR4GWP100', 'AR5GWP100']

    # add explicit conversion mappings for derived units (with time & mass)
    formatters = [
        "[{}]",
        "[mass] * [{}]",
        "[mass] * [{}] / [time]",
        "[{}] / [time]",
    ]

    # load data from table, drop all rows that don't have defined species
    # the species must match the base unit in `emissions.txt`
    data_path = DATA_PATH / 'emissions'
    data = pd.read_csv(data_path / 'metric_conversions.csv') \
             .dropna(subset=['Species'])

    for context in contexts:
        # check that context exists as column in the table
        if context not in data.columns:
            raise ValueError(f'no column `{context}` in data file')

        # downselect to required columns, drop na
        _data = data[['Species', 'Symbol', context]].dropna()

        # open file and write header
        gwp = open(data_path / f'gwp_{context}.txt', 'w')

        gwp.write('# This file was generated using python -m iam_units.update '
                  'emissions\n')
        gwp.write('# DO NOT ALTER THIS FILE MANUALLY!\n\n')
        gwp.write(f'@context gwp_{context}\n')

        lines = '\n'.join([
            '    {f_gas} -> {f_co2}: value * {value} * CO2 / {symbol}',
            '    {f_co2} -> {f_gas}: value / {value} * {symbol} / CO2',
            '',
        ])

        for i, (species, symbol, value) in _data.iterrows():
            gwp.write(f'\n# {species} - {symbol}\n\n')
            for f in formatters:
                f_gas, f_co2 = f.format(species), f.format('carbon_dioxide')
                gwp.write(lines.format(**locals()))

        gwp.write('\n@end\n')
        gwp.close()


if __name__ == '__main__':
    # Invoked using 'python -m iam_units.update'
    # For each additional argument, call the function of the same name
    for module in sys.argv[1:]:
        locals()[module]()
