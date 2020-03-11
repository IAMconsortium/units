# Definitions of greenhouse gas emissions 

This module defines a number of greenhouse gases as pint base units and
their conversion to CO2-equivalent using specific <IPCC report>-GWP<y> metrics
implemented as pint contexts.

## Source of CO-equivalent conversion factors

The conversion factors to CO2-equivalent are extracted from the file `metric_conversions.csv`,
which was created by [lewisjared](https://github.com/lewisjared) and licensed under BSD-3.
See [lewisjared/scmdata v0.4](https://github.com/lewisjared/scmdata/tree/v0.4.0/src/scmdata/data)
for the original file.

The conversion factors were removed from the csv file for simplicity; the values were collected
from https://www.ghgprotocol.org/sites/default/files/ghgp/Global-Warming-Potential-Values%20%28Feb%2016%202016%29_1.pdf.
