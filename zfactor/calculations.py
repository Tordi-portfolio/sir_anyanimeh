def calculate_z_factor(
    pressure,
    temperature,
):

    # Normalize the variables

    p = pressure / 1000

    t = temperature / 100

    # Polynomial coefficients

    a = 0.78
    b = -0.08
    c = 0.35
    d = 0.04
    e = -0.02
    f = 0.03
    g = -0.004
    h = 0.002
    i = -0.003
    j = 0.005

    z = (
        a
        + (b * p)
        + (c * t)
        + (d * (p ** 2))
        + (e * (t ** 2))
        + (f * p * t)
        + (g * (p ** 3))
        + (h * (t ** 3))
        + (i * (p ** 2) * t)
        + (j * p * (t ** 2))
    )

    return round(
        z,
        4,
    )