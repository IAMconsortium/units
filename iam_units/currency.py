"""Currency conversions."""

from enum import Enum, auto
from typing import TYPE_CHECKING

from .currency_data import DATA

if TYPE_CHECKING:
    from pint import UnitRegistry

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
    different method raises an exception for any already-configured pairs.

    Raises
    ------
    NotImplementedError
        For unsupported values of `method` or `period`.
    ValueError
        For repeated calls with different `method`.
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

    try:
        data = DATA[method.name, period].copy()
    except KeyError:
        raise NotImplementedError(
            f"Convert currency for method={method!r}, period={period}; use one of:\n"
            + repr(sorted(DATA))
        )

    # Maybe retrieve a dict mapping from (other, period): method for every already-
    # configured currency
    configured = dict(getattr(registry, CONFIGURED_CURRENCY_ATTR, {}))

    # Identify any conflicting, existing configurations: keys appearing in both `data`
    # and `configured` with different methods
    if conflicts := {
        k: m for k, m in configured.items() if k in data and m is not method
    }:
        unit_list = sorted(
            (f"{other}_{period} (configured with method={method_configured.name!r})")
            for (other, period), method_configured in conflicts.items()
        )
        raise ValueError(
            f"configure_currency() cannot change to method={method.name!r} for already "
            f"defined units: {', '.join(unit_list)}"
        )

    # Insert definitions
    for (other, period), value in data.items():
        registry.define(f"{other}_{period} = USD_{period} / {value} = {other}")
        configured[(other, period)] = method

    # Store information about configuration
    setattr(registry, CONFIGURED_CURRENCY_ATTR, configured)
