import gzip
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from chart.models import ZRawDataPoint

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "zfactor_raw_data.json.gz"


class Command(BaseCommand):
    help = (
        "Loads every raw row (one per simulated composition/case, before averaging) from "
        "chart/data/zfactor_raw_data.json.gz into the ZRawDataPoint table. This is the "
        "complete, unaveraged dataset extracted from all 7 source CSVs (349,784 rows). "
        "The file is stored gzip-compressed (~4 MB instead of ~113 MB) so it stays well "
        "under GitHub's 100 MB per-file limit."
    )

    def handle(self, *args, **options):
        with gzip.open(DATA_FILE, "rt", encoding="utf-8") as f:
            rows = json.load(f)

        ZRawDataPoint.objects.all().delete()

        batch = []
        batch_size = 5000
        total = 0
        for row in rows:
            batch.append(
                ZRawDataPoint(
                    source_file=row["source_file"],
                    case_label=row.get("case_label"),
                    temperature_c=row["temperature_c"],
                    pressure_psia=row["pressure_psia"],
                    z_factor=row["z_factor"],
                    h2o_mole_frac=row.get("h2o_mole_frac"),
                    ch4_mole_frac=row.get("ch4_mole_frac"),
                    co2_mole_percent=row.get("co2_mole_percent"),
                    reduced_pressure=row.get("reduced_pressure"),
                    reduced_temperature=row.get("reduced_temperature"),
                    phase=row.get("phase"),
                    is_outlier=row.get("is_outlier", False),
                )
            )
            if len(batch) >= batch_size:
                ZRawDataPoint.objects.bulk_create(batch)
                total += len(batch)
                self.stdout.write(f"  ...{total} rows loaded")
                batch = []

        if batch:
            ZRawDataPoint.objects.bulk_create(batch)
            total += len(batch)

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {total} raw data rows into the database.")
        )
