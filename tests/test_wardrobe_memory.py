import importlib
import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import app
import config


SAVED_WARDROBE = {
    "items": [
        {
            "id": "saved_001",
            "name": "Emerald pleated trousers",
            "category": "bottoms",
            "colors": ["emerald"],
            "style_tags": ["preppy", "tailored"],
            "notes": "High waisted",
        },
        {
            "id": "saved_002",
            "name": "Cream canvas sneakers",
            "category": "shoes",
            "colors": ["cream"],
            "style_tags": ["casual"],
            "notes": None,
        },
    ]
}


class WardrobeMemoryTests(unittest.TestCase):
    def memory_module(self):
        spec = importlib.util.find_spec("utils.wardrobe_memory")
        self.assertIsNotNone(spec, "utils.wardrobe_memory is not implemented")
        return importlib.import_module("utils.wardrobe_memory")

    def test_remembered_wardrobe_survives_source_file_changes(self):
        memory = self.memory_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            saved = root / "memory" / "wardrobe.json"
            source.write_text(json.dumps(SAVED_WARDROBE), encoding="utf-8")

            imported = memory.remember_wardrobe(source, saved)
            source.write_text(json.dumps({"items": []}), encoding="utf-8")

            self.assertEqual(SAVED_WARDROBE, imported)
            self.assertEqual(SAVED_WARDROBE, memory.load_remembered_wardrobe(saved))

    def test_invalid_import_does_not_replace_existing_memory(self):
        memory = self.memory_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.json"
            malformed = root / "malformed.json"
            wrong_shape = root / "wrong-shape.json"
            wrong_item = root / "wrong-item.json"
            saved = root / "memory" / "wardrobe.json"
            valid.write_text(json.dumps(SAVED_WARDROBE), encoding="utf-8")
            malformed.write_text("not json", encoding="utf-8")
            wrong_shape.write_text(json.dumps({"items": "not a list"}), encoding="utf-8")
            invalid_item = json.loads(json.dumps(SAVED_WARDROBE))
            invalid_item["items"][0]["category"] = []
            wrong_item.write_text(json.dumps(invalid_item), encoding="utf-8")
            memory.remember_wardrobe(valid, saved)

            for source in (malformed, wrong_shape, wrong_item):
                with self.subTest(source=source.name):
                    with self.assertRaises(ValueError):
                        memory.remember_wardrobe(source, saved)
                    self.assertEqual(
                        SAVED_WARDROBE,
                        memory.load_remembered_wardrobe(saved),
                    )

    def test_missing_source_and_corrupt_memory_give_actionable_errors(self):
        memory = self.memory_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            saved = root / "memory" / "wardrobe.json"

            with self.assertRaisesRegex(ValueError, "not found"):
                memory.remember_wardrobe(root / "missing.json", saved)
            self.assertFalse(saved.exists())

            saved.parent.mkdir()
            saved.write_text("{bad", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "wardrobe forget"):
                memory.load_remembered_wardrobe(saved)

    def test_forget_removes_memory_and_reports_if_it_existed(self):
        memory = self.memory_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            saved = root / "memory" / "wardrobe.json"
            source.write_text(json.dumps(SAVED_WARDROBE), encoding="utf-8")
            memory.remember_wardrobe(source, saved)

            self.assertTrue(memory.forget_remembered_wardrobe(saved))
            self.assertIsNone(memory.load_remembered_wardrobe(saved))
            self.assertFalse(memory.forget_remembered_wardrobe(saved))

    def test_cli_uses_memory_unless_empty_override_is_set(self):
        self.assertTrue(
            hasattr(app, "_wardrobe_for_ask"),
            "app._wardrobe_for_ask is not implemented",
        )
        remembered = SAVED_WARDROBE

        with patch(
            "utils.wardrobe_memory.load_remembered_wardrobe",
            return_value=remembered,
        ) as load_memory:
            wardrobe, source = app._wardrobe_for_ask(False)
            empty_wardrobe, empty_source = app._wardrobe_for_ask(True)

        self.assertIs(remembered, wardrobe)
        self.assertEqual("remembered", source)
        self.assertEqual([], empty_wardrobe["items"])
        self.assertEqual("empty override", empty_source)
        load_memory.assert_called_once_with()

    def test_empty_override_does_not_erase_remembered_wardrobe(self):
        memory = self.memory_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            saved = root / "memory" / "wardrobe.json"
            source.write_text(json.dumps(SAVED_WARDROBE), encoding="utf-8")
            memory.remember_wardrobe(source, saved)

            with patch.object(config, "WARDROBE_MEMORY_PATH", saved):
                wardrobe, source_name = app._wardrobe_for_ask(True)

            self.assertEqual([], wardrobe["items"])
            self.assertEqual("empty override", source_name)
            self.assertEqual(SAVED_WARDROBE, memory.load_remembered_wardrobe(saved))

    def test_cli_returns_to_example_after_memory_is_forgotten(self):
        self.assertTrue(
            hasattr(app, "_wardrobe_for_ask"),
            "app._wardrobe_for_ask is not implemented",
        )

        with patch(
            "utils.wardrobe_memory.load_remembered_wardrobe",
            return_value=None,
        ):
            wardrobe, source = app._wardrobe_for_ask(False)

        self.assertEqual("example", source)
        self.assertGreater(len(wardrobe["items"]), 0)


class WardrobeCommandTests(unittest.TestCase):
    def test_parser_exposes_remember_show_and_forget_commands(self):
        handlers = (
            "cmd_wardrobe_remember",
            "cmd_wardrobe_show",
            "cmd_wardrobe_forget",
        )
        for handler in handlers:
            self.assertTrue(hasattr(app, handler), f"app.{handler} is not implemented")

        parser = app.build_parser()
        remember = parser.parse_args(["wardrobe", "remember", "closet.json"])
        show = parser.parse_args(["wardrobe", "show"])
        forget = parser.parse_args(["wardrobe", "forget"])

        self.assertIs(app.cmd_wardrobe_remember, remember.func)
        self.assertEqual("closet.json", remember.path)
        self.assertIs(app.cmd_wardrobe_show, show.func)
        self.assertIs(app.cmd_wardrobe_forget, forget.func)

    def test_commands_remember_show_and_forget_one_wardrobe(self):
        handlers = (
            "cmd_wardrobe_remember",
            "cmd_wardrobe_show",
            "cmd_wardrobe_forget",
        )
        for handler in handlers:
            self.assertTrue(hasattr(app, handler), f"app.{handler} is not implemented")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            saved = root / "memory" / "wardrobe.json"
            source.write_text(json.dumps(SAVED_WARDROBE), encoding="utf-8")
            output = StringIO()

            with patch.object(config, "WARDROBE_MEMORY_PATH", saved):
                with redirect_stdout(output):
                    app.cmd_wardrobe_remember(Namespace(path=str(source)))
                    app.cmd_wardrobe_show(Namespace())
                    app.cmd_wardrobe_forget(Namespace())

            text = output.getvalue()
            self.assertIn("Remembered 2 wardrobe items", text)
            self.assertIn("Emerald pleated trousers", text)
            self.assertIn("Forgot the remembered wardrobe", text)
            self.assertFalse(saved.exists())


if __name__ == "__main__":
    unittest.main()
