from units import convert

assert abs(convert(1, "km", "m") - 1000) < 1e-9
assert abs(convert(1, "in", "cm") - 2.54) < 1e-9
assert abs(convert(5000, "mm", "km") - 0.005) < 1e-12
assert abs(convert(250, "cm", "m") - 2.5) < 1e-9
try:
    convert(1, "mile", "m")
except ValueError:
    pass
else:
    raise AssertionError("unknown units must still raise ValueError")
print("OK")
