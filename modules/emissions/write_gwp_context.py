import pandas as pd

context = 'SARGWP100'

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

# check that context exists as column in the table
if context not in data.columns:
    raise ValueError(f'no column `{context}` in data file')

# downselect to required columns, drop na
data = data[['Species', 'Symbol', context]].dropna()

# write to file
gwp = open(f'gwp_{context}.txt', 'w')
gwp.writelines(f'@context gwp_{context} \n \n')

for i, (species, symbol, value) in data.iterrows():
    for f in formatters:
        f_species = f.format(species)
        f_co2 = f.format('carbon_dioxide')
        gwp.write(
            f'    {f_species} -> {f_co2}: value * {value} * CO2 / {symbol} \n')
        gwp.write(
            f'    {f_co2} -> {f_species}: value / {value} / CO2 * {symbol} \n')

gwp.write('@end')
gwp.close()