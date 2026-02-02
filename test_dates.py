import unittest
import re

class TestDatePatterns(unittest.TestCase):
    def setUp(self):
        # This mirrors the logic in renamer_logic.py
        self.patterns = [
            r'(?:Effective|Issue|Policy)\s*(?:Date)?[:\.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(?:Period|From)[:\.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'Date of Issue:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:Effective|Issue|Policy)?\s*Date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

    def test_effective_date(self):
        text = "Effective Date: 01/30/2025"
        match = None
        for p in self.patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: match = m.group(1); break
        self.assertEqual(match, "01/30/2025")

    def test_period(self):
        text = "Policy Period: 01/30/2025 to 01/30/2026"
        match = None
        for p in self.patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: match = m.group(1); break
        self.assertEqual(match, "01/30/2025")

    def test_from(self):
        text = "From 01/30/2025"
        match = None
        for p in self.patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: match = m.group(1); break
        self.assertEqual(match, "01/30/2025")

if __name__ == '__main__':
    unittest.main()
