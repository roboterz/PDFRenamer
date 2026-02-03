import json
import os

class SurnameMatcher:
    def __init__(self, json_path):
        self.surnames = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.surnames = json.load(f)
        except Exception as e:
            print(f"Error loading surnames: {e}")
            
        # Hardcoded set of valid pinyin syllables (without tones)
        # This list covers standard Mandarin pinyin.
        self.pinyin_syllables = {
            "a", "ai", "an", "ang", "ao",
            "ba", "bai", "ban", "bang", "bao", "bei", "ben", "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu",
            "ca", "cai", "can", "cang", "cao", "ce", "cen", "ceng", "cha", "chai", "chan", "chang", "chao", "che", "chen", "cheng", "chi", "chong", "chou", "chu", "chua", "chuai", "chuan", "chuang", "chui", "chun", "chuo", "ci", "cong", "cou", "cu", "cuan", "cui", "cun", "cuo",
            "da", "dai", "dan", "dang", "dao", "de", "dei", "den", "deng", "di", "dian", "diao", "die", "ding", "diu", "dong", "dou", "du", "duan", "dui", "dun", "duo",
            "e", "ei", "en", "eng", "er",
            "fa", "fan", "fang", "fei", "fen", "feng", "fo", "fou", "fu",
            "ga", "gai", "gan", "gang", "gao", "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan", "guang", "gui", "gun", "guo",
            "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong", "hou", "hu", "hua", "huai", "huan", "huang", "hui", "hun", "huo",
            "ji", "jia", "jian", "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun",
            "ka", "kai", "kan", "kang", "kao", "ke", "kei", "ken", "keng", "kong", "kou", "ku", "kua", "kuai", "kuan", "kuang", "kui", "kun", "kuo",
            "la", "lai", "lan", "lang", "lao", "le", "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling", "liu", "long", "lou", "lu", "lv", "luan", "lue", "lun", "luo",
            "ma", "mai", "man", "mang", "mao", "me", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "miu", "mo", "mou", "mu",
            "na", "nai", "nan", "nang", "nao", "ne", "nei", "nen", "neng", "ni", "nian", "niang", "niao", "nie", "nin", "ning", "niu", "nong", "nou", "nu", "nv", "nuan", "nue", "nuo",
            "o", "ou",
            "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng", "pi", "pian", "piao", "pie", "pin", "ping", "po", "pou", "pu",
            "qi", "qia", "qian", "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun",
            "ran", "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "ruan", "rui", "run", "ruo",
            "sa", "sai", "san", "sang", "sao", "se", "sen", "seng", "sha", "shai", "shan", "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai", "shuan", "shuang", "shui", "shun", "shuo", "si", "song", "sou", "su", "suan", "sui", "sun", "suo",
            "ta", "tai", "tan", "tang", "tao", "te", "teng", "ti", "tian", "tiao", "tie", "ting", "tong", "tou", "tu", "tuan", "tui", "tun", "tuo",
            "wa", "wai", "wan", "wang", "wei", "wen", "weng", "wo", "wu",
            "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing", "xiong", "xiu", "xu", "xuan", "xue", "xun",
            "ya", "yan", "yang", "yao", "ye", "yi", "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun",
            "za", "zai", "zan", "zang", "zao", "ze", "zei", "zen", "zeng", "zha", "zhai", "zhan", "zhang", "zhao", "zhe", "zhei", "zhen", "zheng", "zhi", "zhong", "zhou", "zhu", "zhua", "zhuai", "zhuan", "zhuang", "zhui", "zhun", "zhuo", "zi", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo"
        }

    def _is_pinyin(self, word):
        """Checks if a word is a likely Pinyin syllable."""
        return word.lower() in self.pinyin_syllables

    def find_potential_names(self, text):
        candidates = []
        text_tokens = text.split()
        
        # Flatten Pinyin/Surname list
        surname_pinyins = set()
        for entry in self.surnames:
            for p in entry.get('pinyin', []):
                surname_pinyins.add(p.lower())
                
        stopwords = {
            "the", "is", "for", "by", "of", "and", "to", "in", "on", "at", 
            "customer", "insured", "name", "policy", "number", "agent", "date",
            "page", "total", "amount", "due", "paid", "payment", "from", "bill",
            "effective", "coverage", "insurance", "premium", "declaration", "certificate",
            "endorsement", "period", "issue", "issued", "producer", "agency", "company",

            "description", "item", "location", "check", "cancelled"
        }

        def clean_token(token):
            t = token.strip("()\"',-:")
            if not t: return None
            if t.endswith('.') and len(t) == 2 and t[0].isalpha(): return t # Initial
            return t.strip(".")

        def is_alpha_or_initial(w):
            if w.endswith('.'): return w[:-1].isalpha()
            return w.isalpha()

        for i in range(len(text_tokens)):
            if i + 1 >= len(text_tokens): break
            
            t1 = text_tokens[i]
            t2 = text_tokens[i+1]
            t3 = text_tokens[i+2] if i + 2 < len(text_tokens) else None
            
            w1 = clean_token(t1)
            w2 = clean_token(t2)
            w3 = clean_token(t3) if t3 else None
            
            if not w1 or not w2: continue
            if not is_alpha_or_initial(w1) or not is_alpha_or_initial(w2): continue
            
            # --- Check 3-Word Pattern (Strict) ---
            if w3 and is_alpha_or_initial(w3):
                 if w1[0].isupper() and w2[0].isupper() and w3[0].isupper():
                     w1_lower = w1.lower().strip('.')
                     w2_lower = w2.lower().strip('.')
                     w3_lower = w3.lower().strip('.')
                     
                     if (w1_lower not in stopwords and w2_lower not in stopwords and w3_lower not in stopwords):
                         
                         is_surname_1 = w1_lower in surname_pinyins
                         is_surname_3 = w3_lower in surname_pinyins
                         
                         # Scenario A: Standard Chinese (Surname Given Given) or (Given Given Surname)
                         # Strict: Non-surname parts MUST be pinyin
                         candidate_accepted = False
                         
                         if is_surname_1:
                             # Start is Surname. Check Rest.
                             # e.g. Wang Xiao Ming
                             # Xiao and Ming must be pinyin
                             if self._is_pinyin(w2_lower) and self._is_pinyin(w3_lower):
                                 candidate_accepted = True
                             # e.g. Wang A. Ming (Initial Middle)
                             elif w2.endswith('.') or w2_lower.isalpha() and len(w2)==1: # Initial
                                  candidate_accepted = True
                         
                         elif is_surname_3:
                             # End is Surname. Check Start.
                             # e.g. Xiao Ming Wang
                             if self._is_pinyin(w1_lower) and self._is_pinyin(w2_lower):
                                 candidate_accepted = True
                             # e.g. John A. Wang
                             elif w2.endswith('.') or len(w2)==1:
                                 candidate_accepted = True
                                 
                         if candidate_accepted:
                             candidates.append(f"{w1} {w2} {w3}")

            # --- Check 2-Word Pattern ---
            if w1[0].isupper() and w2[0].isupper():
                 w1_lower = w1.lower().strip('.')
                 w2_lower = w2.lower().strip('.')
                 
                 if w1_lower not in stopwords and w2_lower not in stopwords:
                     is_surname_1 = w1_lower in surname_pinyins
                     is_surname_2 = w2_lower in surname_pinyins
                     
                     candidate_accepted = False
                     
                     if is_surname_1:
                         # e.g. Wang Wei (Wei must be pinyin)
                         if self._is_pinyin(w2_lower):
                             candidate_accepted = True
                         elif w2.endswith('.') or (w2_lower.isalpha() and len(w2)==1): # Initial
                             candidate_accepted = True
                             
                     elif is_surname_2:
                         # e.g. Wei Wang (Wei must be pinyin)
                         if self._is_pinyin(w1_lower):
                             candidate_accepted = True
                         elif w1.endswith('.') or (w1_lower.isalpha() and len(w1)==1): # Initial
                             candidate_accepted = True
                             
                     if candidate_accepted:
                         candidates.append(f"{w1} {w2}")

        unique_candidates = list(set(candidates))
        unique_candidates.sort(key=len, reverse=True)
        return unique_candidates
