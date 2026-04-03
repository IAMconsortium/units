import sys
from functools import cache
from itertools import chain
from pathlib import Path

# This package is only required when updating the emissions GWP conversion factors
import globalwarmingpotentials as gwp

# Base path for package code
BASE_PATH = Path(__file__).parent

# Base path for package data
DATA_PATH = BASE_PATH / "data"
CURRENCY_DATA_PATH = BASE_PATH / "currency_data.py"


# Format strings for emissions()
_EMI_HEADER = """# This file was generated using:
#    python -m iam_units.update emissions
# DO NOT ALTER THIS FILE MANUALLY!
"""

# Format string for individual metrics. To expand the set of supported conversions,
# duplicate and modify the first pair of lines in the context. Currently supported:
# 1. Mass.
# 2. Mass rate, or mass per time.
# 3. Flux, or mass per area per time.
# 4. Mass per unit energy.
_EMI_DATA = f"""{_EMI_HEADER}
@context(_a=NaN) {{metric}}
    [mass] -> [_GWP]: value * (_a * _gwp / kg)
    [_GWP] -> [mass]: value / (_a * _gwp / kg)
    [mass] / [time] -> [_GWP] / [time]: value * (_a * _gwp / kg)
    [_GWP] / [time] -> [mass] / [time]: value / (_a * _gwp / kg)
    [mass] / [time] / [area] -> [_GWP] / [time] / [area]: value * (_a * _gwp / kg)
    [_GWP] / [time] / [area] -> [mass] / [time] / [area]: value / (_a * _gwp / kg)
    [time] ** 2 / [length] ** 2 -> [_GWP] * [time] ** 2 / [length] ** 2: value * (_a * _gwp)
    [_GWP] * [time] ** 2 / [length] ** 2 -> [time] ** 2 / [length] ** 2: value / (_a * _gwp)


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

_CURRENCY_DATA = """# This file was generated using:
#    python -m iam_units.update currency
# source=OECD flow=DSD_NAMAIN10@DF_TABLE4
# representative_area[EUR]=DEU
# DO NOT ALTER THIS FILE MANUALLY!

DATA = {{
{data}
}}
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

_CURRENCY_PERIODS = ("2005", "2010", "2015", "2020", "2024")
# OECD Table 4 supplies the primary source for all currently supported methods.
# Cross-source validation against World Bank overlap is deferred to a follow-up
# PR because the WDI SDMX metadata/dataflow path was unreliable in live tests.
# DEU is used as the representative EUR-area series. For exchange rates this is
# equivalent to any euro-area member because the national currency is EUR. For PPP
# methods, the choice is specific to Germany and should remain documented.
_CURRENCY_REF_AREA = {"EUR": "DEU"}
_TRANSACTION_BY_METHOD = {
    "EXC": "EXC_A",
    "EXCE": "EXC_E",
    "PPPGDP": "PPP_B1GQ",
    "PPPPRC": "PPP_P31S14",
    "PPPP41": "PPP_P41",
}
_CURRENCY_QUERY = {
    "FREQ": "A",
    # These dimensions are invariant for the five Table 4 transactions used here:
    # annual frequency, total economy vs total economy, currency-to-USD quotes,
    # and the canonical national-accounts table transformation.
    "SECTOR": "S1",
    "COUNTERPART_SECTOR": "S1",
    "INSTR_ASSET": "F21",
    "ACTIVITY": "_Z",
    "EXPENDITURE": "_Z",
    "UNIT_MEASURE": "XDC_USD",
    "PRICE_BASE": "_Z",
    "TRANSFORMATION": "N",
    # OECD Table 4 data are exposed within DSD_NAMAIN10@DF_TABLE4 using T001.
    "TABLE_IDENTIFIER": "T001",
}


def currency() -> None:
    """Update the generated currency data module."""
    _write_currency_module(CURRENCY_DATA_PATH, _fetch_currency_rows_oecd())


@cache
def _fetch_currency_rows_oecd() -> dict[
    tuple[str, str], tuple[tuple[str, str, float], ...]
]:
    import sdmx
    from sdmx import to_pandas

    client = sdmx.Client("OECD")
    result: dict[tuple[str, str], tuple[tuple[str, str, float], ...]] = {}

    for currency, ref_area in _CURRENCY_REF_AREA.items():
        msg = client.data(
            "DSD_NAMAIN10@DF_TABLE4",
            key={
                **_CURRENCY_QUERY,
                "REF_AREA": ref_area,
                "TRANSACTION": "+".join(_TRANSACTION_BY_METHOD.values()),
            },
            params={
                "startPeriod": min(_CURRENCY_PERIODS),
                "endPeriod": max(_CURRENCY_PERIODS),
            },
        )
        data = to_pandas(msg.data[0]).sort_index()

        for method, transaction in _TRANSACTION_BY_METHOD.items():
            for period in _CURRENCY_PERIODS:
                selected = data.xs(transaction, level="TRANSACTION").xs(
                    period, level="TIME_PERIOD"
                )
                if len(selected) != 1:
                    raise ValueError(
                        f"Expected 1 row for method={method} period={period} "
                        f"currency={currency}; got {len(selected)}"
                    )

                result[method, period] = ((currency, period, float(selected.iloc[0])),)

    return result


def _write_currency_module(
    path: Path, data: dict[tuple[str, str], tuple[tuple[str, str, float], ...]]
) -> None:
    lines = [
        "    "
        + repr((method, period))
        + ": {"
        + ", ".join(
            f"{(currency, row_period)!r}: {value:.6f}"
            for currency, row_period, value in rows
        )
        + "},"
        for (method, period), rows in sorted(data.items())
    ]
    path.write_text(_CURRENCY_DATA.format(data="\n".join(lines)))


def emissions() -> None:
    """Update emissions definitions files."""
    data_path = DATA_PATH / "emissions"

    # Import data from `globalwarmingpotentials`, get list of species aka symbols.
    data = gwp.as_frame().sort_index()
    symbols = data.index

    # Format and write the species defs file
    lines = [_EMI_HEADER]
    for species, alias in _EMI_EQUIV.items():
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
