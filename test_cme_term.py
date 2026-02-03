
import unittest
from datetime import datetime
from renamer_logic import PDFProcessor, DocumentType

class TestCMETerm(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_cme_term_recognition_and_renaming(self):
        # Mock extracted text based on the user's image
        mock_text = """
        CME Insurance Brokerage Inc.
        773 60th Street #2R, Brooklyn, NY 11220
        
        Agreement Acknowledgement
        
        This AGREEMENT is executed by CME Insurance Brokerage Inc and its appointed affiliates...
        
        Effective Date:
        The designated effective date is acknowledged by insured, CME will NOT be responsible...
        
        Insured Name: John Doe LLC                            Applicant: Jane Doe
        """
        
        # Add date for this test
        mock_text_with_date = mock_text + "\nEffective Date: 02/02/2026"
         
        data = {
            "full_text": mock_text_with_date,
            "pages": [{"words": [], "text": mock_text_with_date}]
        }

        doc_type, metadata = self.processor.analyze_content(data)
        
        self.assertEqual(doc_type, DocumentType.CME_TERM, "Should process as CME_TERM")
        self.assertEqual(metadata['insured_name'], "John_Doe_LLC", "Should extract Insured Name")
        self.assertEqual(metadata['date'], "02-02-2026", "Should extract Date")
        
        # Test Renaming
        new_name = self.processor.generate_new_name("test.pdf", doc_type, metadata)
        expected_name = "John_Doe_LLC_CME Term_02-02-2026.pdf"
        self.assertEqual(new_name, expected_name, f"Expected {expected_name}, got {new_name}")

    def test_cme_term_date_fallback(self):
        # Mock extracted text WITHOUT date
        mock_text = """
        CME Insurance Brokerage Inc.
        Agreement Acknowledgement
        
        Insured Name: Fallback User LLC
        """
         
        data = {
            "full_text": mock_text,
            "pages": [{"words": [], "text": mock_text}]
        }

        doc_type, metadata = self.processor.analyze_content(data)
        
        expected_date = datetime.now().strftime("%m-%d-%Y")
        
        self.assertEqual(doc_type, DocumentType.CME_TERM, "Should process as CME_TERM")
        self.assertEqual(metadata['insured_name'], "Fallback_User_LLC", "Should extract Insured Name")
        self.assertEqual(metadata['date'], expected_date, "Should use current date as fallback")
        
        # Test Renaming
        new_name = self.processor.generate_new_name("test.pdf", doc_type, metadata)
        expected_name = f"Fallback_User_LLC_CME Term_{expected_date}.pdf"
        self.assertEqual(new_name, expected_name, f"Expected {expected_name}, got {new_name}")

if __name__ == '__main__':
    unittest.main()
