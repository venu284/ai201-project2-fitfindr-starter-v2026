import re
import unittest
from unittest.mock import patch

import tools
from utils.data_loader import load_listings


class FitCardFallbackTests(unittest.TestCase):
    def test_fallback_stays_within_two_sentences_when_outfit_has_punctuation(self):
        item = load_listings()[1]
        outfit = "Wear it with baggy jeans. Add white sneakers! Finish with a crossbody bag?"

        with patch.object(tools, "generate", return_value="  "):
            card = tools.create_fit_card(outfit, item)

        sentences = [s for s in re.split(r"(?<=[.!?])\s+", card.strip()) if s]
        self.assertEqual(2, len(sentences), card)
        self.assertIn(item["platform"], card)
        self.assertIn(f"${item['price']:.2f}", card)


if __name__ == "__main__":
    unittest.main()
