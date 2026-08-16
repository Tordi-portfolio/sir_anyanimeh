import base64
import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def create_plot(results):

    fig, ax = plt.subplots(
        figsize=(12, 8)
    )

    temperatures = sorted(
        set(
            row["temperature"]
            for row in results
        )
    )

    for temperature in temperatures:

        curve = [
            row
            for row in results
            if row["temperature"] == temperature
        ]

        curve = sorted(
            curve,
            key=lambda row: row["pressure"]
        )

        if len(curve) < 2:

            continue

        pressures = np.array(
            [
                row["pressure"]
                for row in curve
            ]
        )

        z_factors = np.array(
            [
                row["z_factor"]
                for row in curve
            ]
        )

        x = np.linspace(
            pressures.min(),
            pressures.max(),
            300,
        )

        y = np.interp(
            x,
            pressures,
            z_factors,
        )

        ax.plot(
            x,
            y,
            linewidth=2,
            label=f"{temperature}°C",
        )

        ax.scatter(
            pressures,
            z_factors,
        )

    ax.set_xlabel(
        "Pressure (psi)"
    )

    ax.set_ylabel(
        "Z-Factor"
    )

    ax.set_title(
        "CO₂ Z-Factor Chart"
    )

    ax.grid(True)

    ax.legend()

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )

    buffer.seek(0)

    image = base64.b64encode(
        buffer.read()
    ).decode()

    plt.close()

    return image