Unit definitions for integrated-assessment research
***************************************************

© 2020 `IAM-units authors`_; licensed under the `GNU GPL version 3`_.

The file `definitions.txt`_ gives `Pint`_-compatible definitions of energy, climate, and related units to supplement the SI and other units included in Pint's `default_en.txt`_.
These definitions are used by:

- the IIASA Energy Program `MESSAGEix-GLOBIOM`_ integrated assessment model (IAM),
- the Python package `pyam`_ for analysis and visualization of integrated-assessment scenarios (see `pyam.IamDataFrame.convert_unit()`_ for details)

and may be used for research in integrated assessment, energy systems, transportation, or other, related fields.
(Please open a `pull request`_ to add your usage to this README!)

Usage
=====

.. code-block:: python

    >>> from iam_units import registry

    >>> qty = registry('1.2 tce')
    >>> qty
    1.2 <Unit('tonne_of_coal_equivalent')>

    >>> qty.to('GJ')
    29.308 <Unit('gigajoule')>

To make the ``registry`` from this package the default:

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
   - - 'C' = Coulomb
     - 'C' = carbon
     - See `emissions.txt`_ at line 10.

Technical details
=================

Emissions and GWP
-----------------

`emissions.txt`_ defines some greenhouse gases (GHGs) as Pint base units.
Conversion of masses of these GHGs to CO₂ equivalents use selectable global warming potential (GWP) metrics, implemented as Pint `contexts`_ in the other files in the same directory.
The contexts have names like ``gwp_<IPCC report>GWP<years>``, where ``<years>`` is `100` and:

.. list-table::
   :header-rows: 1

   - - ``<IPCC report>``
     - Meaning
   - - ``SAR``
     - Second Assessment Report (1995)
   - - ``AR4``
     - Fourth Assessment Report (2007)
   - - ``AR5``
     - Fifth Assessment Report (2014)

To use one of these contexts, give its name as the second argument to the ``pint.Quantity.to()`` method:

.. code-block:: python

   >>> qty = registry('3.5e3 t N20')
   >>> qty
   3500 <Unit('metric_ton * nitrous_oxide')>

   >>> qty.to('Mt CO2', 'gwp_AR4GWP100')
   0.9275 <Unit('carbon_dioxide * megametric_ton')>

   # Using a different metric
   >>> qty.to('Mt CO2', 'gwp_SARGWP100')
   1.085 <Unit('carbon_dioxide * megametric_ton')>

Data sources
~~~~~~~~~~~~
The GWP unit definitions are generated using the file metric_conversions.csv.
The file is copied from `lewisjared/scmdata`_ v0.4, authored by `@lewisjared <https://github.com/lewisjared>`_, `@swillner <https://github.com/swillner>`_, and `@znicholls <https://github.com/znicholls>`_ and licensed under BSD-3.
The version in scmdata was transcribed from `this source`_ (PDF link).

See `<DEVELOPING.rst>`_ for details on updating the definitions.

.. _contexts: https://pint.readthedocs.io/en/latest/contexts.html
.. _lewisjared/scmdata: https://github.com/lewisjared/scmdata/tree/v0.4.0/src/scmdata/data
.. _this source: https://www.ghgprotocol.org/sites/default/files/ghgp/Global-Warming-Potential-Values%20%28Feb%2016%202016%29_1.pdf


Tests and development
=====================

Use ``pytest iam_units`` to check that the definitions can be loaded.
Example unit expressions in `checks.csv`_ are also checked.
See `<DEVELOPING.rst>`_ for further details.

.. _IAM-units authors: ./AUTHORS
.. _GNU GPL version 3: ./LICENSE
.. _definitions.txt: ./iam_units/data/definitions.txt
.. _emissions.txt: ./iam_units/data/emissions/emissions.txt
.. _checks.csv: ./iam_units/data/checks.csv
.. _Pint: https://pint.readthedocs.io
.. _default_en.txt: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
.. _MESSAGEix-GLOBIOM: https://message.iiasa.ac.at
.. _pyam: https://pyam-iamc.readthedocs.io
.. _pyam.IamDataFrame.convert_unit(): https://pyam-iamc.readthedocs.io/en/stable/api/iamdataframe.html#pyam.IamDataFrame.convert_unit
.. _pull request: https://github.com/IAMconsortium/units/pulls
