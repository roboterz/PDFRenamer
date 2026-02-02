import unittest
from renamer_logic import PDFProcessor

class TestBadGuesses(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_header_as_name(self):
        """Test that a document title is NOT picked as the name."""
        words = [
            # Huge Header
            {"text": "COMMERCIAL", "x0": 100, "x1": 300, "top": 50, "bottom": 80, "size": 24},
            {"text": "POLICY", "x0": 310, "x1": 400, "top": 50, "bottom": 80, "size": 24},
            
            # The real name (smaller)
            {"text": "John", "x0": 50, "x1": 80, "top": 150, "bottom": 162, "size": 12},
            {"text": "Doe", "x0": 85, "x1": 110, "top": 150, "bottom": 162, "size": 12},
            
            # Address to help valid name
            {"text": "123", "x0": 50, "x1": 70, "top": 165, "bottom": 177, "size": 12},
            {"text": "Main", "x0": 75, "x1": 100, "top": 165, "bottom": 177, "size": 12},
            {"text": "St", "x0": 105, "x1": 120, "top": 165, "bottom": 177, "size": 12},
        ]
        data = {
            "full_text": "COMMERCIAL POLICY\nJohn Doe\n123 Main St",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Header Guess: {extracted}")
        # Expect: "John_Doe" (or Unknown), definitely NOT "COMMERCIAL_POLICY"
        self.assertNotEqual(extracted, "COMMERCIAL_POLICY")

    def test_agent_as_name(self):
        """Test that Agent name is avoided."""
        words = [
            # Agent Block
            {"text": "Agent:", "x0": 10, "x1": 50, "top": 50, "bottom": 62, "size": 12},
            {"text": "James", "x0": 60, "x1": 90, "top": 50, "bottom": 62, "size": 12},
            {"text": "Bond", "x0": 95, "x1": 120, "top": 50, "bottom": 62, "size": 12},
            
            # Real Insured (No label, just address below)
            {"text": "Evil", "x0": 10, "x1": 40, "top": 200, "bottom": 212, "size": 12},
            {"text": "Villain", "x0": 45, "x1": 90, "top": 200, "bottom": 212, "size": 12},
            {"text": "LLC", "x0": 95, "x1": 120, "top": 200, "bottom": 212, "size": 12},
            
            {"text": "Secret", "x0": 10, "x1": 50, "top": 215, "bottom": 227, "size": 12}, # Addr
            {"text": "Lair", "x0": 55, "x1": 80, "top": 215, "bottom": 227, "size": 12},
        ]
        data = {
            "full_text": "Agent: James Bond\nEvil Villain LLC\nSecret Lair",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Agent Guess: {extracted}")
        self.assertNotEqual(extracted, "James_Bond")

    def test_junk_header(self):
        """Test large junk text."""
        words = [
            {"text": "Summary", "x0": 50, "x1": 150, "top": 50, "bottom": 80, "size": 20},
            {"text": "of", "x0": 160, "x1": 180, "top": 50, "bottom": 80, "size": 20},
            {"text": "Coverage", "x0": 190, "x1": 300, "top": 50, "bottom": 80, "size": 20},
            
            # Real Name
            {"text": "John", "x0": 50, "x1": 80, "top": 150, "bottom": 162, "size": 12},
            {"text": "Doe", "x0": 85, "x1": 110, "top": 150, "bottom": 162, "size": 12},
            # Address below
            {"text": "123", "x0": 50, "x1": 70, "top": 165, "bottom": 177, "size": 12},
            {"text": "Main", "x0": 75, "x1": 100, "top": 165, "bottom": 177, "size": 12},
        ]
        data = {
            "full_text": "Summary of Coverage\nJohn Doe\n123 Main",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Summary Guess: {extracted}")
        self.assertNotEqual(extracted, "Summary_of_Coverage")

    def test_page_number_junk(self):
        """Test picking up page number."""
        words = [
             {"text": "Page", "x0": 500, "x1": 530, "top": 20, "bottom": 30, "size": 14},
             {"text": "1", "x0": 535, "x1": 545, "top": 20, "bottom": 30, "size": 14},
             {"text": "of", "x0": 550, "x1": 560, "top": 20, "bottom": 30, "size": 14},
             {"text": "5", "x0": 565, "x1": 575, "top": 20, "bottom": 30, "size": 14},
             
             # Name
             {"text": "Alice", "x0": 50, "x1": 90, "top": 100, "bottom": 112, "size": 12},
             {"text": "Smith", "x0": 95, "x1": 130, "top": 100, "bottom": 112, "size": 12},
             # Address
             {"text": "456", "x0": 50, "x1": 70, "top": 115, "bottom": 127, "size": 12},
             {"text": "Rd", "x0": 75, "x1": 90, "top": 115, "bottom": 127, "size": 12},
        ]
        data = {
            "full_text": "Page 1 of 5\nAlice Smith\n456 Rd",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"PageNum Guess: {extracted}")
        self.assertNotEqual(extracted, "Page_1_of_5")

if __name__ == '__main__':
    unittest.main()
