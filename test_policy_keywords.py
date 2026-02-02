import unittest
from renamer_logic import PDFProcessor, DocumentType

class TestPolicyKeywords(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_coverage(self):
        text = "Details of your Coverage."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

    def test_deductible(self):
        text = "The Deductible is $500."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

    def test_dwelling(self):
        text = "Dwelling Coverage matches."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

    def test_perils(self):
        text = "Insured Perils include fire."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

if __name__ == '__main__':
    unittest.main()
