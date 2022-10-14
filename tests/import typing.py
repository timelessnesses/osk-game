import typing
from decimal import ROUND_05UP, Decimal

import src.utils.calc_stats as stats

data_set: dict[str, typing.Union[int, float]] = {
    "apm": 42.94,
    "pps": 1.5,
    "vs": 91,
    "rd": 60.89,
}


def test_weighted_app():
    assert (
        float(
            Decimal(stats.weighted_app(**data_set)).quantize(
                Decimal(".0001"), rounding=ROUND_05UP
            )
        )
        == 0.5084
    )
