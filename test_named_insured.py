import unittest
from renamer_logic import PDFProcessor

class TestNamedInsured(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_item_prefix_digits(self):
        """Test Item prefix and digits in name."""
        text = "Item 1. Named Insured: 3M Corp"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "3M_Corp")

    def test_plural_and_punctuation(self):
        """Test (s) suffix and punctuation."""
        text = "Named Insured(s): Smith, John & Sons"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "Smith_John_&_Sons")

    def test_plain_no_colon(self):
        """Test simple Named Insured, no colon."""
        text = "Named Insured John Wick"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "John_Wick")

    def test_trailing_junk_cleanup(self):
        """Test cleanup of trailing punctuation."""
        text = "Named Insured: Best Insurance Co..."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "Best_Insurance_Co")

if __name__ == '__main__':
    unittest.main()
