"""Currency conversions."""

from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pint import UnitRegistry

DATA_PATH = Path(__file__).with_name("data") / "currency"


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
        For unsupported values of `method` or `period`.
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

    data = _load_currency_data(method, period)

    # Insert definitions
    for (other, period), value in data.items():
        registry.define(f"{other}_{period} = USD_{period} / {value} = {other}")


def _load_currency_data(method: METHOD, period: str) -> dict[tuple[str, str], float]:
    path = DATA_PATH / f"{method.name}-{period}.txt"

    if not path.exists():
        message = []
        if method is not METHOD.EXC:
            message.append(f"method={method!r}")
        if period != "2005":
            message.append(f"period={period}")
        raise NotImplementedError(", ".join(message))

    result: dict[tuple[str, str], float] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        other, file_period, value = line.split()
        result[(other, file_period)] = float(value)

    if not result:
        raise ValueError(f"No currency data found in {path}")

    return result
