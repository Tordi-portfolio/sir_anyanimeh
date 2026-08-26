from collections import defaultdict

from django.core.paginator import Paginator
from django.shortcuts import render

from .models import ZFactorPoint, ZRawDataPoint


def zfactor_chart(request):
    """
    Renders a locked, read-only Standing-Katz style chart: Z-factor (y-axis)
    vs Pressure (x-axis), with one line per Temperature isotherm.
    """
    points = ZFactorPoint.objects.all().order_by("temperature_c", "pressure_psia")

    series = defaultdict(list)
    for point in points:
        series[point.temperature_c].append({"x": point.pressure_psia, "y": point.z_factor})

    # Sort temperatures and build one Chart.js dataset per isotherm
    datasets = []
    for temperature in sorted(series.keys()):
        datasets.append(
            {
                "label": f"{temperature:g} °C",
                "data": series[temperature],
            }
        )

    context = {
        "chart_data": datasets,
        "point_count": points.count(),
        "temperature_count": len(datasets),
        "min_pressure": points.order_by("pressure_psia").first().pressure_psia if points else None,
        "max_pressure": points.order_by("-pressure_psia").first().pressure_psia if points else None,
        "min_z": points.order_by("z_factor").first().z_factor if points else None,
        "max_z": points.order_by("-z_factor").first().z_factor if points else None,
    }
    return render(request, "chart/graph.html", context)


def zfactor_data_list(request):
    """
    Renders the complete, unaveraged dataset (349,784 rows extracted from all
    7 source CSVs) as a paginated, read-only table. Supports optional
    filtering by source file and temperature via query parameters, but there
    is no way to edit, add, or delete rows from this page.
    """
    rows = ZRawDataPoint.objects.all().order_by("id")

    source_file = request.GET.get("source_file", "").strip()
    temperature = request.GET.get("temperature", "").strip()
    outliers_only = request.GET.get("outliers_only", "").strip() == "1"

    if source_file:
        rows = rows.filter(source_file=source_file)
    if temperature:
        try:
            rows = rows.filter(temperature_c=float(temperature))
        except ValueError:
            pass
    if outliers_only:
        rows = rows.filter(is_outlier=True)

    total_all_rows = ZRawDataPoint.objects.count()
    total_filtered_rows = rows.count()

    paginator = Paginator(rows, 200)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    source_files = (
        ZRawDataPoint.objects.order_by("source_file")
        .values_list("source_file", flat=True)
        .distinct()
    )
    temperatures = (
        ZRawDataPoint.objects.order_by("temperature_c")
        .values_list("temperature_c", flat=True)
        .distinct()
    )

    # Preserve active filters across pagination links
    querydict = request.GET.copy()
    querydict.pop("page", None)
    base_query = querydict.urlencode()

    context = {
        "page_obj": page_obj,
        "total_all_rows": total_all_rows,
        "total_filtered_rows": total_filtered_rows,
        "outlier_total": ZRawDataPoint.objects.filter(is_outlier=True).count(),
        "source_files": source_files,
        "temperatures": temperatures,
        "selected_source_file": source_file,
        "selected_temperature": temperature,
        "outliers_only": outliers_only,
        "base_query": base_query,
    }
    return render(request, "chart/data_list.html", context)
