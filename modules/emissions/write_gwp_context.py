import pandas as pd

context = 'SARGWP100'

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
    gwp.write(
        f'    [{species}] -> [carbon_dioxide]: value * {value} * CO2 / {symbol} \n')
    gwp.write(
        f'    [{species}] * [mass] -> [carbon_dioxide] * [mass]: value * {value} * CO2 / {symbol} \n')
    gwp.write(
        f'    [carbon_dioxide] -> [{species}]: value / {value} / CO2 * ch4 \n')
    gwp.write(
        f'    [carbon_dioxide] * [mass] -> [{species}] * [mass]: value / {value} / CO2 * {symbol} \n \n')

gwp.write('@end')
gwp.close()