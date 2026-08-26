from django.db import models


class ZFactorPoint(models.Model):
    """
    A single averaged (Temperature, Pressure, Z) data point derived from the
    CH4-CO2-H2O and CO2-H2O simulation datasets.

    Each point represents the Z-factor averaged across every simulated
    composition (Case 1, Case 2, ...) that shares the same temperature and
    pressure, so the chart shows one clean isotherm line per temperature
    instead of a noisy cloud of composition-specific points.
    """

    temperature_c = models.FloatField(help_text="Temperature in degrees Celsius")
    pressure_psia = models.FloatField(help_text="Pressure in psia")
    z_factor = models.FloatField(help_text="Compressibility factor (Z), averaged across compositions")
    sample_count = models.PositiveIntegerField(
        default=1, help_text="Number of raw simulation rows averaged into this point"
    )

    class Meta:
        ordering = ["temperature_c", "pressure_psia"]
        indexes = [
            models.Index(fields=["temperature_c"]),
            models.Index(fields=["pressure_psia"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["temperature_c", "pressure_psia"], name="unique_temperature_pressure_point"
            )
        ]

    def __str__(self):
        return f"T={self.temperature_c}C, P={self.pressure_psia}psia, Z={self.z_factor}"


class ZRawDataPoint(models.Model):
    """
    A single, untouched row extracted directly from the source simulation
    CSVs — one row per simulated composition/case, before any averaging.

    This is the complete dataset (349,784 rows across all 7 source files),
    kept exactly as it appears in the original data. The averaged
    ZFactorPoint table (used for the chart) is derived from this table by
    grouping on (temperature_c, pressure_psia) and averaging z_factor,
    after excluding rows flagged here as is_outlier.
    """

    source_file = models.CharField(max_length=255, help_text="Original CSV file this row came from")
    case_label = models.CharField(max_length=64, blank=True, null=True, help_text="Case/row label from the source file, e.g. 'Case 1042'")
    temperature_c = models.FloatField(help_text="Temperature in degrees Celsius")
    pressure_psia = models.FloatField(help_text="Pressure in psia")
    z_factor = models.FloatField(help_text="Compressibility factor (Z) as reported in the source row")
    h2o_mole_frac = models.FloatField(blank=True, null=True, help_text="H2O mole fraction (master composition or x_H2O)")
    ch4_mole_frac = models.FloatField(blank=True, null=True, help_text="Methane mole fraction (master composition)")
    co2_mole_percent = models.FloatField(blank=True, null=True, help_text="CO2 composition, mole %")
    reduced_pressure = models.FloatField(blank=True, null=True, help_text="Pr, reduced pressure (CCS dataset only)")
    reduced_temperature = models.FloatField(blank=True, null=True, help_text="Tr, reduced temperature (CCS dataset only)")
    phase = models.CharField(max_length=32, blank=True, null=True, help_text="Reported phase (CCS dataset only)")
    is_outlier = models.BooleanField(
        default=False,
        help_text="True if Z fell outside a physically plausible range (a simulator solver-glitch row), excluded from the averaged chart",
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["temperature_c"]),
            models.Index(fields=["pressure_psia"]),
            models.Index(fields=["source_file"]),
            models.Index(fields=["is_outlier"]),
        ]

    def __str__(self):
        return f"{self.case_label or self.id} — T={self.temperature_c}C, P={self.pressure_psia}psia, Z={self.z_factor}"
