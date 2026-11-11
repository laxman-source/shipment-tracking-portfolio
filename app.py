"""A local shipment dashboard using only fictional CSV data."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "data" / "demo_shipments.csv"
DEMO_DATE = pd.Timestamp("2026-11-11")
STATUSES = ["Delivered", "In Transit", "Delayed"]


def load_shipments(path=DATA_PATH):
    """Read the CSV and check that dates and shipment statuses agree."""
    shipments = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = [
        "shipment_id", "carrier", "origin", "destination", "eta",
        "actual_delivery_date", "status", "last_update",
    ]
    missing = set(required) - set(shipments.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")
    shipments = shipments[required].copy()
    for column in required:
        if column != "actual_delivery_date" and shipments[column].str.strip().eq("").any():
            raise ValueError(f"The {column} column contains a blank value.")
    if shipments["shipment_id"].duplicated().any():
        raise ValueError("Each shipment ID must be unique.")
    for column in ["eta", "actual_delivery_date"]:
        shipments[column] = pd.to_datetime(
            shipments[column].replace("", None), format="%Y-%m-%d", errors="raise"
        )
    shipments["last_update"] = pd.to_datetime(
        shipments["last_update"], format="%Y-%m-%d %H:%M", errors="raise"
    )
    if not shipments["status"].isin(STATUSES).all():
        raise ValueError("Status must be Delivered, In Transit, or Delayed.")
    if (shipments["actual_delivery_date"] > DEMO_DATE).any():
        raise ValueError("Actual delivery dates cannot be after the demo date.")
    if (shipments["last_update"].dt.normalize() > DEMO_DATE).any():
        raise ValueError("Last updates cannot be after the demo date.")
    expected_status = pd.Series("In Transit", index=shipments.index)
    expected_status.loc[shipments["eta"] < DEMO_DATE] = "Delayed"
    expected_status.loc[shipments["actual_delivery_date"].notna()] = "Delivered"
    if not shipments["status"].eq(expected_status).all():
        raise ValueError("Shipment statuses do not match the dates and demo date.")
    return shipments


def calculate_kpis(shipments):
    """Count each mutually exclusive shipment status."""
    return {
        "Total shipments": len(shipments),
        "Delivered shipments": int(shipments["status"].eq("Delivered").sum()),
        "In-transit shipments": int(shipments["status"].eq("In Transit").sum()),
        "Delayed shipments": int(shipments["status"].eq("Delayed").sum()),
    }


def delivery_performance(shipments):
    """Compare completed deliveries with their promised ETA dates."""
    delivered = shipments.loc[shipments["status"].eq("Delivered")]
    on_time = int(delivered["actual_delivery_date"].le(delivered["eta"]).sum())
    return pd.DataFrame({
        "Delivery result": ["On time", "Late"],
        "Shipments": [on_time, len(delivered) - on_time],
    }).set_index("Delivery result")


def main():
    st.set_page_config(page_title="Shipment Tracking | Portfolio Demo", page_icon="📦", layout="wide")
    st.title("Shipment Tracking Dashboard")
    st.warning("Portfolio Demo — Fictional Data")
    st.caption(
        "Supply chain portfolio project • Fixed snapshot: 11 November 2026 • "
        "All shipment IDs and carriers are invented. Locations are illustrative."
    )

    try:
        shipments = load_shipments()
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Unable to load demo shipments: {error}")
        st.info("Check data/demo_shipments.csv and the CSV instructions in README.md.")
        st.stop()

    st.sidebar.header("Shipment filters")
    selected = st.sidebar.multiselect("Status", STATUSES, default=STATUSES)
    st.sidebar.caption("Clear all statuses to show an empty selection. Select all to restore the full demo.")
    st.sidebar.info("Local CSV only. No accounts, credentials, external APIs, or live tracking.")
    filtered = shipments.loc[shipments["status"].isin(selected)]

    st.subheader("Shipment overview")
    st.caption(f"Showing {len(filtered)} of {len(shipments)} shipments. Cards, table, and chart follow the status filter.")
    for column, (label, value) in zip(st.columns(4), calculate_kpis(filtered).items()):
        column.metric(label, value)

    st.subheader("Shipment tracking")
    if filtered.empty:
        st.info("No shipments selected. Choose at least one status in the sidebar.")
    else:
        display = filtered.sort_values(["eta", "shipment_id"]).copy()
        for column in ["eta", "actual_delivery_date"]:
            display[column] = display[column].dt.strftime("%Y-%m-%d").fillna("—")
        display["last_update"] = display["last_update"].dt.strftime("%Y-%m-%d %H:%M")
        display = display.rename(columns={
            "shipment_id": "Shipment ID", "carrier": "Carrier", "origin": "Origin",
            "destination": "Destination", "eta": "ETA",
            "actual_delivery_date": "Actual delivery date", "status": "Status",
            "last_update": "Last update",
        })
        st.dataframe(display, hide_index=True, width="stretch")

    st.subheader("Delivery performance")
    performance = delivery_performance(filtered)
    completed = int(performance["Shipments"].sum())
    if completed:
        on_time = int(performance.loc["On time", "Shipments"])
        st.metric("On-time delivery rate", f"{on_time / completed:.0%}")
        st.caption(f"{on_time} of {completed} delivered shipments arrived on or before their ETA.")
        st.bar_chart(performance, y="Shipments", color="#148A80", height=300)
    else:
        st.info("No delivered shipments in this selection. Select Delivered to see performance.")

    with st.expander("How the metrics work"):
        st.markdown(
            "- **Delivered:** an actual delivery date is recorded, even if delivery was late.\n"
            "- **In Transit:** no actual delivery date and ETA is on or after 11 November 2026.\n"
            "- **Delayed:** no actual delivery date and ETA is before 11 November 2026.\n"
            "- **On time:** actual delivery date is on or before ETA.\n"
            "- **On-time delivery rate:** on-time deliveries divided by all delivered shipments.\n\n"
            "The three statuses are mutually exclusive. A completed late delivery counts as "
            "Delivered in the cards and Late in the chart. Dates are interpreted at calendar-day "
            "precision; last-update times are fictional local times without timezone conversion. "
            "The snapshot date is fixed so the portfolio results do not change tomorrow."
        )


if __name__ == "__main__":
    main()
