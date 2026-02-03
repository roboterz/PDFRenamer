import json
import re

def parse_surnames(input_file, output_file):
    surnames_list = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Column headers based on the user provided text (implied):
    # Index, Char, Mainland, Taiwan, HK, Macau, Singapore, Malaysia, Vietnam, Korea
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') or line.startswith('中文'):
            continue
            
        parts = [p.strip() for p in line.split('\t') if p.strip()]
        
        # Heuristic to check if it's a data line
        # It should start with a number
        if not parts[0].isdigit():
            continue
            
        if len(parts) < 3:
            continue
            
        index = parts[0]
        char_raw = parts[1]
        
        # Clean character (remove comments like 讀「洛」或「惡」)
        # Usually checking for first unicode character that is CJK
        match = re.search(r'[\u4e00-\u9fff]', char_raw)
        if match:
            char = match.group(0)
        else:
            char = char_raw[0] # Fallback
            
        # Collect variants
        # The rest of the columns are variants
        variants_raw = parts[2:]
        variants_set = set()
        
        for v in variants_raw:
            # Split by '/' or ',' or space if it looks like multiple
            # The data uses '/' often
            sub_parts = v.split('/')
            for sp in sub_parts:
                clean_v = sp.strip()
                if clean_v:
                    variants_set.add(clean_v)
                    
        # Sort variants for consistency
        variants = sorted(list(variants_set))
        
        entry = {
            "index": int(index),
            "char": char,
            "char_raw": char_raw,
            "pinyin": variants
        }
        surnames_list.append(entry)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(surnames_list, f, ensure_ascii=False, indent=4)
        
    print(f"Processed {len(surnames_list)} surnames. Saved to {output_file}")

if __name__ == "__main__":
    parse_surnames("e:/AI_WorkPlace/PDFRenamer/surnames_raw.txt", "e:/AI_WorkPlace/PDFRenamer/chinese_surnames_detailed.json")
