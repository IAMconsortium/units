"""Currency conversions.

See the inline comments (NB) for possible extensions of this code; also
iam_units.update.currency.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pint import UnitRegistry

#: Exchange rate data for method=EXC, period=2005, from
#: https://data.oecd.org/conversion/exchange-rates.htm
#:
#: NB this data could be extended to cover other currencies.
DATA = {
    ("EUR", "2005"): 0.8038,
}


class METHOD(Enum):
    """Method of computing exchange rate data.

    From the code list OECD:CL_SNA_TABLE4_TRANSACT. The docstrings here are from their
    English-language descriptions.
    """

    #: Exchange rates, period-average
    EXC = auto()
    #: Exchange rates, end of period.
    EXCE = auto()
    #: Purchasing Power Parities for GDP.
    PPPGDP = auto()
    #: Purchasing Power Parities for private consumption.
    PPPPRC = auto()
    #: Purchasing Power Parities for actual individual consumption.
    PPPP41 = auto()


def configure_currency(
    method: METHOD | str = METHOD.EXC,
    period: str | int = 2005,
    *,
    _registry: "UnitRegistry | None" = None,
) -> None:
    """Configure currency conversions.

    Parameters
    ----------
    method : METHOD or str
        Method of computing exchange rate data.
    period : int or str
        Time period (e.g. year) for exchange rates.

    Raises
    ------
    NotImplementedError
        For unsupported values of `method` or `period`. Currently, only the defaults are
        supported.
    """
    if _registry is None:
        from iam_units import registry
    else:
        registry = _registry

    # Ensure instance of METHOD
    try:
        method = METHOD[method] if isinstance(method, str) else method
    except KeyError:
        raise ValueError(f"method={method}; expected one of {[m.name for m in METHOD]}")

    # Ensure string
    period = str(period)

    # Select data for (method, period)
    if method is METHOD.EXC and period == "2005":
        # NB this code could be extended to:
        # - Load data for other combinations of (method, period).
        # - Load from file, instead of copying from values embedded in code.
        data = DATA.copy()
    else:
        message = []
        if method is not METHOD.EXC:
            message.append(f"method={method!r}")
        if period != "2005":
            message.append(f"period={period}")
        raise NotImplementedError(", ".join(message))

    # Insert definitions
    for (other, period), value in data.items():
        registry.define(f"{other}_{period} = USD_{period} / {value} = {other}")
