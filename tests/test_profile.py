"""Regression checks for accurate counts and refreshing GitHub image URLs."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("builder", Path(__file__).resolve().parents[1] / "scripts/build_assets.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ProfileTests(unittest.TestCase):
    def test_first_calendar_day_is_not_lost_from_count(self):
        days = [{"date": "2025-10-05", "count": 7, "level": 4},
                {"date": "2026-10-05", "count": 2, "level": 1}]
        svg = builder.calendar(builder.PALETTE, days, "2026-10-05T12:00:00Z")
        root = ET.fromstring(svg)
        cells = [node for node in root.iter() if node.attrib.get("class") == "reveal"]
        self.assertEqual(len(cells), 2)
        self.assertIn("9 GitHub contributions", svg)
        self.assertIn("UPDATED 05 OCT 2026 12:00 UTC", svg)

    def test_image_url_changes_with_graphic_and_does_not_accumulate_queries(self):
        original = '<p><img src="assets/contributions-dark.svg?v=old" width="100%"></p>'
        first = builder.version_calendar_image(original, "first graphic")
        self.assertEqual(first, builder.version_calendar_image(first, "first graphic"))
        second = builder.version_calendar_image(first, "updated graphic")
        self.assertNotEqual(first, second)
        self.assertEqual(second.count("?v="), 1)
        self.assertIn('width="100%"', second)

    def test_upstream_failure_does_not_become_an_empty_calendar(self):
        parser = builder.CalendarParser()
        parser.feed("<html>Service unavailable</html>")
        with self.assertRaises(ValueError):
            parser.days()

    def test_refuse_to_publish_a_graph_with_no_readme_reference(self):
        with self.assertRaises(ValueError):
            builder.version_calendar_image("<p>No calendar</p>", "graphic")


if __name__ == "__main__":
    unittest.main()
