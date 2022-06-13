Unit definitions for integrated-assessment research
***************************************************

.. image:: https://img.shields.io/pypi/v/iam-units.svg
   :target: https://pypi.python.org/pypi/iam-units/
   :alt: PyPI version

.. image:: https://github.com/IAMconsortium/units/actions/workflows/test.yaml/badge.svg
   :target: https://github.com/IAMconsortium/units/actions/workflows/test.yaml
   :alt: Build status

© 2020–2022 `IAM-units authors`_; licensed under the `GNU GPL version 3`_.

The file `definitions.txt`_ gives `Pint`_-compatible definitions of energy, climate, and related units to supplement the SI and other units included in Pint's `default_en.txt`_.
These definitions are used by:

- the IIASA Energy Program `MESSAGEix-GLOBIOM`_ integrated assessment model (IAM),
- the Python package `pyam`_ for analysis and visualization of integrated-assessment scenarios (see `pyam.IamDataFrame.convert_unit()`_ for details)

and may be used for research in integrated assessment, energy systems, transportation, or other, related fields.

Please open a GitHub `issue`_ or `pull request`_ to:

- Add more units to definitions.txt.
- Add your usage of iam-units to this README.
- Request or contribute additional features.

Usage
=====

``iam_units.registry`` is a ``pint.UnitRegistry`` object with the definitions from definitions.txt loaded:

.. code-block:: python

    >>> from iam_units import registry

    # Parse an energy unit defined by iam-units
    >>> qty = registry('1.2 tce')
    >>> qty
    1.2 <Unit('tonne_of_coal_equivalent')>

    >>> qty.to('GJ')
    29.308 <Unit('gigajoule')>

To make the registry from this package the default:

.. code-block:: python

    >>> import pint
    >>> pint.set_application_registry(registry)

    # Now used by default for pint top-level classes and methods
    >>> pint.Quantity('1.2 tce')
    1.2 <Unit('tonne_of_coal_equivalent')>

Warnings
========

``iam_units`` overwrites Pint's default definitions in the following cases:

.. list-table::
   :header-rows: 1

   - - ``pint`` default
     - ``iam_units``
     - Note
   - - 'kt' = knot [velocity]
     - 'kt' = 1000 metric tons
     - 'kt' is commonly used for emissions in the IAM-context.

Technical details
=================

Emissions and GWP
-----------------

The function ``convert_gwp()`` converts from mass (or mass-related units) of one specific greenhouse gas (GHG) species to an equivalent quantity of second species, based on `global warming potential`_ (GWP) *metrics*.
The supported species are listed in `species.txt`_ and the variable ``iam_units.emissions.SPECIES``.

The metrics have names like ``<IPCC report>GWP<years>``, where ``<years>`` is the time period over which heat absorption was assessed.
The supported metrics are listed in the variable ``iam_units.emissions.METRICS``.

.. code-block:: python

   >>> qty = registry('3.5e3 t').to('Mt')
   >>> qty
   3.5 <Unit('megametric_ton')>

   # Convert from mass of N2O to GWP-equivalent mass of CO2
   >>> convert_gwp('AR4GWP100', qty, 'N2O', 'CO2')
   0.9275 <Unit('megametric_ton')>

   # Using a different metric
   >>> convert_gwp('AR5GWP100', qty, 'N2O', 'CO2')
   1.085 <Unit('megametric_ton')>

The function also accepts input with the commonly-used combination of mass (or related) *units* **and** the identity of a particular GHG species:

.. code-block:: python

   # Expression combining magnitude, units, *and* GHG species
   >>> qty = '3.5 Mt N2O / year'

   # Input species is determined from *qty*
   >>> convert_gwp('AR5GWP100', qty, 'CO2')
   1.085 <Unit('megametric_ton / year')>

Strictly, the original species is not a unit but a *nominal property*; see the `International Vocabulary of Metrology`_ (VIM) used in the SI.
To avoid ambiguity, code handling GHG quantities should also track and output these nominal properties, including:

1. Original species.
2. Species in which GWP-equivalents are expressed (e.g. CO₂ or C)
3. GWP metric used to convert (1) to (2).

To aid with this, the function ``format_mass()`` is provided to re-assemble strings that include the GHG species or other information:

.. code-block:: python

   # Perform a conversion
   >>> qty = convert_gwp('AR5GWP100', '3.5 Mt N2O / year', 'CO2e')
   >>> qty
   927.5 <Unit('megametric_ton / year')>

   # Format a string with species and metric info after the mass units of *qty*
   >>> format_mass(qty, 'CO₂-e (AR5)', spec=':~')
   'Mt CO₂-e (AR5) / a'

See `Pint's formatting documentation`_ for values of the *spec* argument.

Data sources
~~~~~~~~~~~~

The GWP unit definitions are generated from the package globalwarmingpotentials_.
The version of that package used to generate the definitions is stated in the variable ``iam_units.emissions.GWP_VERSION``.

See `<DEVELOPING.rst>`_ for details on updating the definitions.

.. _global warming potential: https://en.wikipedia.org/wiki/Global_warming_potential
.. _International Vocabulary of Metrology: https://www.bipm.org/utils/common/documents/jcgm/JCGM_200_2008.pdf
.. _contexts: https://pint.readthedocs.io/en/latest/contexts.html
.. _Pint's formatting documentation: https://pint.readthedocs.io/en/latest/tutorial.html#string-formatting
.. _globalwarmingpotentials: https://github.com/openclimatedata/globalwarmingpotentials


Tests and development
=====================

Use ``pytest iam_units --verbose`` to run the test suite included in the submodule ``iam_units.test_all``.
See `<DEVELOPING.rst>`_ for further details.

.. _IAM-units authors: ./AUTHORS
.. _GNU GPL version 3: ./LICENSE
.. _definitions.txt: ./iam_units/data/definitions.txt
.. _emissions.txt: ./iam_units/data/emissions/emissions.txt
.. _species.txt: ./iam_units/data/emissions/species.txt
.. _checks.csv: ./iam_units/data/checks.csv
.. _Pint: https://pint.readthedocs.io
.. _default_en.txt: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
.. _MESSAGEix-GLOBIOM: https://docs.messageix.org
.. _pyam: https://pyam-iamc.readthedocs.io
.. _pyam.IamDataFrame.convert_unit(): https://pyam-iamc.readthedocs.io/en/stable/api/iamdataframe.html#pyam.IamDataFrame.convert_unit
.. _issue: https://github.com/IAMconsortium/units/issues
.. _pull request: https://github.com/IAMconsortium/units/pulls
