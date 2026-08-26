# Z-Factor Isotherm Chart (Django)

A Django site with two read-only pages built from your CH4-CO2-H2O and
CO2-H2O PVT simulation datasets:

1. **Chart page (`/`)** — a locked Standing-Katz style chart: Z-factor (Y) vs
   Pressure (X), one isotherm line per temperature (28 isotherms, 15°C–150°C),
   built from 2,959 composition-averaged (T, P, Z) points.
2. **Complete Data Table (`/data/`)** — every single row extracted from all
   7 source CSVs, completely unaveraged: **349,784 rows**, paginated
   (200 rows/page) with filters by source file, temperature, and an
   "outliers only" toggle. Rows that were excluded from the chart's average
   (non-physical solver-glitch values) are flagged in red.

Both pages are strictly view-only — there are no forms, edit controls, or
ways to alter the underlying data from the site itself.

## Data accounting

| | |
|---|---|
| Raw rows extracted from all 7 source files | 349,784 |
| Rows flagged as non-physical outliers (excluded from chart average) | 2,236 |
| Clean rows averaged into the chart | 347,548 |
| Resulting averaged (T, P, Z) points on the chart | 2,959 |

Every row from every file is preserved and viewable on the Complete Data
Table page — nothing was discarded, only clearly flagged where it was
excluded from the chart average.

## Project layout

```
zfactor_site/
├── manage.py
├── requirements.txt
├── db.sqlite3              # Pre-loaded with both tables — ready to run immediately
├── zfactor_site/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── chart/                   # The single app powering both pages
    ├── models.py             # ZFactorPoint (averaged) + ZRawDataPoint (complete raw rows)
    ├── views.py              # zfactor_chart (graph) + zfactor_data_list (paginated table)
    ├── urls.py
    ├── data/
    │   ├── zfactor_data.json       # Averaged dataset (2,959 points) — source for the chart
    │   └── zfactor_raw_data.json   # Complete raw dataset (349,784 rows) — source for the table
    ├── management/commands/
    │   ├── load_zfactor_data.py       # Loads zfactor_data.json into ZFactorPoint
    │   └── load_raw_zfactor_data.py   # Loads zfactor_raw_data.json into ZRawDataPoint
    ├── static/chart/js/
    │   └── chart.umd.min.js       # Chart.js, served locally
    └── templates/chart/
        ├── graph.html              # Chart page
        └── data_list.html          # Complete data table page
```

## Project layout

```
zfactor_site/
├── manage.py
├── requirements.txt
├── .gitignore               # Excludes db.sqlite3, venv/, __pycache__ from git
├── zfactor_site/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── chart/                   # The single app powering both pages
    ├── models.py             # ZFactorPoint (averaged) + ZRawDataPoint (complete raw rows)
    ├── views.py              # zfactor_chart (graph) + zfactor_data_list (paginated table)
    ├── urls.py
    ├── data/
    │   ├── zfactor_data.json           # Averaged dataset (2,959 points) — source for the chart
    │   └── zfactor_raw_data.json.gz    # Complete raw dataset (349,784 rows), gzip-compressed
    ├── management/commands/
    │   ├── load_zfactor_data.py       # Loads zfactor_data.json into ZFactorPoint
    │   └── load_raw_zfactor_data.py   # Loads zfactor_raw_data.json.gz into ZRawDataPoint
    ├── static/chart/js/
    │   └── chart.umd.min.js       # Chart.js, served locally
    └── templates/chart/
        ├── graph.html              # Chart page
        └── data_list.html          # Complete data table page
```

Note: `db.sqlite3` is **not** committed to git (it's in `.gitignore`, as is
standard Django practice) — you generate it locally with the commands below.
The raw dataset is stored gzip-compressed (`zfactor_raw_data.json.gz`, ~4 MB)
instead of raw JSON (~113 MB), since GitHub rejects any single file over
100 MB — the loader command reads the `.gz` file directly.

## Setup

```bash
cd zfactor_site
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py load_zfactor_data        # loads the 2,959 averaged points
python manage.py load_raw_zfactor_data    # loads all 349,784 raw rows (~15-25s)
python manage.py runserver
```

Then open http://127.0.0.1:8000/ for the chart, or
http://127.0.0.1:8000/data/ for the complete data table.

## Pushing this to GitHub

If you're publishing this repo, the two load commands above are what
(re)build `db.sqlite3` on any machine — nobody needs the database file
itself in git. Since `db.sqlite3` and `__pycache__/` are already in
`.gitignore`, a normal `git add . && git commit && git push` will only ever
send source files plus the small gzipped dataset (~4 MB total), well under
GitHub's per-file and repo-size limits.

If you already have a local commit that included the old, uncompressed
`zfactor_raw_data.json` (113 MB) and GitHub rejected the push, that large
blob is stuck in your local git history even after you delete the file —
removing it from the working directory alone won't fix the push. Easiest
fix if this is a brand-new project (nothing has successfully pushed yet):

```bash
# from inside the zfactor_site folder, with the fixed files in place
rmdir /s /q .git          # Windows;  use `rm -rf .git` on macOS/Linux
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Tordi-portfolio/sir_anyanimeh.git
git push -u origin main
```

This starts a clean history with only the fixed (small) files, so the push
should succeed.

## How the data was built

The seven source CSVs (six CH4-CO2-H2O simulation exports across pressure
bands from 14.7 to 10,000 psia, plus one CO2-H2O dataset) were parsed in
full — every row from every file, including the double-column-block file,
was extracted (349,784 rows total, verified against each file's exact line
count).

A small number of rows (2,236) had non-physical Z values (e.g. -32,770)
caused by solver failures near certain critical-point conditions in the
simulation software — these are kept in the raw table but flagged
`is_outlier = True`, and excluded only from the chart's averaged isotherms.

The remaining 347,548 rows were grouped by (Temperature, Pressure) and
averaged across all simulated gas compositions, producing the 2,959 clean
points used for the isotherm chart.

## Changing the chart's or table's look

All styling lives inline in each template (`graph.html`, `data_list.html`)
as `<style>` blocks and inline `<script>` — there's no separate CSS/JS asset
pipeline to manage.
