TO_METERS = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000.0,
    "in": 0.0254,
}


def convert(value, from_unit, to_unit):
    """convert(250, "cm", "m") == 2.5"""
    if from_unit not in TO_METERS or to_unit not in TO_METERS:
        raise ValueError(f"unknown unit: {from_unit} or {to_unit}")
    return value * TO_METERS[from_unit] / TO_METERS[to_unit]
