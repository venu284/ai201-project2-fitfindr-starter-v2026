import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import call, patch

import agent
import trace
from generate import ModelUnavailable
from utils.data_loader import get_example_wardrobe, load_listings


class AgentFailureAndTraceTests(unittest.TestCase):
    def setUp(self):
        self.item = load_listings()[0]
        self.wardrobe = get_example_wardrobe()

    def test_model_failure_at_outfit_returns_actionable_session_error(self):
        with (
            patch.object(agent, "call_tool", return_value=[self.item]),
            patch.object(agent, "suggest_outfit", side_effect=ModelUnavailable("bad key")),
            patch.object(agent, "create_fit_card") as create,
        ):
            session = agent.run_agent("vintage jeans", self.wardrobe)

        self.assertIn("model", session["error"].lower())
        self.assertIn("key", session["error"].lower())
        self.assertIn("try again", session["error"].lower())
        self.assertIsNone(session["outfit_suggestion"])
        self.assertIsNone(session["fit_card"])
        create.assert_not_called()

    def test_model_failure_at_fit_card_returns_actionable_session_error(self):
        with (
            patch.object(agent, "call_tool", return_value=[self.item]),
            patch.object(agent, "suggest_outfit", return_value="saved outfit"),
            patch.object(agent, "create_fit_card", side_effect=ModelUnavailable("bad key")),
        ):
            session = agent.run_agent("vintage jeans", self.wardrobe)

        self.assertIn("model", session["error"].lower())
        self.assertIn("try again", session["error"].lower())
        self.assertEqual("saved outfit", session["outfit_suggestion"])
        self.assertIsNone(session["fit_card"])

    def test_trace_shows_mcp_and_every_called_tool_in_order(self):
        comparison = {"status": "below_median", "message": "below median"}
        with (
            patch.object(
                agent,
                "call_tool",
                side_effect=(load_listings()[:2], comparison),
            ) as mcp,
            patch.object(agent, "suggest_outfit", return_value="saved outfit"),
            patch.object(agent, "create_fit_card", return_value="saved card"),
            redirect_stdout(StringIO()),
        ):
            trace.start_trace()
            agent.run_agent("vintage jeans under $40", self.wardrobe)
            output = trace.get_trace()

        self.assertIn("description='vintage jeans'", output)
        self.assertIn("max_price=40.0", output)
        self.assertLess(
            output.index("search_listings (via MCP)"),
            output.index("compare_price (via MCP)"),
        )
        self.assertLess(output.index("compare_price (via MCP)"), output.index("suggest_outfit"))
        self.assertLess(output.index("suggest_outfit"), output.index("create_fit_card"))
        self.assertIn(self.wardrobe["items"][0]["name"], output)
        self.assertIn("saved card", output)
        self.assertEqual(
            [
                call(
                    "search_listings",
                    {
                        "description": "vintage jeans",
                        "size": None,
                        "max_price": 40.0,
                    },
                ),
                call("compare_price", {"new_item": load_listings()[0]}),
            ],
            mcp.call_args_list,
        )

    def test_trace_does_not_print_without_opt_in(self):
        with (
            patch.object(agent, "call_tool", return_value=[self.item]),
            patch.object(agent, "suggest_outfit", return_value="saved outfit"),
            patch.object(agent, "create_fit_card", return_value="saved card"),
            redirect_stdout(StringIO()) as output,
        ):
            agent.run_agent("vintage jeans", self.wardrobe)

        self.assertEqual("", output.getvalue())

    def test_empty_search_trace_stops_before_model_tools(self):
        with (
            patch.object(agent, "call_tool", return_value=[]),
            patch.object(agent, "suggest_outfit") as suggest,
            redirect_stdout(StringIO()),
        ):
            trace.start_trace()
            session = agent.run_agent("designer ballgown size XXS under $5", self.wardrobe)
            output = trace.get_trace()

        self.assertIn("no listings", session["error"].lower())
        self.assertIn("search_listings (via MCP)", output)
        self.assertIn("[] (empty)", output)
        self.assertNotIn("suggest_outfit", output)
        suggest.assert_not_called()


if __name__ == "__main__":
    unittest.main()
