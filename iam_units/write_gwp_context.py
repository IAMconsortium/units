import pandas as pd

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
data = (
    pd.read_csv('metric_conversions.csv')
      .dropna(subset=['Species'])
)


for context in contexts:
    # check that context exists as column in the table
    if context not in data.columns:
        raise ValueError(f'no column `{context}` in data file')

    # downselect to required columns, drop na
    _data = data[['Species', 'Symbol', context]].dropna()

    # open file and write header
    gwp = open(f'gwp_{context}.txt', 'w')

    gwp.writelines(f'# This file was created using the script `{__file__}`\n')
    gwp.write('# DO NOT ALTER THIS FILE MANUALLY!\n\n')
    gwp.write(f'@context gwp_{context}\n')

    for i, (species, symbol, value) in _data.iterrows():
        gwp.write('\n')
        gwp.write(f'# {species} - {symbol}\n\n')
        for f in formatters:
            f_gas, f_co2 = f.format(species), f.format('carbon_dioxide')
            gwp.write(
                f'    {f_gas} -> {f_co2}: value * {value} * CO2 / {symbol}\n')
            gwp.write(
                f'    {f_co2} -> {f_gas}: value / {value} * {symbol} / CO2\n')

    gwp.write('\n')
    gwp.write('@end')
    gwp.close()
