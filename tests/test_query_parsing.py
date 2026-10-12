import unittest

import agent


class QueryParsingTests(unittest.TestCase):
    def test_parses_size_constraints(self):
        cases = {
            "vintage tee size M": {
                "description": "vintage tee",
                "size": "M",
                "max_price": None,
            },
            "vintage tee size S/M": {
                "description": "vintage tee",
                "size": "S/M",
                "max_price": None,
            },
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(expected, agent.parse_query(query))

    def test_parses_each_supported_price_phrase(self):
        cases = {
            "vintage tee under $30": {
                "description": "vintage tee",
                "size": None,
                "max_price": 30.0,
            },
            "vintage tee below 30": {
                "description": "vintage tee",
                "size": None,
                "max_price": 30.0,
            },
            "vintage tee less than $30": {
                "description": "vintage tee",
                "size": None,
                "max_price": 30.0,
            },
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(expected, agent.parse_query(query))

    def test_parses_size_and_price_together(self):
        self.assertEqual(
            {
                "description": "vintage tee",
                "size": "M",
                "max_price": 30.0,
            },
            agent.parse_query("vintage tee size M under $30"),
        )

    def test_returns_unconstrained_query_as_description(self):
        self.assertEqual(
            {
                "description": "vintage tee",
                "size": None,
                "max_price": None,
            },
            agent.parse_query("vintage tee"),
        )

    def test_matches_constraint_keywords_case_insensitively(self):
        self.assertEqual(
            {
                "description": "Vintage Tee",
                "size": "m",
                "max_price": 30.0,
            },
            agent.parse_query("Vintage Tee SIZE m BELOW $30"),
        )

    def test_parses_decimal_max_price(self):
        self.assertEqual(
            {
                "description": "vintage tee",
                "size": None,
                "max_price": 30.5,
            },
            agent.parse_query("vintage tee under $30.50"),
        )


if __name__ == "__main__":
    unittest.main()
