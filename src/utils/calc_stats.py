import math


def app(apm: float, pps: float) -> float:
    return apm / (pps * 60)


def ds_second(vs: float, apm: float) -> float:
    return (vs / 100) - (apm / 60)


def ds_piece(vs: float, apm: float, pps: float) -> float:
    return ds_second(vs, apm) / pps


def app_ds_piece(vs: float, apm: float, pps: float) -> float:
    return ds_piece(vs, apm, pps) + apm / (pps * 60)


def cheese_index(vs: float, apm: float, pps: float) -> float:
    return (
        (ds_piece(vs, apm, pps) * 150)
        + (((vs / apm) - 2) * 50)
        + ((0.6 - app(apm, pps)) * 125)
    )


def garbage_efficiency(vs: float, apm: float, pps: float) -> float:
    return ((app(apm, pps) * ds_second(vs, apm)) / pps) * 2


def area(apm, pps, vs) -> float:
    return (
        apm
        + pps * 45
        + vs * 0.444
        + app(apm, pps) * 185
        + ds_second(vs, apm) * 175
        + ds_piece(vs, apm, pps) * 450
        + garbage_efficiency(vs, apm, pps) * 315
    )


def weighted_app(apm, pps, vs) -> float:
    return app(apm, pps) - 5 * math.tan((cheese_index(vs, apm, pps) / -30) + 1)


def estimated_tr(pps: float, apm: float, vs: float, rd: float) -> float:
    return 25000 / (
        1
        + (
            10
            ^ (
                (
                    (
                        1500
                        - (
                            4.0867
                            * (pps * 90 + app * 290 + ds_piece(vs, apm, pps) * 750)
                            + 186.68
                        )
                    )
                    * 3.14159
                )
                / ((15.9056943314 * (rd ^ 2) + 3527584.25978) ^ 0.5)
            )
        )
    )
