# Shipment Tracking Portfolio

**Portfolio Demo — Fictional Data**

A beginner-friendly supply chain dashboard built with Python, Streamlit, and pandas. It runs on your computer and reads 20 invented shipments from a local CSV file. All carriers and shipment IDs are fictional; city names are illustrative. There is no real company information.

## What you can do

- See total, delivered, in-transit, and delayed shipment counts.
- Filter by one or more statuses and inspect the tracking table.
- Compare on-time and late completed deliveries in a bar chart.
- See the on-time delivery rate and read the metric definitions inside the app.

All cards, the table, and the chart follow the status filter. Clearing the filter shows zero counts and a helpful empty-selection message.

## What each file does

| File | Purpose in simple English |
| --- | --- |
| `app.py` | Reads and checks the sample data, calculates the numbers, and draws the dashboard. |
| `requirements.txt` | Lists the two free Python packages needed to run the app. |
| `data/demo_shipments.csv` | Holds the 20 fictional shipments in a spreadsheet-style text file. |
| `README.md` | Contains these setup instructions and explains the business rules. |
| `.gitignore` | Tells Git which temporary and local files to ignore if you choose to use Git later. It does not initialize Git or publish anything. |
| `.streamlit/config.toml` | Turns off Streamlit usage statistics, restricts the server to this computer, and sets the dashboard colors. |
| `test_dashboard.py` | Checks the sample calculations, status rules, dashboard filters, and empty selection automatically. |



## How to run this project

1. Install Python 3.11 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install the required packages:

```bash
python -m pip install -r requirements.txt
```

5. Start the dashboard:

```bash
python -m streamlit run app.py
```

6. Open http://localhost:8501 in your browser.

This project uses fictional shipment data and requires no API keys or external accounts.



## Business rules and expected results

This is a fixed snapshot as of **11 November 2026**, not a live tracking service. Using a fixed date keeps the portfolio reproducible. The app does not contact carriers or update shipment records automatically.

| Metric with all statuses selected | Expected value |
| --- | ---: |
| Total shipments | 20 |
| Delivered shipments | 10 |
| In-transit shipments | 6 |
| Delayed shipments | 4 |
| Completed deliveries on time | 8 |
| Completed deliveries late | 2 |
| On-time delivery rate | 80% |

**Delivered** means an actual delivery date exists. **Delayed** means there is no actual delivery date and ETA is earlier than the snapshot date. **In Transit** means there is no actual delivery date and ETA is on or after the snapshot date. An undelivered shipment due on the snapshot date is still in transit.

Each shipment belongs to exactly one status, so 10 + 6 + 4 = 20. A completed late delivery belongs to Delivered, and contributes to Late in the performance chart. It does not count in the delayed card, which tracks outstanding overdue shipments.

On time means actual delivery date is on or before ETA. The rate is 8 / 10 × 100 = 80%. Outstanding shipments are excluded from that rate because their delivery outcome is not known.

Dates use calendar-day precision. Last-update timestamps are fictional local times; no timezone conversions are performed.

## Edit the sample data

Open `data/demo_shipments.csv` in a text editor or spreadsheet program. Keep the column headers unchanged. Use `YYYY-MM-DD` for ETA and delivery dates, and `YYYY-MM-DD HH:MM` for last update. Leave actual delivery date empty for undelivered shipments. Use only `Delivered`, `In Transit`, or `Delayed` for status, consistent with the rules above. Use unique shipment IDs and fictional data only.

The app checks required columns, missing values, unique IDs, date formats, and whether statuses match the dates. Refresh the browser after saving edits. To intentionally change the snapshot date, edit `DEMO_DATE` in `app.py` and update the displayed date, CSV statuses, and documentation to agree.

## Quick manual checks

1. Open the dashboard with all statuses selected: expect cards of **20, 10, 6, 4**, 20 table rows, an **80%** rate, and chart counts of **8 on time / 2 late**.
2. Select only **Delayed**: expect **4, 0, 0, 4**, four rows, and a message explaining there are no delivered shipments to chart.
3. Select only **Delivered**: expect **10, 10, 0, 0**, ten rows, and the same **80%** rate.
4. Clear all statuses: expect four zero cards and helpful messages instead of an error.
5. Select all statuses to restore the original view.

Run the automated checks from the project folder with:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_dashboard
```

These checks use Streamlit's built-in app testing tools and Python's standard test runner. No extra testing package or external account is needed.

Verified during setup with Python 3.12.16, Streamlit 1.67.0, and pandas 2.3.3:

- All six automated tests passed, covering data calculations, status rules, invalid data, filters, and empty selections.
- An independent CSV count confirmed 20 total, 10 delivered, 6 in transit, 4 delayed, and 8 of 10 delivered on time.
- The actual Streamlit server started successfully; its health endpoint and dashboard page returned HTTP 200. The temporary test server was stopped afterwards.
- Python's package check found no broken requirements. Local-only access and disabled usage statistics were verified.

## Independence and privacy

There are no Google Drive connections, Slack webhooks, external tracking APIs, credentials, or account requirements. The only data input is this project's local CSV. Streamlit usage statistics are disabled in the project configuration. No original ShipmentTracker or ClearUp files are needed or imported. No Git setup, commit, or push is required to run the dashboard.
