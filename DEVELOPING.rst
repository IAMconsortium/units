Development notes
*****************

The repository and package aim to be ruthlessly simple, and thus as easy as possible to maintain.
Thus:

- No built documentation; like `pycountry <https://pypi.org/project/pycountry/>`_, the README *is* the documentation.
- Actual code (in \_\_init\_\_.py) kept to a minimum.
- Versioning:

  - similar to pycountry: ``<YYYY>.<M>.<D>``.
  - `setuptools-scm <https://pypi.org/project/setuptools-scm/>`_ and git tags used for all versioning; nothing hardcoded.

- Minimal CI configuration: one service/OS/Python version.
- AUTHORS: anyone adding a commit to the repo should also add their name to AUTHORS.


Releasing
=========

The 'Build' and 'Check' steps are also performed by the GitHub CI for each PR/commit.

.. code-block::

   # Tag the release. Omit leading zeros.
   $ git tag v2020.4.6

   # Build
   $ rm -r build dist
   $ python3 setup.py bdist_wheel sdist

   # Check
   $ twine check dist/*

   # Upload to TestPyPI and check that the package is installable
   $ twine upload --repository-url https://test.pypi.org/legacy dist/*

   # Publish
   $ twine upload
   $ git push --tags


Generated data files for GWP contexts
=====================================

iam_units/data/emissions/emissions.txt defines the base units for Pint, and imports the other files iam_units/data/emissions/\*.txt.
These files each define one context, and contain a notice that they should not be edited manually.

Update these files using the command::

    $ python -m iam_units.update emissions

The update submodule parses metric_conversions.csv and writes the context files.
When adding a new context file, make sure to ``@import`` it in emissions.txt and expand the tests.
