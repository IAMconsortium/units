Unit definitions for integrated-assessment research
***************************************************

© 2020 `IAMC members`_; licensed under the `Creative Commons Attribution 4.0 license <CC-BY>`_.

The file `definitions.txt`_ gives `Pint`_-compatible definitions of energy, climate, and related units to supplement the SI and other units included in Pint's `default_en.txt`_.
These definitions are used by:

- the IIASA Energy Program `MESSAGEix-GLOBIOM`_ integrated assessment model (IAM),
- the Python package `pyam`_ for analysis and visualization of integrated-assessment scenarios (see `IamDataFrame.convert_unit() <pyam-convert_unit>`_ for details)

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
    # Now used by default
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

Tests and development
=====================

Use ``pytest iam_units`` to check that the definitions can be loaded.
Example unit expressions in `checks.csv`_ are also checked.
See `<DEVELOPING.rst>`_ for further details.

.. _IAMC members: http://www.globalchange.umd.edu/iamc/members/
.. _CC-BY: https://creativecommons.org/licenses/by/4.0/
.. _definitions.txt: ./iam_units/data/definitions.txt
.. _emissions.txt: ./iam_units/data/emissions/emissions.txt
.. _checks.csv: ./iam_units/data/checks.csv
.. _Pint: https://pint.readthedocs.io
.. _default_en.txt: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
.. _MESSAGEix-GLOBIOM: https://message.iiasa.ac.at
.. _pyam: https://pyam-iamc.readthedocs.io
.. _pyam-convert_unit: https://pyam-iamc.readthedocs.io/en/latest/api.html#pyam.IamDataFrame.convert_unit
.. _pull request: https://github.com/IAMconsortium/units/pulls
