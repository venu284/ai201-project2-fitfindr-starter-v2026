import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import call, patch

import agent
import app
import trace
from utils.data_loader import get_example_wardrobe, load_listings


class SearchRelaxationTests(unittest.TestCase):
    def setUp(self):
        self.wardrobe = get_example_wardrobe()
        self.first, self.second = load_listings()[:2]

    def test_new_session_starts_without_search_relaxation(self):
        session = agent.new_session("vintage tee", self.wardrobe)

        self.assertIsNone(session["search_relaxation"])

    def test_empty_sized_search_retries_without_size_and_continues(self):
        comparison = {"status": "below_median", "message": "below median"}

        def dispatch(tool_name, arguments):
            if tool_name == "search_listings":
                return [] if arguments["size"] == "M" else [self.first, self.second]
            if tool_name == "compare_price":
                return comparison
            self.fail(f"unexpected MCP tool: {tool_name}")

        with (
            patch.object(agent, "call_tool", side_effect=dispatch) as mcp,
            patch.object(agent, "suggest_outfit", return_value="saved outfit") as suggest,
            patch.object(agent, "create_fit_card", return_value="saved card") as create,
        ):
            session = agent.run_agent("vintage tee size M under $40", self.wardrobe)

        search_calls = [
            tool_call
            for tool_call in mcp.call_args_list
            if tool_call.args[0] == "search_listings"
        ]
        self.assertEqual(
            [
                call(
                    "search_listings",
                    {"description": "vintage tee", "size": "M", "max_price": 40.0},
                ),
                call(
                    "search_listings",
                    {"description": "vintage tee", "size": None, "max_price": 40.0},
                ),
            ],
            search_calls,
        )
        self.assertEqual(
            call("compare_price", {"new_item": self.first}),
            mcp.call_args_list[-1],
        )
        self.assertEqual(self.first, session["selected_item"])
        self.assertIs(comparison, session["price_comparison"])
        self.assertIn("size M", session["search_relaxation"])
        self.assertIn("retried without the size filter", session["search_relaxation"])
        self.assertIsNone(session["error"])
        suggest.assert_called_once_with(self.first, self.wardrobe)
        create.assert_called_once_with("saved outfit", self.first)

    def test_successful_sized_search_does_not_relax_or_retry(self):
        with (
            patch.object(agent, "call_tool", return_value=[self.first]) as mcp,
            patch.object(agent, "suggest_outfit", return_value="saved outfit") as suggest,
            patch.object(agent, "create_fit_card", return_value="saved card") as create,
        ):
            session = agent.run_agent("vintage tee size M under $40", self.wardrobe)

        mcp.assert_called_once_with(
            "search_listings",
            {"description": "vintage tee", "size": "M", "max_price": 40.0},
        )
        self.assertIsNone(session["search_relaxation"])
        self.assertEqual(self.first, session["selected_item"])
        self.assertEqual("skipped_single_match", session["price_comparison"]["status"])
        self.assertEqual("saved outfit", session["outfit_suggestion"])
        self.assertEqual("saved card", session["fit_card"])
        self.assertIsNone(session["error"])
        suggest.assert_called_once_with(self.first, self.wardrobe)
        create.assert_called_once_with("saved outfit", self.first)

    def test_empty_relaxed_search_stops_before_comparison_and_model_tools(self):
        def dispatch(tool_name, arguments):
            self.assertEqual("search_listings", tool_name)
            return []

        with (
            patch.object(agent, "call_tool", side_effect=dispatch) as mcp,
            patch.object(agent, "suggest_outfit") as suggest,
            patch.object(agent, "create_fit_card") as create,
        ):
            session = agent.run_agent("designer ballgown size XXS under $5", self.wardrobe)

        self.assertEqual(2, mcp.call_count)
        self.assertEqual("XXS", mcp.call_args_list[0].args[1]["size"])
        self.assertIsNone(mcp.call_args_list[1].args[1]["size"])
        self.assertIn("dropped the size filter", session["error"])
        self.assertIn("XXS", session["error"])
        self.assertIn("broader keywords", session["error"])
        self.assertIn("higher price limit", session["error"])
        self.assertIn("size XXS", session["search_relaxation"])
        self.assertIn(
            "retried without the size filter", session["search_relaxation"]
        )
        self.assertIsNone(session["price_comparison"])
        self.assertIsNone(session["outfit_suggestion"])
        self.assertIsNone(session["fit_card"])
        suggest.assert_not_called()
        create.assert_not_called()

    def test_empty_search_without_size_does_not_retry(self):
        with (
            patch.object(agent, "call_tool", return_value=[]) as mcp,
            patch.object(agent, "suggest_outfit") as suggest,
            patch.object(agent, "create_fit_card") as create,
        ):
            session = agent.run_agent("designer ballgown under $5", self.wardrobe)

        mcp.assert_called_once_with(
            "search_listings",
            {"description": "designer ballgown", "size": None, "max_price": 5.0},
        )
        self.assertIsNone(session["search_relaxation"])
        self.assertEqual(
            "No listings matched. Try broader keywords, a different size, "
            "or a higher price limit.",
            session["error"],
        )
        suggest.assert_not_called()
        create.assert_not_called()

    def test_trace_records_relaxed_mcp_search_and_reason(self):
        def dispatch(tool_name, arguments):
            self.assertEqual("search_listings", tool_name)
            return [] if arguments["size"] == "M" else [self.first]

        with (
            patch.object(agent, "call_tool", side_effect=dispatch),
            patch.object(agent, "suggest_outfit", return_value="saved outfit"),
            patch.object(agent, "create_fit_card", return_value="saved card"),
            redirect_stdout(StringIO()),
        ):
            trace.start_trace()
            session = agent.run_agent("vintage tee size M under $40", self.wardrobe)
            output = trace.get_trace()

        self.assertIn("search_listings retry (via MCP)", output)
        self.assertIn("size=None", output)
        self.assertIn("dropped size filter", output)
        self.assertIn(session["search_relaxation"], output)

    def test_successful_relaxation_is_printed_before_found(self):
        session = agent.new_session("vintage tee size M", self.wardrobe)
        message = (
            "No listings matched size M, so FitFindr retried without the size filter."
        )
        session.update(
            {
                "search_relaxation": message,
                "selected_item": self.first,
                "price_comparison": {"message": "saved comparison"},
                "outfit_suggestion": "saved outfit",
                "fit_card": "saved card",
            }
        )

        direct_output = StringIO()
        with redirect_stdout(direct_output):
            agent._show(session)

        cli_output = StringIO()
        with (
            patch.object(agent, "run_agent", return_value=session),
            redirect_stdout(cli_output),
        ):
            app._ask_one(session["query"], self.wardrobe, False)

        for output in (direct_output.getvalue(), cli_output.getvalue()):
            with self.subTest(output=output):
                self.assertIn(message, output)
                self.assertLess(output.index(message), output.casefold().index("found:"))

    def test_agent_failure_output_prints_dropped_size_error_once(self):
        session = self._exhausted_relaxed_session()
        output = StringIO()

        with redirect_stdout(output):
            agent._show(session)

        text = output.getvalue()
        self.assertEqual(1, text.count("dropped the size filter"))
        self.assertEqual(1, text.count("size filter"))
        self.assertEqual(1, text.count(session["error"]))
        self.assertNotIn(session["search_relaxation"], text)

    def test_cli_failure_output_prints_dropped_size_error_once(self):
        session = self._exhausted_relaxed_session()
        output = StringIO()

        with (
            patch.object(agent, "run_agent", return_value=session),
            redirect_stdout(output),
        ):
            returned = app._ask_one(session["query"], self.wardrobe, False)

        text = output.getvalue()
        self.assertIs(session, returned)
        self.assertEqual(1, text.count("dropped the size filter"))
        self.assertEqual(1, text.count("size filter"))
        self.assertEqual(1, text.count(session["error"]))
        self.assertNotIn(session["search_relaxation"], text)

    def _exhausted_relaxed_session(self):
        with (
            patch.object(agent, "call_tool", return_value=[]),
            patch.object(agent, "suggest_outfit") as suggest,
            patch.object(agent, "create_fit_card") as create,
        ):
            session = agent.run_agent(
                "designer ballgown size XXS under $5", self.wardrobe
            )

        suggest.assert_not_called()
        create.assert_not_called()
        return session


if __name__ == "__main__":
    unittest.main()
