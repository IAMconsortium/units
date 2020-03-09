# Unit definitions for IA research

© 2020 [IAMC members](http://www.globalchange.umd.edu/iamc/members/);
licensed under the [Creative Commons Attribution 4.0 license](https://creativecommons.org/licenses/by/4.0/).

`definitions.txt` gives [Pint](https://pint.readthedocs.io)-compatible definitions of energy, climate, and related units to supplement the SI and other units included in Pint's [default_en.txt](https://github.com/hgrecco/pint/blob/master/pint/default_en.txt).
These definitions are used by:

- the IIASA Energy Program [MESSAGEix-GLOBIOM](https://message.iiasa.ac.at) integrated assessment model (IAM),

and may be used for research in integrated assessment, energy systems, transportation, or other, related fields.

## Usage

```python
>>> import pint

>>> ureg = pint.UnitRegistry()
>>> ureg.load_definitions('definitions.txt')

>>> qty = ureg('1.2 tce')
>>> qty
1.2 <Unit('tonne_of_coal_equivalent')>

>>> qty.to('GJ')
29.308 <Unit('gigajoule')>
```

This repository can be included in others as a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

## Tests

Use `pytest test.py` to check that the definitions can be loaded.
Example unit expressions in `checks.csv` are also checked.
