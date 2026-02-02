import re
import os
import pytesseract
from thefuzz import process, fuzz
from pdfplumber import open as plumber_open
import pdfplumber
from enum import Enum, auto

class DocumentType(Enum):
    POLICY = auto()
    INVOICE = auto()
    CERTIFICATE = auto()
    UNKNOWN = auto()

class PDFProcessor:
    def __init__(self):
        pass

    def extract_data(self, filepath):
        """Extracts text and spatial data from the first few pages of the PDF."""
        data = {
            "full_text": "", 
            "pages": [] # List of {words, width, height, text}
        }
        try:
            with pdfplumber.open(filepath) as pdf:
                # Scan up to first 5 pages
                num_pages = min(len(pdf.pages), 5)
                for i in range(num_pages):
                    page = pdf.pages[i]
                    text = page.extract_text() or ""
                    
                    # OCR Fallback
                    if len(text) < 50:
                        try:
                            # Convert to image for OCR
                            # We try pdfplumber's image extraction if available or skip.
                            im = page.to_image(resolution=300).original
                            text = pytesseract.image_to_string(im)
                        except Exception as ocr_e:
                            print(f"OCR Failed for page {i}: {ocr_e}")

                    p_data = {
                        "width": page.width,
                        "height": page.height,
                        "text": text,
                        "words": page.extract_words(extra_attrs=["fontname", "size"])
                    }
                    data["pages"].append(p_data)
                    data["full_text"] += "\n" + text
                    
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        return data


        
    def _fuzzy_match(self, target, candidates, threshold=80):
        """Helper for fuzzy matching a string against a list/string."""
        # Not used directly in loop to avoid perf hit, but useful for verifying anchors
        pass # implemented inline for speed

    def _perform_zone_ocr(self, filepath, page_index, anchor_rect):
        """
        Performs OCR on a specific region relative to an anchor.
        anchor_rect: (x0, top, x1, bottom)
        """
        try:
           with pdfplumber.open(filepath) as pdf:
               if page_index >= len(pdf.pages): return None
               page = pdf.pages[page_index]
               
               # Define crop region: Right of anchor, same height approx
               # x0 = anchor.right, top = anchor.top - 5, x1 = page.width, bottom = anchor.bottom + 5
               # But pdfplumber bbox is (x0, top, x1, bottom)
               
               # Let's define a generous area to the right
               crop_box = (
                   anchor_rect[2], # x0 (start at anchor right)
                   max(0, anchor_rect[1] - 5), # top
                   min(page.width, anchor_rect[2] + 400), # x1 (width of value ~400px)
                   min(page.height, anchor_rect[3] + 5) # bottom
               )
               
               # Crop
               cropped = page.crop(crop_box)
               
               # Image conversion
               im = cropped.to_image(resolution=300).original
               
               # OCR
               text = pytesseract.image_to_string(im, config='--psm 7').strip() # PSM 7 = Single text line
               return text
        except Exception as e:
            print(f"Zone OCR Failed: {e}")
            return None
            
    def _find_text_spatially(self, data, keywords, search_direction='right', x_tolerance=50, y_tolerance=10, filepath=None):
        """
        Finds text spatially relative to a keyword.
        search_direction: 'right' (same line) or 'below' (next line)
        """
        pages = data.get("pages", [])
        if not pages: return None
        
        # Stop words that indicate we hit another label
        STOP_WORDS = ["date", "policy", "number", "agent", "address", "phone", "fax", "email", "website", "www", "http", "page", "of", "produced", "by", "code"]

        # Iterate through EACH page independently
        for page_data in pages:
            words = page_data.get("words", [])
            if not words: continue

            # ... anchor logic ...
            target_values = []
            
            for kw in keywords:
                # Prepare kw tokens for matching
                kw_tokens = kw.lower().split()
                
                for i, word in enumerate(words):
                    # Optimized Fuzzy Match: 
                    # 1. First Check first token strictly (speed) -> 'named' vs 'namcd'
                    # Actually, for OCR errors, strict first token validation is bad.
                    # But comparing every word to every keyword is slow. 
                    # Let's do a quick length check?
                    
                    w_text = word['text'].lower().strip(":").strip()
                    if not w_text: continue
                    
                    # Fuzzy match first token of keyword
                    # Threshold 80 allows "Namcd" (83 vs Named)
                    if fuzz.ratio(w_text, kw_tokens[0].strip(":")) < 80:
                        continue
                        
                    # Potential Start Found. Check phrase.
                    match = True
                    matched_indices = [i]
                    
                    for k in range(1, len(kw_tokens)):
                        if i + k >= len(words):
                            match = False
                            break
                        
                        val_word = words[i+k]['text'].lower().strip(":").strip()
                        val_kw = kw_tokens[k].strip(":")
                        
                        # Fuzzy match each subsequent token
                        if fuzz.ratio(val_word, val_kw) < 80:
                            match = False
                            break
                        
                        matched_indices.append(i+k)
                    
                    if match:
                        # Found anchor
                        last_word = words[matched_indices[-1]]
                        anchor_right = last_word['x1']
                        anchor_bottom = last_word['bottom']
                        anchor_top = words[matched_indices[0]]['top']
                        anchor_left = words[matched_indices[0]]['x0']
                        
                        found_candidates = []
                        
                        if search_direction == 'right':
                             same_line_candidates = []
                             for w in words:
                                if w['text'].lower() in kw: continue # Skip self
                                if i <= words.index(w) < i + len(kw_tokens): continue # Skip self strictly
                                
                                # Relaxed Y-Overlap
                                w_mid = (w['top'] + w['bottom']) / 2
                                if w_mid >= (anchor_top - 5) and w_mid <= (anchor_bottom + 5):
                                    if w['x0'] > anchor_right and (w['x0'] - anchor_right) < x_tolerance:
                                        same_line_candidates.append(w)
                             
                             found_candidates.extend(same_line_candidates)
                             
                             # Check for wrap-around (multi-line value)
                             if same_line_candidates:
                                 same_line_candidates.sort(key=lambda x: x['x0'])
                                 val_left = same_line_candidates[0]['x0']
                                 mask_bottom = max(w['bottom'] for w in same_line_candidates)
                                 
                                 # Look for words strictly below, aligned left
                                 for w in words:
                                     if w in found_candidates: continue
                                     
                                     # Y-Check: Next line (approx 10-20px gap)
                                     if w['top'] > (mask_bottom - 2) and w['top'] < (mask_bottom + 20):
                                         # X-Check: Aligned approx left or indented
                                         # Allow starting slightly left or anywhere to right (continuation)
                                         if w['x0'] > (val_left - 20):
                                             found_candidates.append(w)
                                            
                        elif search_direction == 'below':
                             for w in words:
                                if w['text'].lower() in kw: continue
                                if i <= words.index(w) < i + len(kw_tokens): continue
                                
                                # Stricter Alignment for "Below":
                                # Value should not be significantly to the left of Key.
                                # Value top should be below key bottom.
                                if w['top'] > (anchor_bottom - 2) and (w['top'] - anchor_bottom) < y_tolerance:
                                    # Allow small float (-10) for slight misalignment, but not -50
                                    if w['x0'] >= (anchor_left - 10) and w['x0'] <= (anchor_right + 100):
                                         found_candidates.append(w)

                        if found_candidates:
                            found_candidates.sort(key=lambda x: (x['top'], x['x0']))
                            
                            # Filter junk
                            clean_words = []
                            for w in found_candidates:
                                text_clean = w['text'].strip()
                                if text_clean.lower().strip(":") in STOP_WORDS:
                                     break 
                                clean_words.append(text_clean)
                            
                            val_text = " ".join(clean_words)
                            if len(val_text) > 2:
                                return val_text
                            
                        # Fallback: Zone OCR if filepath is provided and no candidates found but anchor exists
                        if filepath and not found_candidates and search_direction == 'right':
                            # Only do this for 'right' lookups for now as they are most common for "Anchor: Value"
                            # Construct anchor rect
                            anchor_rect = (anchor_left, anchor_top, anchor_right, anchor_bottom)
                            # Which page?
                            # We are iterating through pages, need index. 
                            # Hack: data['pages'] list index implies page number if sequential.
                            # Let's assume sequential.
                            page_idx = data['pages'].index(page_data)
                            
                            ocr_text = self._perform_zone_ocr(filepath, page_idx, anchor_rect)
                            if ocr_text and len(ocr_text) > 2:
                                # Basic stopword check on OCR result
                                if ocr_text.lower().split()[0] not in STOP_WORDS:
                                    print(f"Zone OCR recovered: {ocr_text}")
                                    return ocr_text

        return None

    def _parse_date_string(self, date_str):
        """Helper to parse MM/DD/YYYY or similar into (M, D, Y) tuple."""
        # Normalize
        d = date_str.replace('-', '/').replace('.', '/').replace(',', '').replace(' ', '/')
        parts = re.split(r'/', d)
        
        # Filter empty strings from split
        parts = [p for p in parts if p]
        
        try:
            if len(parts) == 3:
                # Assuming MM/DD/YYYY or MM/DD/YY
                p1, p2, p3 = parts[0], parts[1], parts[2]
                
                # Handle text months
                months = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, 
                          "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12}
                
                m = 0
                
                # Check if p1 is text
                if p1[:3].lower() in months:
                     m = months[p1[:3].lower()]
                     d = int(p2)
                     y = int(p3)
                else:
                     # Numeric
                     m = int(p1)
                     d = int(p2)
                     y = int(p3)
                
                # Year normalization (2-digit to 4-digit)
                if y < 100: y += 2000 
                
                return (m, d, y)
        except:
            return None
        return None

    def _find_date_by_term_logic(self, text):
        """
        Finds effective date by looking for a pair (Start, End) 
        where Month and Day are same, but Year is different.
        Returns the earlier date string if found.
        """
        # Find ALL dates
        # Using a broad pattern to catch everything
        patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b'
        ]
        
        candidates = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            candidates.extend(matches)
            
        parsed_dates = []
        for c in candidates:
            p = self._parse_date_string(c)
            if p:
                parsed_dates.append({"raw": c, "parsed": p})
        
        # Look for pairs
        # We want D1, D2 such that D1.m == D2.m and D1.d == D2.d and D1.y != D2.y
        # And usually D2.y = D1.y + 1 (1 year term) or similar.
        # We pick the earliest one as Effective Date.
        
        # Sort by date
        parsed_dates.sort(key=lambda x: (x['parsed'][2], x['parsed'][0], x['parsed'][1]))
        
        for i in range(len(parsed_dates)):
            d1 = parsed_dates[i]
            for j in range(i+1, len(parsed_dates)):
                d2 = parsed_dates[j]
                
                p1 = d1['parsed']
                p2 = d2['parsed']
                
                if p1[0] == p2[0] and p1[1] == p2[1]:
                    # Month and Day match
                    if p1[2] < p2[2]:
                        # Year is increasing. This is likely a term.
                        # We return the start date (d1)
                        # Normalize it now? Or return raw?
                        # Let's return the raw strings processed by main logic later or normalized here.
                        # Logic below expects dashed format.
                        return f"{p1[0]:02d}-{p1[1]:02d}-{p1[2]}"
        
        return None

        return None

    def _is_valid_name(self, name_str):
        """Validates if the extracted string is a reasonable name."""
        name = name_str.strip()
        if len(name) < 3: return False
        
        name_lower = name.lower()
        
        # Blocklist of generic terms
        blocklist = [
            "policy", "number", "date", "page", "invoice", "bill", "renewal", 
            "item", "agent", "agency", "producer", "transaction", "code",
            "insurance", "company", "declaration", "homeowner", "automobile",
            "unknown", "address", "phone", "fax", "email", "website", "www", "http",
            "summary", "coverage", "auto", "liability", "commercial", "quote", 
            "proposal", "endorsement", "detail", "premium", "location"
        ]
        
        for bad_word in blocklist:
            if bad_word in name_lower:
                return False
                
        # Check for digit density (e.g. phone numbers or IDs)
        digit_count = sum(c.isdigit() for c in name)
        if digit_count > len(name) * 0.4: # More than 40% digits
            return False
            
        # Check for date-like characters
        if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', name):
            return False
            
        return True
    
    def _sanitize_name(self, name):
        """Removes invalid filename characters and excess whitespace."""
        # Invalid chars: < > : " / \ | ? *
        cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
        cleaned = cleaned.strip(" .,-_")
        return cleaned



    def analyze_content(self, data, filepath=None):
        """Analyzes text to determine document type and extract metadata."""
        text = data.get("full_text", "")
        text_lower = text.lower()
        
        metadata = {
            "insured_name": "UnknownInsured",
            "company_name": "UnknownCompany",
            "date": "0000-00-00",
            "policy_number": None,
            "type_detail": "Doc"
        }
        
        doc_type = DocumentType.UNKNOWN
        
        # 1. Determine Document Type
        # Priority 1: Policy/Declaration (User Request: Check this FIRST)
        policy_keywords = ["declaration", "deductible", "peril"]
        policy_found = False
        for kw in policy_keywords:
            if kw in text_lower:
                doc_type = DocumentType.POLICY
                policy_found = True
                break
        
        if not policy_found:
            # Priority 2: Certificate
            if "certificate of insurance" in text_lower or "acord" in text_lower:
                doc_type = DocumentType.CERTIFICATE
            # Priority 3: Invoice (Check this LAST)
            elif "invoice" in text_lower or "bill" in text_lower or "due" in text_lower:
                doc_type = DocumentType.INVOICE

        # 2. Extract Metadata - HYBRID APPROACH (Regex Priority for Reliability)

        # --- Insured Name ---
        # Regex First (it handles "Name: Value" patterns well usually)
        insured_patterns = [
            # Explicit "Named Insured" is strongest signal
            # Handle: "Item 1. Named Insured", "Named Insured(s)", "Named Insured:"
            # Note: (?:...) is non-capturing group. parens in text need escaping if we mean literal parens.
            # We want to match "Named Insured" or "Named Insured(s)" or "Named Insureds"
            r'(?:Item\s*\d+\.?)?\s*Named\s*Insured(?:\(s\)|s)?[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Insured\s*Name(?:s)?[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Insured[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Account\s*Name[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Applicant[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Customer[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'(?:First\s*)?Named\s*Insured[:\.]?\s*([A-Za-z0-9\s,&.-]+)', 
            r'Policyholder[:\.]?\s*([A-Za-z0-9\s,&.-]+)',
            r'Entity[:\.]?\s*([A-Za-z0-9\s,&.-]+)' 
        ]
        
        name_found = False
        for pat in insured_patterns:
             m = re.search(pat, text, re.IGNORECASE)
             if m:
                 # Capture group 1
                 raw_name = m.group(1)
                 
                 # Split by newline looks for end of line
                 # But sometimes name is multi-line. Here we take first line to be safe for filename.
                 clean = raw_name.split('\n')[0].strip()
                 
                 # Basic cleaner
                 clean = re.sub(r'Page\s+\d+', '', clean, flags=re.IGNORECASE)
                 clean = re.sub(r'Policy\s+No.*', '', clean, flags=re.IGNORECASE)
                 # Remove trailing punctuation often captured
                 clean = clean.strip(".,-:")
                 # Remove internal commas for cleaner filename
                 clean = clean.replace(',', '')
                 
                 if self._is_valid_name(clean):
                     metadata["insured_name"] = self._sanitize_name(clean).replace(' ', '_')
                     name_found = True
                     break
        
        # If Regex failed, or result looks suspicious (short), try Spatial
        if not name_found:
             # Strategy: Keys with colons usually imply Right. Keys without usually imply Below.
             colon_keys = ["named insured:", "insured name:", "insured:", "applicant:", "customer:", "policyholder:", "entity:", "client:"]
             no_colon_keys = ["named insured", "insured name", "policyholder"]
             
             spat_name = None
             
             # 1. Try Colon Keys -> Right (Standard Form)
             spat_name = self._find_text_spatially(data, colon_keys, 'right', x_tolerance=300, filepath=filepath)
             
             # 2. Try No Colon Keys -> Below (Header Style)
             if not spat_name:
                 spat_name = self._find_text_spatially(data, no_colon_keys, 'below', y_tolerance=25, filepath=filepath)
             
             # 3. Fallbacks (Colon -> Below, NoColon -> Right)
             if not spat_name:
                 spat_name = self._find_text_spatially(data, colon_keys, 'below', y_tolerance=25, filepath=filepath)
             if not spat_name:
                 spat_name = self._find_text_spatially(data, no_colon_keys, 'right', x_tolerance=300, filepath=filepath)
                 
             if spat_name:
                 cleaned_spat = spat_name.split('\n')[0].strip()
                 if self._is_valid_name(cleaned_spat):
                     metadata["insured_name"] = self._sanitize_name(cleaned_spat).replace(' ', '_')

                     metadata["insured_name"] = self._sanitize_name(cleaned_spat).replace(' ', '_')



        # --- Date ---
        found_date = None
        
        # 1. Term Match Logic (Highest Priority) - User Request
        # "Start date has a corresponding End date with same Month/Day but diff Year"
        term_date = self._find_date_by_term_logic(text)
        if term_date:
            found_date = term_date
            
        if not found_date:
            # 2. Regex with specific Keywords
            date_patterns = [
                # High Priority: Explicit Labels mentioned by user
                r'(?:Effective|Issue|Policy)\s*(?:Date)?[:\.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # Effective Date: 01/30/2025
                r'(?:Period|From)[:\.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',                        # Period: 01/30/2025 or From: 01/30/2025
                
                # Secondary
                r'Date of Issue:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Policy Period:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(?:Effective|Issue|Policy)?\s*Date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})' # Fallback
            ]
            
            # Try Regex
            for pat in date_patterns:
                dm = re.search(pat, text, re.IGNORECASE)
                if dm:
                    val = dm.group(0)
                    if len(dm.groups()) > 0 and dm.group(1): val = dm.group(1)
                    found_date = val
                    break
            
            # 3. Spatial
            if not found_date:
                date_keys = ["effective date", "policy period", "period:", "date of issue", "invoice date"]
                spat_date = self._find_text_spatially(data, date_keys, 'right', x_tolerance=200)
                if spat_date:
                     for pat in date_patterns: # Re-use date patterns for spatial text
                        dm = re.search(pat, spat_date, re.IGNORECASE)
                        if dm:
                            val = dm.group(0)
                            if len(dm.groups()) > 0 and dm.group(1): val = dm.group(1)
                            found_date = val
                            break
                        
        if found_date:
             found_date = found_date.replace('/', '-').replace(',', '').replace('.', '')
             metadata["date"] = found_date.replace(' ', '-')

        # --- Company ---
        # Known list is best
        known_companies = [
            "Geico", "State Farm", "Allstate", "Liberty Mutual", "Progressive", "Chubb", 
            "Travelers", "MIC", "Integon", "Guard", "Hyundai", "Nationwide", "Farmers", 
            "USAA", "The Hartford", "Berkshire Hathaway", "MetLife", "CNA", "Amica", 
            "Erie", "Auto-Owners", "Zurich", "AIG", "Markel", "Hiscox", "Hartford",
            "Philadelphia", "Starr", "Lloyds", "Scottsdale"
        ]
        
        company_found = False
        company_found = False
        
        # Fuzzy Matching for known companies
        # Threshold 85 seems reasonable for "The Hartford" vs "The Hartford Ins"
        best_match, score = process.extractOne(text_lower, [c.lower() for c in known_companies], scorer=fuzz.partial_ratio)
        
        if score > 85:
            # Find the original case
            for c in known_companies:
                if c.lower() == best_match:
                    metadata["company_name"] = c
                    company_found = True
                    break
        
        if not company_found:
             # Fallback Regex
             m = re.search(r'(?:Underwritten by|Company|Insurer|Producer):\s*([A-Za-z\s,.]+)', text, re.IGNORECASE)
             if m:
                 cand = m.group(1).split(',')[0].strip().rstrip('.')
                 if len(cand) > 3:
                    metadata["company_name"] = cand.replace(' ', '_')
         


        # Type specific refinement
        if doc_type == DocumentType.CERTIFICATE:
            if "acord 25" in text_lower:
                metadata["type_detail"] = "Acord25"
            else:
                metadata["type_detail"] = "Certificate"
        
        return doc_type, metadata

    def generate_new_name(self, filepath, doc_type, metadata):
        """Generates the new filename based on rules."""
        # Rules:
        # 1. Policy: Insured_Company_DEC_EFF_Date
        # 2. Invoice: Insured_Company_Invoice_Date
        # 3. Certificate: Insured_type_Date
        
        ext = os.path.splitext(filepath)[1]
        insured = metadata.get("insured_name", "Unknown")
        company = metadata.get("company_name", "Unknown")
        date = metadata.get("date", "NoDate")

        new_name = ""
        if doc_type == DocumentType.POLICY:
            new_name = f"{insured}_{company}_DEC_EFF_{date}{ext}"
        elif doc_type == DocumentType.INVOICE:
            new_name = f"{insured}_{company}_Invoice_{date}{ext}"
        elif doc_type == DocumentType.CERTIFICATE:
            cert_type = metadata.get("type_detail", "Certificate")
            new_name = f"{insured}_{cert_type}_{date}{ext}"
        else:
            # Fallback
            new_name = f"Unknown_{os.path.basename(filepath)}"
            
        return new_name

    def rename_file(self, filepath, new_name):
        """Renames the file."""
        directory = os.path.dirname(filepath)
        new_path = os.path.join(directory, new_name)
        
        # Avoid overwriting
        if os.path.exists(new_path):
            base, extension = os.path.splitext(new_name)
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(directory, f"{base}_{counter}{extension}")
                counter += 1
                
        try:
            os.rename(filepath, new_path)
            return new_path
        except OSError as e:
            return f"Error: {e}"
