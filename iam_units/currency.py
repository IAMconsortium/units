"""Currency conversions.

See the inline comments (NB) for possible extensions of this code; also
iam_units.update.currency.
"""
from typing import Literal, Union

#: Exchange rate data for method=EXC, period=2005, from
#: https://data.oecd.org/conversion/exchange-rates.htm
#:
#: NB this data could be extended to cover other currencies.
DATA = {
    ("EUR", "2005"): 0.8038,
}


def configure_currency(
    method: Literal["EXC", "EXCE", "PPPGDP", "PPPPRC", "PPPP41"] = "EXC",
    period: Union[str, int] = 2005,
):
    """Configure currency conversions.

    Parameters
    ----------
    method : str
        Method of computing exchange rate data. The accepted values are from the code
        list OECD:CL_SNA_TABLE4_TRANSACT; given here with their English descriptions.

        - `EXC`: Exchange rates, period-average
        - `EXCE`: Exchange rates, end of period
        - `PPPGDP`: Purchasing Power Parities for GDP
        - `PPPPRC`: Purchasing Power Parities for private consumption
        - `PPPP41`: Purchasing Power Parities for actual individual consumption
    period : int or str
        Time period (e.g. year) for exchange rates.

    Raises
    ------
    NotImplementedError
        For unsupported values of `method` or `period`. Currently, only the defaults are
        supported.
    """

    from iam_units import registry

    # Ensure string
    period = str(period)

    # Select data for (method, period)
    if method == "EXC" and period == "2005":
        # NB this code could be extended to:
        # - Load data for other combinations of (method, period).
        # - Load from file, instead of copying from values embedded in code.
        data = DATA.copy()
    else:
        message = []
        if method != "EXC":
            message.append(f"method={method!r}")
        if period != "2005":
            message.append(f"period={period}")
        raise NotImplementedError(", ".join(message))

    # Insert definitions
    for (other, period), value in data.items():
        registry.define(f"{other}_{period} = USD_{period} / {value} = {other}")
