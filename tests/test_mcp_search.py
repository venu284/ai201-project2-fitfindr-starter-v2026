import asyncio
import sys
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_client import SERVER, call_tool
from tools import compare_price, search_listings
from utils.data_loader import load_listings


class MCPSearchTests(unittest.TestCase):
    @staticmethod
    async def _list_tools():
        params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return (await session.list_tools()).tools

    def test_mcp_search_preserves_matching_and_empty_results(self):
        for arguments in (
            {"description": "vintage graphic tee", "size": "M", "max_price": 30.0},
            {"description": "designer ballgown", "size": "XXS", "max_price": 5.0},
        ):
            with self.subTest(arguments=arguments):
                self.assertEqual(
                    search_listings(**arguments),
                    call_tool("search_listings", arguments),
                )

    def test_mcp_compare_price_preserves_normal_result(self):
        new_item = next(
            listing for listing in load_listings() if listing["id"] == "lst_002"
        )

        self.assertEqual(
            compare_price(new_item),
            call_tool("compare_price", {"new_item": new_item}),
        )

    def test_mcp_compare_price_preserves_unavailable_result(self):
        new_item = {"id": "missing-price", "category": "tops"}

        self.assertEqual(
            compare_price(new_item),
            call_tool("compare_price", {"new_item": new_item}),
        )

    def test_compare_price_discovery_advertises_input_and_return_contract(self):
        advertised_tools = asyncio.run(self._list_tools())
        advertised = next(
            tool for tool in advertised_tools if tool.name == "compare_price"
        )
        schema = advertised.inputSchema
        new_item_schema = schema["properties"]["new_item"]

        self.assertEqual({"new_item"}, set(schema["properties"]))
        self.assertEqual("object", new_item_schema["type"])
        self.assertEqual(["new_item"], schema["required"])
        self.assertNotIn("required", new_item_schema)

        description = advertised.description.casefold()
        for phrase in ("id", "category", "numeric price", "unavailable"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, description)
        for field in (
            "status",
            "category",
            "item_price",
            "median_price",
            "difference",
            "comparable_count",
            "message",
        ):
            with self.subTest(field=field):
                self.assertIn(field, description)


if __name__ == "__main__":
    unittest.main()
