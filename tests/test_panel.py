import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
import unittest
import ipywidgets as widgets
from panel import build_panel


class TestPanel(unittest.TestCase):

    def setUp(self):
        # runs before every test — build panel once and store it
        self.panel, self.refs = build_panel()

    def test_build_returns_vbox(self):
        self.assertIsInstance(self.panel, widgets.VBox)

    def test_inventory(self):
        speed = self.refs["cannonball_speed"]
        self.assertIsInstance(speed, widgets.BoundedFloatText)
        self.assertEqual(speed.min, 5)
        self.assertEqual(speed.max, 25)

        angle = self.refs["cannonball_angle"]
        self.assertIsInstance(angle, widgets.BoundedFloatText)
        self.assertEqual(angle.min, 0)
        self.assertEqual(angle.max, 30)

        integrator = self.refs["integrator"]
        self.assertIsInstance(integrator, widgets.Dropdown)
        self.assertIn("Verlet", integrator.options)
        self.assertIn("Euler", integrator.options)

        start_button = self.refs["start_button"]
        self.assertIsInstance(start_button, widgets.Button)

    def test_callback_calls_run(self):
        from unittest.mock import MagicMock, patch

        fake_run = MagicMock()
        fake_render = MagicMock()

        with patch("panel.run", fake_run), patch("panel.render", fake_render):
            self.refs["start_button"].click()

        # run must have been called exactly once
        fake_run.assert_called_once()

        # run gets 6 arguments: cannon, integrator, duration, angle, speed, scale
        # speed is at index 4 — widget value is km/s, run expects m/s
        speed_received = fake_run.call_args[0][4]
        expected_speed = self.refs["cannonball_speed"].value * 1000
        self.assertEqual(speed_received, expected_speed)

    def test_error_handling(self):
        from unittest.mock import MagicMock, patch

        # run throws an error — except must catch it, kernel must survive
        fake_run = MagicMock(side_effect=ValueError("defect"))

        with patch("panel.run", fake_run):
            # this must not raise — if except works, click() returns normally
            try:
                self.refs["start_button"].click()
            except Exception:
                self.fail("on_start_clicked let the exception escape")

        # run was called and threw — if we get here, except caught it correctly
        fake_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
