import unittest
from renamer_logic import PDFProcessor

class TestTermLogic(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_term_match_standard(self):
        """Standard 1-year term: Match 01/01/2025 and 01/01/2026."""
        text = """
        Policy Number: 123
        Date of Issue: 12/15/2024
        Policy Period: From 01/01/2025 to 01/01/2026
        """
        # Should pick 01/01/2025 because it pairs with 01/01/2026
        # Date of Issue is loose regex, but term logic is higher priority.
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "01-01-2025")

    def test_term_match_distractor(self):
        """Distractor date (Date of Issue) appears before effective date."""
        text = """
        Issue Date: 05/20/2023
        Some other date: 06/01/2023
        Effective: 07/01/2023 Expiring: 07/01/2024
        """
        # 07/01/2023 pairs with 07/01/2024. 
        # 05/20/2023 has no pair.
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "07-01-2023")

    def test_term_match_text_month(self):
        """Text month support."""
        text = """
        Period: Jan 15, 2025 - Jan 15, 2026
        """
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "01-15-2025")

    def test_no_match_fallback(self):
        """If no pair found, fallback to regex."""
        text = """
        Just one date: Effective 03/15/2025
        """
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "03-15-2025")

if __name__ == '__main__':
    unittest.main()
