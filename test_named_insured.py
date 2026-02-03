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

    def test_postnet_rejection(self):
        """Test rejection of 'PostNet'."""
        text = "Named Insured: PostNet Suite 100"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "UnknownInsured")

    def test_parentheses_removal(self):
        """Test removal of parentheses and content."""
        text = "Named Insured: John Doe (Owner)"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "John_Doe")

    def test_check_rejection(self):
        """Test rejection of 'Check'."""
        text = "Named Insured: Check"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "UnknownInsured")

    def test_forbidden_words(self):
        """Test rejection of 'AND' and 'CANCELLED'."""
        # Test AND
        text = "Named Insured: AND"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "UnknownInsured")
        
        # Test CANCELLED
        text2 = "Named Insured: CANCELLED"
        data2 = {"full_text": text2, "pages": [{"words": [], "width": 100, "height": 100, "text": text2}]}
        _, metadata2 = self.processor.analyze_content(data2)
        self.assertEqual(metadata2["insured_name"], "UnknownInsured")

    def test_single_char_rejection(self):
        """Test rejection of 'A B C'."""
        text = "Named Insured: A B C"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "UnknownInsured")
        
    def test_mixed_char_acceptance(self):
        # "A B Wang" -> Should be accepted (Wang > 1)
        text = "Named Insured: A B Wang"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "A_B_Wang")

if __name__ == '__main__':
    unittest.main()
