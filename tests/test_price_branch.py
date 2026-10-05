import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import agent
import app
import tools
from utils.data_loader import get_example_wardrobe, load_listings


class ComparePriceTests(unittest.TestCase):
    def test_compares_listing_with_other_items_in_its_category(self):
        item = next(listing for listing in load_listings() if listing["id"] == "lst_002")
        compare_price = getattr(tools, "compare_price", None)

        self.assertIsNotNone(compare_price, "tools.compare_price is not implemented")
        with patch.object(tools, "generate") as generate:
            result = compare_price(item)

        generate.assert_not_called()
        self.assertEqual("below_median", result["status"])
        self.assertEqual("tops", result["category"])
        self.assertEqual(18.0, result["item_price"])
        self.assertEqual(21.5, result["median_price"])
        self.assertEqual(-3.5, result["difference"])
        self.assertEqual(14, result["comparable_count"])
        self.assertIn("$18.00", result["message"])
        self.assertIn("$21.50", result["message"])

    def test_returns_unavailable_when_comparison_cannot_be_calculated(self):
        compare_price = getattr(tools, "compare_price", None)
        self.assertIsNotNone(compare_price, "tools.compare_price is not implemented")

        cases = (
            {"id": "missing-price", "category": "tops"},
            {"id": "missing-category", "price": 20.0},
            {"id": "no-comparables", "category": "costumes", "price": 20.0},
        )
        for item in cases:
            with self.subTest(item=item):
                result = compare_price(item)
                self.assertEqual("unavailable", result["status"])
                self.assertIsNone(result["median_price"])
                self.assertIsNone(result["difference"])
                self.assertEqual(0, result["comparable_count"])
                self.assertTrue(result["message"].strip())


class PriceBranchTests(unittest.TestCase):
    def setUp(self):
        self.wardrobe = get_example_wardrobe()
        self.first, self.second = load_listings()[:2]

    def test_empty_search_stops_before_price_and_model_tools(self):
        with (
            patch.object(agent, "search_listings", return_value=[]),
            patch.object(agent, "compare_price", create=True) as compare,
            patch.object(agent, "suggest_outfit") as suggest,
            patch.object(agent, "create_fit_card") as create,
        ):
            session = agent.run_agent("nothing matches", self.wardrobe)

        self.assertIsNone(session.get("price_comparison"))
        self.assertIsNone(session["fit_card"])
        self.assertIsNotNone(session["error"])
        compare.assert_not_called()
        suggest.assert_not_called()
        create.assert_not_called()

    def test_one_match_skips_price_tool_and_keeps_first_result(self):
        with (
            patch.object(agent, "search_listings", return_value=[self.first]),
            patch.object(agent, "compare_price", create=True) as compare,
            patch.object(agent, "suggest_outfit", return_value="saved outfit") as suggest,
            patch.object(agent, "create_fit_card", return_value="saved card") as create,
        ):
            session = agent.run_agent("argyle", self.wardrobe)

        self.assertIs(self.first, session["selected_item"])
        self.assertEqual("skipped_single_match", session["price_comparison"]["status"])
        self.assertIn("one listing", session["price_comparison"]["message"].lower())
        compare.assert_not_called()
        suggest.assert_called_once_with(self.first, self.wardrobe)
        create.assert_called_once_with("saved outfit", self.first)

    def test_multiple_matches_call_price_tool_and_keep_first_result(self):
        comparison = {
            "status": "below_median",
            "category": "tops",
            "item_price": 18.0,
            "median_price": 21.5,
            "difference": -3.5,
            "comparable_count": 14,
            "message": "comparison",
        }
        with (
            patch.object(agent, "search_listings", return_value=[self.first, self.second]),
            patch.object(
                agent, "compare_price", return_value=comparison, create=True
            ) as compare,
            patch.object(agent, "suggest_outfit", return_value="saved outfit") as suggest,
            patch.object(agent, "create_fit_card", return_value="saved card") as create,
        ):
            session = agent.run_agent("vintage tee", self.wardrobe)

        self.assertIs(self.first, session["selected_item"])
        self.assertIs(comparison, session["price_comparison"])
        compare.assert_called_once_with(self.first)
        suggest.assert_called_once_with(self.first, self.wardrobe)
        create.assert_called_once_with("saved outfit", self.first)


class PriceOutputTests(unittest.TestCase):
    def setUp(self):
        item = load_listings()[0]
        self.session = agent.new_session("vintage jacket", get_example_wardrobe())
        self.session.update(
            {
                "selected_item": item,
                "price_comparison": {"message": "This is the saved price comparison."},
                "outfit_suggestion": "saved outfit",
                "fit_card": "saved card",
            }
        )

    def test_agent_direct_output_prints_price_comparison(self):
        output = StringIO()

        with redirect_stdout(output):
            agent._show(self.session)

        self.assertIn("price", output.getvalue().casefold())
        self.assertIn("This is the saved price comparison.", output.getvalue())

    def test_app_output_prints_price_comparison(self):
        output = StringIO()

        with patch.object(agent, "run_agent", return_value=self.session):
            with redirect_stdout(output):
                returned = app._ask_one("vintage jacket", self.session["wardrobe"], False)

        self.assertIs(self.session, returned)
        self.assertIn("price", output.getvalue().casefold())
        self.assertIn("This is the saved price comparison.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
