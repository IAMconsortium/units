"""Currency conversions."""

from enum import Enum, auto
from typing import TYPE_CHECKING

from .currency_data import DATA

if TYPE_CHECKING:
    from pint import UnitRegistry

CONFIGURED_CURRENCY_ATTR = "_iam_units_configured_currency_bridges"


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
        Year of the USD↔currency exchange rate used to bridge the two currencies.

    Notes
    -----
    `period` selects only the exchange-rate bridge year; the within-currency deflator
    chains then carry any USD vintage to any defined target vintage. For example,
    ``configure_currency("EXC", 2010)`` converts between any ``USD_*`` and any ``EUR_*``
    using the 2010 EUR/USD exchange rate as the bridge. Because the currencies do not
    inflate in lock-step, different `period` values give different results.

    A registry holds one bridge per target currency. Repeated calls with the same
    `method` and `period` are a no-op; a call that changes either for an
    already-configured currency raises, rather than silently altering earlier
    conversions.

    Raises
    ------
    NotImplementedError
        For unsupported values of `method` or `period`.
    ValueError
        For an unknown `method`, or a call that changes the configured `method` or
        `period` for an already-bridged currency.
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
        data = DATA[method.name, period]
    except KeyError:
        raise NotImplementedError(
            f"Convert currency for method={method!r}, period={period}; use one of:\n"
            + repr(sorted(DATA))
        )

    # One bridge per target currency: map each currency to its active (method, period)
    bridge = (method, period)
    configured: dict[str, tuple[METHOD, str]] = dict(
        getattr(registry, CONFIGURED_CURRENCY_ATTR, {})
    )

    # Identify any conflicting, existing configurations: currencies already bridged
    # with a different method or period
    if conflicts := {
        other: existing
        for other, _ in data
        if (existing := configured.get(other)) is not None and existing != bridge
    }:
        detail = ", ".join(
            f"{other} (configured with method={m.name!r}, period={p})"
            for other, (m, p) in sorted(conflicts.items())
        )
        raise ValueError(
            f"configure_currency() cannot change to method={method.name!r}, "
            f"period={period} for already configured: {detail}"
        )

    # Anchor the bridge at each target currency's chain base ({other}_2005): dividing
    # the exchange rate by _{other}_deflator_{period} (defined alongside the vintages in
    # definitions.txt) keeps the whole {other} vintage chain connected to USD through
    # the chosen bridge year.
    pending = {
        other: rate
        for (other, _), rate in data.items()
        if configured.get(other) != bridge
    }
    for other, rate in pending.items():
        registry.define(
            f"{other}_2005 = USD_{period} / {rate} / _{other}_deflator_{period}"
            f" = {other}"
        )
        configured[other] = bridge

    if pending:
        setattr(registry, CONFIGURED_CURRENCY_ATTR, configured)
