
import os
import unittest
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class TestEnergyIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg.connect(
            host="127.0.0.1",
            port=5433,
            dbname="aethergrid",
            user="aethergrid",
            password=os.environ["POSTGRES_PASSWORD"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_building_count(self):
        result = self.conn.execute(
            "SELECT COUNT(*) FROM buildings"
        ).fetchone()[0]

        self.assertEqual(result, 3)

    def test_reading_count(self):
        result = self.conn.execute(
            "SELECT COUNT(*) FROM electricity_readings"
        ).fetchone()[0]

        self.assertEqual(result, 52580)

    def test_zero_readings(self):
        result = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM electricity_readings
            WHERE consumption_kwh = 0
            """
        ).fetchone()[0]

        self.assertEqual(result, 9984)

    def test_no_negative_consumption(self):
        result = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM electricity_readings
            WHERE consumption_kwh < 0
            """
        ).fetchone()[0]

        self.assertEqual(result, 0)

    def test_readings_per_building(self):
        expected = {
            "Panther_education_Rosalie": 17524,
            "Panther_education_Misty": 17524,
            "Panther_education_Mattie": 17532,
        }

        rows = self.conn.execute(
            """
            SELECT building_id, COUNT(*)
            FROM electricity_readings
            GROUP BY building_id
            """
        ).fetchall()

        actual = dict(rows)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
