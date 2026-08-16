from django.shortcuts import render

from .calculations import calculate_z_factor
from .plot import create_plot


def theory(request):

    return render(
        request,
        "zfactor/theory.html",
    )

def home(request):

    rows = range(1, 21)

    results = []

    graph = None

    if request.method == "POST":

        for i in rows:

            pressure = request.POST.get(
                f"pressure_{i}"
            )

            temperature = request.POST.get(
                f"temperature_{i}"
            )

            if pressure and temperature:

                pressure = float(pressure)

                temperature = float(temperature)

                z_factor = calculate_z_factor(
                    pressure,
                    temperature,
                )

                results.append(
                    {
                        "pressure": pressure,
                        "temperature": temperature,
                        "z_factor": z_factor,
                    }
                )

        if results:

            graph = create_plot(
                results
            )

    return render(
        request,
        "zfactor/home.html",
        {
            "rows": rows,
            "results": results,
            "graph": graph,
        },
    )
