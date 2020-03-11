# Definitions of greenhouse gas emissions 

This module defines a number of greenhouse gases as pint base units and
their conversion to CO2-equivalent using specific <IPCC report>GWP<y> metrics
implemented as pint contexts.

## Structure of this module

This module consists of a file `emissions.txt` which defines the base units for pint,
as well as a number of files defining different contexts to convert greenhouse
gases to CO2-equivalents using different metrics.

These files should not be edited manually. Instead, they can be regenerated
by running `write_gwp_context.py`, which parses the data table with conversion
factors and writes a text file defining a context.

When adding a new GWP-context file, make sure to add it to the import list
of `emissions.txt` and write a unit test.

## Source of CO-equivalent conversion factors

The conversion factors to CO2-equivalent are parsed from the file `metric_conversions.csv`,
which was created by [lewisjared](https://github.com/lewisjared) and licensed under BSD-3.
See [lewisjared/scmdata v0.4](https://github.com/lewisjared/scmdata/tree/v0.4.0/src/scmdata/data)
for the original file.

The conversion factors were collected from
https://www.ghgprotocol.org/sites/default/files/ghgp/Global-Warming-Potential-Values%20%28Feb%2016%202016%29_1.pdf.
The row with the source was removed from the data file.
