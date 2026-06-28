import sys
sys.path.append("src")
import unittest
import ipywidgets as widgets
from Panel import build_panel


class TestPanel(unittest.TestCase):

    def test_build_returns_vbox(self):
        panel, refs = build_panel()
        self.assertIsInstance(panel, widgets.VBox)

    def test_inventory(self):
        panel, refs = build_panel()

        speed = refs["cannonball_speed"]
        self.assertIsInstance(speed, widgets.BoundedFloatText)
        self.assertEqual(speed.min, 5)
        self.assertEqual(speed.max, 25)

        angle = refs["cannonball_angle"]
        self.assertIsInstance(angle, widgets.BoundedFloatText)
        self.assertEqual(angle.min, 0)
        self.assertEqual(angle.max, 30)

        integrator = refs["integrator"]
        self.assertIsInstance(integrator, widgets.Dropdown)
        self.assertIn("Verlet", integrator.options)
        self.assertIn("Euler", integrator.options)

        start_button = refs["start_button"]
        self.assertIsInstance(start_button, widgets.Button)

    def test_callback_calls_run(self):
        from unittest.mock import MagicMock, patch
        panel, refs = build_panel()

        fake_run = MagicMock()
        fake_render = MagicMock()

        with patch("Panel.run", fake_run), patch("Panel.render", fake_render):
            refs["start_button"].click()

        # run must have been called exactly once
        fake_run.assert_called_once()

        # run gets 6 arguments: cannon, integrator, duration, angle, speed, scale
        # speed is at index 4 — widget value is km/s, run expects m/s
        speed_received = fake_run.call_args[0][4]
        expected_speed = refs["cannonball_speed"].value * 1000
        self.assertEqual(speed_received, expected_speed)

    def test_error_handling(self):
        from unittest.mock import MagicMock, patch
        panel, refs = build_panel()

        # run throws an error — except must catch it and print "Fehler: ..."
        fake_run = MagicMock(side_effect=ValueError("defect"))

        with patch("Panel.run", fake_run):
            refs["start_button"].click()

        # collect everything printed to the output widget
        printed_text = ""
        for o in refs["output"].outputs:
            printed_text += o.get("text", "")

        self.assertIn("Fehler:", printed_text)


if __name__ == "__main__":
    unittest.main()









