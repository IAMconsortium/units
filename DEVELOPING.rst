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


Releasing
*********

1. Before releasing, check https://github.com/IAMconsortium/units/actions/workflows/test.yaml to ensure that the push and scheduled builds are passing.
   Address any failures before releasing.

2. Tag the release candidate version, i.e. with a ``rcN`` suffix, and push::

    $ git tag v2021.3.22rc1
    $ git push --tags origin main

3. Check:

   - at https://github.com/IAMconsortium/units/actions/workflows/publish.yaml that the workflow completes: the package builds successfully and is published to TestPyPI.
   - at https://test.pypi.org/project/iam-units/ that:

      - The package can be downloaded, installed and run.
      - The README is rendered correctly.

   Address any warnings or errors that appear.
   If needed, make a new commit and go back to step (2), incrementing the rc number.

4. (optional) Tag the release itself and push::

    $ git tag v2021.3.22
    $ git push --tags origin main

   This step (but *not* step (2)) can also be performed directly on GitHub; see (5), next.

5. Visit https://github.com/IAMconsortium/units/releases and mark the new release: either using the pushed tag from (4), or by creating the tag and release simultaneously.

6. Check at https://github.com/IAMconsortium/units/actions/workflows/publish.yaml and https://pypi.org/project/iam-units/ that the distributions are published.


Generated data files for GWP contexts
=====================================

iam_units/data/emissions/emissions.txt defines the base units for Pint, and imports the other files iam_units/data/emissions/\*.txt.
These files each define one context, and contain a notice that they should not be edited manually.

First, install the ``globalwarmingpotentials`` package::

    $ pip install globalwarmingpotentials

Update these files using the command::

    $ python -m iam_units.update emissions

The update submodule writes the context files.
When adding a new context file, make sure to ``@import`` it in emissions.txt and expand the tests.
