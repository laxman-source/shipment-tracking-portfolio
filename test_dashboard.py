"""Check the demo data and dashboard using Python's built-in unittest runner."""

from pathlib import Path
import tempfile
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from app import DATA_PATH, calculate_kpis, delivery_performance, load_shipments


class ShipmentDataTests(unittest.TestCase):
    def test_sample_counts_and_performance(self):
        shipments = load_shipments()
        self.assertEqual(list(calculate_kpis(shipments).values()), [20, 10, 6, 4])
        self.assertEqual(shipments["shipment_id"].nunique(), 20)
        self.assertEqual(delivery_performance(shipments)["Shipments"].tolist(), [8, 2])

    def test_due_today_is_in_transit_and_late_deliveries_are_delivered(self):
        shipments = load_shipments().set_index("shipment_id")
        self.assertEqual(shipments.loc["DEMO-011", "status"], "In Transit")
        self.assertEqual(shipments.loc["DEMO-009", "status"], "Delivered")
        self.assertGreater(
            shipments.loc["DEMO-009", "actual_delivery_date"],
            shipments.loc["DEMO-009", "eta"],
        )

    def test_inconsistent_status_is_rejected(self):
        raw = pd.read_csv(DATA_PATH)
        raw.loc[0, "status"] = "Delayed"
        with tempfile.TemporaryDirectory(dir=DATA_PATH.parent) as folder:
            path = Path(folder) / "invalid.csv"
            raw.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "statuses do not match"):
                load_shipments(path)


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(DATA_PATH.parent.parent / "app.py")).run(timeout=30)
        self.assertFalse(self.app.exception)

    def test_default_view(self):
        self.assertEqual([metric.value for metric in self.app.metric], ["20", "10", "6", "4", "80%"])
        self.assertEqual(len(self.app.dataframe[0].value), 20)
        self.assertEqual(self.app.warning[0].value, "Portfolio Demo — Fictional Data")

    def test_status_filters(self):
        for status, expected in [
            ("Delivered", ["10", "10", "0", "0", "80%"]),
            ("In Transit", ["6", "0", "6", "0"]),
            ("Delayed", ["4", "0", "0", "4"]),
        ]:
            with self.subTest(status=status):
                self.app.sidebar.multiselect[0].set_value([status]).run()
                self.assertFalse(self.app.exception)
                self.assertEqual([metric.value for metric in self.app.metric], expected)
                self.assertEqual(len(self.app.dataframe[0].value), int(expected[0]))

    def test_empty_selection_and_restore(self):
        self.app.sidebar.multiselect[0].set_value([]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual([metric.value for metric in self.app.metric], ["0"] * 4)
        self.assertEqual(len(self.app.dataframe), 0)
        self.app.sidebar.multiselect[0].set_value(["Delivered", "In Transit", "Delayed"]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.metric[0].value, "20")


if __name__ == "__main__":
    unittest.main()
