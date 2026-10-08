import unittest

from mcp_client import call_tool
from tools import search_listings


class MCPSearchTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
