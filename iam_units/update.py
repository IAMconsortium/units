import sys
from itertools import chain
from pathlib import Path

# This package is only required when updating the emissions GWP conversion factors
import globalwarmingpotentials as gwp  # type: ignore

# Base path for package code
BASE_PATH = Path(__file__).parent

# Base path for package data
DATA_PATH = BASE_PATH / "data"


# Format strings for emissions()
_EMI_HEADER = """# This file was generated using:
#    python -m iam_units.update emissions
# DO NOT ALTER THIS FILE MANUALLY!
"""

# Format string for individual metrics. To expand the set of supported
# conversions, duplicate and modify the first pair of lines in the context.
# Only the portion before of the ':' needs to be modified. Currently supported:
# 1. Mass
# 2. Mass rate, i.e. mass per time.
# 3. Flux, i.e. mass per area per time.
_EMI_DATA = f"""{_EMI_HEADER}
@context(_a=NaN) {{metric}}
    [mass] -> [_GWP]: value * (_a * _gwp / kg)
    [_GWP] -> [mass]: value / (_a * _gwp / kg)
    [mass] / [time] -> [_GWP] / [time]: value * (_a * _gwp / kg)
    [_GWP] / [time] -> [mass] / [time]: value / (_a * _gwp / kg)
    [mass] / [time] / [area] -> [_GWP] / [time] / [area]: value * (_a * _gwp / kg)
    [_GWP] / [time] / [area] -> [mass] / [time] / [area]: value / (_a * _gwp / kg)


    {{defs}}
@end
"""  # noqa: E501

# Format string for an importable Python module defining the *pattern* regex,
# which resembles: (?<=[ -])(CO2|C|N2O|CH4)(?=[ -/]|[^\w]|$)
# - Preceded by a space or '-' character.
# - Followed by a space, '-', '/', end-of-string, or non-word (\w) character.
#   The latter avoids matching only the 'C' within 'CH4'.
_EMI_CODE = rf"""{_EMI_HEADER}
import re

GWP_VERSION = '{gwp.__version__}'

# All available metrics usable with convert_gwp().
METRICS = [
    '{{metrics}}'
]

# All recognised emission species usable with convert_gwp(). See *pattern*.
SPECIES = [
    '{{symbols}}',
    ]

# Sets of symbols that refer to the same species and are interchangeable.
EQUIV = [
    set({{equiv}}),
    ]

# Regular expression for one *SPECIES* in a pint-compatible unit string.
pattern = re.compile(
    '(?<=[ -])('
    + '|'.join(SPECIES)
    + r')(?=[ -/]|[^\w]|$)')
"""

# Format string for list of metrics.
_EMI_METRICS = f"""{_EMI_HEADER}

# Define contexts for each set of metrics

{{metrics}}
"""

# Equivalents: different symbols for the same species.
_EMI_EQUIV = {
    "CO2": {
        "CO2_eq": None,
        "CO2e": None,
        "CO2eq": None,
        "C": "44. / 12 * ",
        "Ce": "44. / 12 * ",
    }
}


def emissions():
    """Update emissions definitions files."""
    data_path = DATA_PATH / "emissions"

    # Import data from `globalwarmingpotentials`, get list of species aka symbols.
    data = gwp.as_frame().sort_index()
    symbols = data.index

    # Format and write the species defs file
    lines = [_EMI_HEADER]
    for (species, alias) in _EMI_EQUIV.items():
        lines.extend(
            f"a_{a} = {factor or ''}a_{species}" for a, factor in alias.items()
        )
    lines.extend(f"a_{s} = NaN" for s in symbols)
    lines.append("")
    (data_path / "species.txt").write_text("\n".join(lines))

    # Write a Python module with a regex matching the species names

    # Prepare list including all symbols
    all_alias_groups = list([key, *value] for key, value in _EMI_EQUIV.items())
    all_symbols = list(chain(*all_alias_groups, symbols))

    # Format and write `emissions.py`
    code = _EMI_CODE.format(
        metrics="',\n    '".join(list(data.columns)),
        symbols="',\n    '".join(all_symbols),
        equiv="),\n    set(".join(map(repr, all_alias_groups)),
    )
    (BASE_PATH / "emissions.py").write_text(code)

    # Format and write `metrics.txt"`
    code = _EMI_METRICS.format(
        metrics="\n".join([f"@import {m}.txt" for m in data.columns])
    )
    (data_path / "metrics.txt").write_text(code)

    # Write one file containing a context for each metric
    for metric in data.columns:
        # Conversion factor definitions
        defs = [
            f"a_{species} = {value}" for species, value in data[metric].dropna().items()
        ]

        # Format the template with the definitions
        content = _EMI_DATA.format(metric=metric, defs="\n    ".join(defs))

        # Write to file
        (data_path / f"{metric}.txt").write_text(content)


if __name__ == "__main__":
    # Invoked using 'python -m iam_units.update'
    # For each additional argument, call the function of the same name
    for module in sys.argv[1:]:
        locals()[module]()
