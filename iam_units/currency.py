"""Currency conversions."""

from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pint import UnitRegistry

DATA_PATH = Path(__file__).with_name("data") / "currency"
CONFIGURED_CURRENCY_ATTR = "_iam_units_configured_currency_methods"


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
    """Configure currency conversions on a registry.

    Parameters
    ----------
    method : METHOD or str
        Method of computing exchange rate data.
    period : int or str
        Time period (e.g. year) for exchange rates.

    Notes
    -----
    Currency units can only be configured once per ``(currency, period)`` pair and
    method on a given registry. Repeated calls with the same method are a no-op; a
    different method for an already configured pair raises ``ValueError``.

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
    configured = dict(getattr(registry, CONFIGURED_CURRENCY_ATTR, {}))
    conflicts = [
        (other, file_period, configured[(other, file_period)])
        for other, file_period in data
        if configured.get((other, file_period), method) is not method
    ]

    if conflicts:
        unit_list = ", ".join(
            sorted(
                (
                    f"{other}_{file_period} "
                    f"(already configured with {configured_method.name})"
                )
                for other, file_period, configured_method in conflicts
            )
        )
        raise ValueError(
            f"Currency unit(s) already defined on this registry: {unit_list}. "
            "configure_currency() cannot switch methods for an existing "
            "(currency, period) pair."
        )

    # Insert definitions
    for (other, period), value in data.items():
        registry.define(f"{other}_{period} = USD_{period} / {value} = {other}")

    configured.update({key: method for key in data})
    setattr(registry, CONFIGURED_CURRENCY_ATTR, configured)


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
