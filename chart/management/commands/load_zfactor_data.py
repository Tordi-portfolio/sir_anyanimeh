import json
from pathlib import Path

from django.core.management.base import BaseCommand

from chart.models import ZFactorPoint

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "zfactor_data.json"


class Command(BaseCommand):
    help = (
        "Loads the averaged (Temperature, Pressure, Z) data points, extracted from the "
        "CH4-CO2-H2O / CO2-H2O simulation CSV files, into the ZFactorPoint table."
    )

    def handle(self, *args, **options):
        with open(DATA_FILE) as f:
            rows = json.load(f)

        ZFactorPoint.objects.all().delete()

        objs = [
            ZFactorPoint(
                temperature_c=row["T"],
                pressure_psia=row["P"],
                z_factor=row["Z"],
                sample_count=row.get("n", 1),
            )
            for row in rows
        ]

        ZFactorPoint.objects.bulk_create(objs, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(objs)} Z-factor data points into the database.")
        )
