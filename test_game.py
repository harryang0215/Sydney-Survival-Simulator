"""Regression checks for Sydney Survival Simulator (Week 10: Testing).

Run: python3 -m unittest -v test_game
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from game import Game, Player, WEEKLY_RENT, TOTAL_DAYS
from storage import SaveError, load_game, save_game


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(Player("Test Student"), seed=12345)

    def test_initial_state(self):
        self.assertEqual(self.game.day, 1)
        self.assertEqual(self.game.player.meals, 4)
        self.assertEqual(self.game.player.money, 1350)

    def test_study_changes_stats(self):
        self.game.perform_action("1")
        self.assertEqual(self.game.player.study, 24)
        self.assertEqual(self.game.player.energy, 74)

    def test_work_increases_money(self):
        self.game.perform_action("2")
        self.assertEqual(self.game.player.money, 1530)

    def test_groceries_need_money(self):
        self.game.player.money = 20
        with self.assertRaises(ValueError):
            self.game.perform_action("3")
        self.assertEqual(self.game.player.meals, 4)
        self.assertEqual(self.game.day, 1)

    def test_invalid_action_does_not_change_day(self):
        with self.assertRaises(ValueError):
            self.game.perform_action("x")
        self.assertEqual(self.game.day, 1)

    def test_trip_requires_valid_destination(self):
        with self.assertRaises(ValueError):
            self.game.perform_action("5", "9")

    def test_player_values_are_clamped(self):
        p = self.game.player
        p.change(energy=999, study=999, happiness=-999, meals=999)
        self.assertEqual((p.energy, p.study, p.happiness, p.meals),
                         (100, 100, 0, 12))

    def test_rent_every_seven_days(self):
        self.game.day = 7
        money_before = self.game.player.money
        messages = self.game.end_day()
        self.assertEqual(self.game.player.money, money_before - WEEKLY_RENT)
        self.assertIn("Weekly rent paid", " ".join(messages))
        self.assertEqual(self.game.day, 8)

    def test_no_food_hurts(self):
        self.game.player.meals = 0
        self.game.end_day()
        self.assertEqual(self.game.player.energy, 72)
        self.assertEqual(self.game.player.happiness, 59)

    def test_event_is_stable_after_loading(self):
        first = self.game.todays_event()
        duplicate = Game.from_dict(self.game.to_dict())
        self.assertEqual(first, duplicate.todays_event())

    def test_event_bad_option(self):
        from game import EVENTS
        with self.assertRaises(ValueError):
            self.game.apply_event(EVENTS[0], "3")

    def test_burnout(self):
        self.game.player.energy = 1
        self.game.perform_action("2")
        self.game.end_day()
        self.assertTrue(self.game.finished)
        self.assertIn("BURNOUT", self.game.ending)

    def test_30_day_winning_result(self):
        self.game.day = TOTAL_DAYS
        p = self.game.player
        p.study, p.energy, p.happiness, p.money, p.meals = 87, 45, 70, 650, 2
        self.game.end_day()
        self.assertTrue(self.game.finished)
        self.assertIn("THRIVING", self.game.ending)

    def test_tough_semester_result(self):
        self.game.day = TOTAL_DAYS
        self.game.player.study = 10
        self.game.end_day()
        self.assertIn("TOUGH SEMESTER", self.game.ending)

    def test_save_and_reload(self):
        self.game.perform_action("1")
        self.game.end_day()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "testsave.json"
            save_game(self.game, path)
            restored = load_game(path)
        self.assertEqual(restored.to_dict(), self.game.to_dict())

    def test_missing_save_file(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(SaveError):
                load_game(Path(folder) / "missing.json")

    def test_corrupt_save_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{not valid json}", encoding="utf-8")
            with self.assertRaises(SaveError):
                load_game(path)

    def test_full_thirty_day_playthrough(self):
        """Smoke test a legal strategy all the way to a winning ending."""
        game = Game(Player("Harry"), seed=2026)
        while not game.finished:
            p = game.player
            if p.meals <= 1 and p.money >= 65:
                action = "3"
            elif p.energy <= 34:
                action = "4"
            elif p.study < 74 and (game.day < 25 or game.day % 2):
                action = "1"
            elif p.money < 650:
                action = "2"
            elif p.happiness < 75:
                action = "5"
            else:
                action = "4"
            game.perform_action(action, "3" if action == "5" else None)
            event = game.todays_event()
            if event:
                choice = "1"
                if event["title"] == "Sydney Rainstorm":
                    choice = "1" if p.money >= 100 else "2"
                elif event["title"] == "Surprise Class Quiz":
                    choice = "1" if p.energy > 25 else "2"
                elif event["title"] == "Light Rail Delay":
                    choice = "2" if p.energy > 30 else "1"
                elif event["title"] == "Extra Cafe Shift":
                    choice = "1" if p.energy > 35 else "2"
                game.apply_event(event, choice)
            game.end_day()
        self.assertEqual(game.day, 30)
        self.assertIn("THRIVING IN SYDNEY", game.ending)

    def test_command_line_new_game_and_save(self):
        """Real console entry point starts and writes a resumable save."""
        script = Path(__file__).with_name("main.py")
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run(
                [sys.executable, str(script)],
                input="1\nHarry\n6\n4\n", text=True,
                capture_output=True, cwd=folder, timeout=10,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("Progress saved", run.stdout)
            self.assertTrue((Path(folder) / "sydney_save.json").exists())
            restored = load_game(Path(folder) / "sydney_save.json")
            self.assertEqual(restored.player.name, "Harry")

    def test_tampered_save_stats(self):
        data = self.game.to_dict()
        data["player"]["energy"] = "one hundred"
        with self.assertRaises(ValueError):
            Game.from_dict(data)


if __name__ == "__main__":
    unittest.main()
