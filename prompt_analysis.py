from thefuzz import process
import re
from datetime import datetime, timedelta
import requests
from difflib import get_close_matches
import csv
import ast

class CompanyInfoExtractor:
    def __init__(self, file_paths, threshold=60):
        self.file_paths = file_paths
        self.threshold = threshold  # Similarity min score
        
        
        # Read the corresponding files
        self.company_names = self.read_file(file_paths["company_names"])
        self.abbreviations = self.read_file(file_paths["abbreviations"])
        
        
        
        
        
        
        
    # Read function
    def read_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
        
        
        
        
        
        

    
    @staticmethod
    def normalize_text(text):
        turkish_to_english = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        return text.translate(turkish_to_english).lower()







    @staticmethod
    def get_duckduckgo_popularity(company_name):
        try:
            # DuckDuckGo API endpoint
            url = f"https://api.duckduckgo.com/?q={company_name}&format=json&pretty=1"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            
            # Check if 'RelatedTopics' exists and is a list
            if 'RelatedTopics' in data and isinstance(data['RelatedTopics'], list):
                return len(data['RelatedTopics'])
            
            # Check if 'AbstractText' exists and is non-empty
            if 'AbstractText' in data and data['AbstractText']:
                return len(data['AbstractText'])
            
            # Check if 'Results' exists and is a list
            if 'Results' in data and isinstance(data['Results'], list):
                return len(data['Results'])
            
            print(f"No related topics, abstract text, or results found for {company_name}")
            return 0
        except requests.RequestException as e:
            print(f"Request error fetching popularity for {company_name}: {e}")
            return 0
        except ValueError as e:
            print(f"JSON decoding error for {company_name}: {e}")
            return 0
        except KeyError as e:
            print(f"Unexpected data structure for {company_name}: {e}")
            return 0
  
    
    
    
     
    
    def read_and_update_csv(self, file_path):
    
        sirketler = {}
        variations_to_official = {}
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                official_name = row[0]
                variations = ast.literal_eval(row[1])
                variations.append(official_name)  
                sirketler[official_name] = variations
                for variation in variations:
                    variations_to_official[variation] = official_name
        return sirketler, variations_to_official
    
    
    
    
    
    
    
    def find_most_similar(self, text, names, variations_to_official):
        normalized_names = [self.normalize_text(name) for name in names]
        match = process.extractOne(text, normalized_names)
        if match and match[1] >= self.threshold:
            name = names[normalized_names.index(match[0])]
            official_name = variations_to_official[name]
            return official_name, match[1]
        return None, 0


   
    @staticmethod
    def generate_segments(text, window_size):
        words = text.split()
        return [' '.join(words[i:i + window_size]) for i in range(len(words) - window_size + 1)]


    
    def match_text(self, input_text, names, variations_to_official):
        best_match = None
        chosen_segment = None
        highest_blended_score = self.threshold

      
        for window_size in range(1, 4):
            segments = self.generate_segments(input_text, window_size)
            for segment in segments:
                match, similarity_score = self.find_most_similar(segment, names, variations_to_official)
                if match:
                    try:
                        popularity_score = 0#self.get_duckduckgo_popularity(match)
                        print(f"Popularity for {match}: {popularity}")
                    except:
                        popularity_score = 0  # Default to 0 if there is no internet connection

                    
                    blended_score = (similarity_score * 0.67) + (popularity_score * 0.33)

                    if blended_score > highest_blended_score:
                        highest_blended_score = blended_score
                        best_match = match
                        chosen_segment = segment
                        

        if best_match:
            return best_match, highest_blended_score, chosen_segment

        return "No similar found.", 0, None

   
   
   
   
   
    
    
    @staticmethod
    def extract_dates(input_text, original_text):
        today = datetime.now()
        today = datetime.now()
        date_formats = {
            "bu sene": (datetime(today.year, 1, 1), today),
            "bu yil": (datetime(today.year, 1, 1), today),
            "gecen sene": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 12, 31)),
            "gecen yil": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 12, 31)),
            "son ceyrek": (datetime(today.year, ((today.month - 1) // 3) * 3 + 1, 1), today),
            "bu yilin birinci ceyregi": (datetime(today.year, 1, 1), datetime(today.year, 3, 31)),
            "bu yilin ikinci ceyregi": (datetime(today.year, 4, 1), datetime(today.year, 6, 30)),
            "bu yilin ucuncu ceyregi": (datetime(today.year, 7, 1), datetime(today.year, 9, 30)),
            "bu yilin dorduncu ceyregi": (datetime(today.year, 10, 1), datetime(today.year, 12, 31)),
            "gecen yilin birinci ceyregi": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 3, 31)),
            "gecen yilin ikinci ceyregi": (datetime(today.year - 1, 4, 1), datetime(today.year - 1, 6, 30)),
            "gecen yilin ucuncu ceyregi": (datetime(today.year - 1, 7, 1), datetime(today.year - 1, 9, 30)),
            "gecen yilin dorduncu ceyregi": (datetime(today.year - 1, 10, 1), datetime(today.year - 1, 12, 31)),
            "bu senenin birinci ceyregi": (datetime(today.year, 1, 1), datetime(today.year, 3, 31)),
            "bu senenin ikinci ceyregi": (datetime(today.year, 4, 1), datetime(today.year, 6, 30)),
            "bu senenin ucuncu ceyregi": (datetime(today.year, 7, 1), datetime(today.year, 9, 30)),
            "bu senenin dorduncu ceyregi": (datetime(today.year, 10, 1), datetime(today.year, 12, 31)),
            "gecen senenin birinci ceyregi": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 3, 31)),
            "gecen senenin ikinci ceyregi": (datetime(today.year - 1, 4, 1), datetime(today.year - 1, 6, 30)),
            "gecen senenin ucuncu ceyregi": (datetime(today.year - 1, 7, 1), datetime(today.year - 1, 9, 30)),
            "gecen senenin dorduncu ceyregi": (datetime(today.year - 1, 10, 1), datetime(today.year - 1, 12, 31))
        }


        date_patterns = [
            r'\b(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{4})\b',
            r'\b(\d{1,2})\s+(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\s+(\d{4})\b',
            r'\b(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\s+(\d{4})\b',
            r'\b(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)\s+(ayi)\b'
        ]

        dynamic_patterns = [
            (r"(\d{4}) yili", lambda m: (datetime(int(m.group(1)), 1, 1), datetime(int(m.group(1)), 12, 31))),
            (r"(\d{4}) yilinin birinci ceyregi", lambda m: (datetime(int(m.group(1)), 1, 1), datetime(int(m.group(1)), 3, 31))),
            (r"(\d{4}) yilinin ikinci ceyregi", lambda m: (datetime(int(m.group(1)), 4, 1), datetime(int(m.group(1)), 6, 30))),
            (r"(\d{4}) yilinin ucuncu ceyregi", lambda m: (datetime(int(m.group(1)), 7, 1), datetime(int(m.group(1)), 9, 30))),
            (r"(\d{4}) yilinin dorduncu ceyregi", lambda m: (datetime(int(m.group(1)), 10, 1), datetime(int(m.group(1)), 12, 31)))
        ]
     
        extracted_dates = []
        
        # Check for predefined date formats
        for key, (start, end) in date_formats.items():
            if key in input_text:
                extracted_dates.append(start)
                extracted_dates.append(end)
                
                start_index = input_text.index(key)
                end_index = start_index + len(key)
                
                original_text = original_text[:start_index] + '' + original_text[end_index:]
                
                input_text = input_text.replace(key, "")
                if len(extracted_dates) == 2:
                    return extracted_dates, input_text, original_text

        # Check for dynamic patterns
        for pattern, func in dynamic_patterns:
            match = re.search(pattern, input_text)
            if match:
                extracted_dates.append(func(match))
                
                start_index, end_index = match.span()
                
                original_text = original_text[:start_index] + '' + original_text[end_index:]
        
                input_text = re.sub(pattern, '', input_text, count=1)
                if len(extracted_dates) == 2:
                    return extracted_dates, input_text, original_text

        # Check for specific date patterns
        regex = re.compile(date_patterns[0], re.IGNORECASE)
        matches = regex.findall(input_text)

        for match in matches:
            day, month, year = int(match[0]), int(match[1]), int(match[2])
            extracted_dates.append(datetime(year, month, day))
            
            start_index = input_text.index(match[0]) 
            end_index = input_text.index(match[2]) + len(match[2])
            
            original_text = original_text[:start_index] + ' ' + original_text[end_index:]
            
            input_text = re.sub(regex, '', input_text, count=1)
            if len(extracted_dates) == 2:
                return extracted_dates, input_text, original_text

        regex = re.compile(date_patterns[1], re.IGNORECASE)
        matches = regex.findall(input_text)

        for match in matches:
            day, month, year = int(match[0]), match[1], int(match[2])
            month_number = {
                'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4,
                'mayis': 5, 'haziran': 6, 'temmuz': 7, 'agustos': 8,
                'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12
            }[month]
            extracted_dates.append(datetime(year, month_number, day))
            
            start_index = input_text.index(match[0])
            end_index = input_text.index(match[2]) + len(match[2])
            
            original_text = original_text[:start_index] + ' ' + original_text[end_index:]
    
            
            input_text = re.sub(regex, '', input_text, count=1)
            if len(extracted_dates) == 2:
                return extracted_dates, input_text, original_text
            
        regex = re.compile(date_patterns[2], re.IGNORECASE)
        matches = regex.findall(input_text)

        for match in matches:
            month, year = match[0], int(match[1])
            month_number = {
                'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4,
                'mayis': 5, 'haziran': 6, 'temmuz': 7, 'agustos': 8,
                'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12
            }[month]
            
            if len(extracted_dates) == 0:
                extracted_dates.append(datetime(year, month_number, 1))
                if month_number != 12:
                    extracted_dates.append(datetime(year, month_number+1, 1))
                else:
                    extracted_dates.append(datetime(year+1, 1, 1))
            else:
                return extracted_dates, input_text, original_text
            
            start_index = input_text.index(match[0])
            end_index = input_text.index(match[1]) + len(match[1])
            
            original_text = original_text[:start_index] + ' ' + original_text[end_index:]
    
            
            input_text = re.sub(regex, '', input_text, count=1)
            if len(extracted_dates) == 2:
                return extracted_dates, input_text, original_text
            
        regex = re.compile(date_patterns[3], re.IGNORECASE)
        matches = regex.findall(input_text)

        for match in matches:
            month = match[0]
            month_number = {
                'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4,
                'mayis': 5, 'haziran': 6, 'temmuz': 7, 'agustos': 8,
                'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12
            }[month]
            
            if len(extracted_dates) == 0:
                extracted_dates.append(datetime(today.year, month_number, 1))
                if month_number != 12:
                    extracted_dates.append(datetime(today.year, month_number+1, 1))
                else:
                    extracted_dates.append(datetime(today.year+1, 1, 1))
            else:
                return extracted_dates, input_text, original_text
            
            start_index = input_text.index(match[0])
            
            if match[0] != "mayis":
                end_index = input_text.index(match[1]) + len(match[1])
            else:
                first_index = input_text.find(match[1])
                end_index = input_text.find(match[1], first_index + len(match[1])) + len(match[1])
            
            
            original_text = original_text[:start_index] + ' ' + original_text[end_index:]
            
            input_text = re.sub(regex, '', input_text, count=1)
            if len(extracted_dates) == 2:
                return extracted_dates, input_text, original_text
                
        
        if len(extracted_dates) == 0:
            end = datetime.now()
            start = end - timedelta(days=90)
            extracted_dates.append(start)
            extracted_dates.append(end)
        return extracted_dates, input_text, original_text






    def remove_substring(self, original_prompt, turkish_prompt, substr):
        # Split both strings into words
        original_words = original_prompt.split()
        turkish_words = turkish_prompt.split()
        substr_words = substr.split()
        
        if len(original_words) != len(turkish_words):
            raise ValueError("The length of original_prompt and turkish_prompt must be the same.")
        
        # Function to find the starting index of a substring in a list of words
        def find_substring_indices(words, substr_words):
            for i in range(len(words) - len(substr_words) + 1):
                if words[i:i + len(substr_words)] == substr_words:
                    return range(i, i + len(substr_words))
            return None
        
        # Find indices of the substring in both original and turkish prompts
        indices_to_remove = find_substring_indices(original_words, substr_words)
        
        if indices_to_remove is None:
            return original_prompt, turkish_prompt
        
        # Remove the indices from both lists
        cleaned_original_words = [word for i, word in enumerate(original_words) if i not in indices_to_remove]
        cleaned_turkish_words = [word for i, word in enumerate(turkish_words) if i not in indices_to_remove]
        
        # Join the remaining words back into a single string
        cleaned_original_prompt = ' '.join(cleaned_original_words)
        cleaned_turkish_prompt = ' '.join(cleaned_turkish_words)
        
        return cleaned_original_prompt, cleaned_turkish_prompt
    
    
    
    
    
    
    
    def get_extracted_notification_info(self, input_text):
        
        original_input = input_text
        input_text = self.normalize_text(input_text)
        
        
        
        
        
        ################## SIRKET #####################
        
        file_path = 'promptdict.csv'  # Path to CSV file
        sirketler, variations_to_official = self.read_and_update_csv(file_path)

        # Flatten the company names for processed names
        all_names = list(variations_to_official.keys())

        
        # Match company names and get corresponding abbreviation
        sirket_adi, score_name, segment = self.match_text(input_text, all_names, variations_to_official)
       
        prompt_without_sirket, original_input = self.remove_substring(input_text, original_input, segment)
        
        borsa_adi = self.abbreviations[self.company_names.index(sirket_adi)]    
      
        #################################################
        
        
        
        
        
        
        ################## BILDIRIM #####################
        
        bildirim_turleri = {
            "FR": ["finansal rapor", "finansal raporlar", "bilanco", "gelir tablosu", "finansal durum", 'gelir', 'gider', 'duran varliklar', 'donen varliklar', 'nakit akisi', 'net kar', 'brut kar', 'ozsermaye', 'borc', 'karlilik', 'yukumluluk', 'kisa vadeli yukumluluk', 'uzun vadeli yukumluluk', 'cari oran'],
            "ÖDA": ["ozel durum", "aciklama", "yeni is iliskisi", "is iliskisi", "ozel durum aciklamalari", "ozel durum aciklamasi"],
            "DKM": ["duzenleyici kurum", "duzenleyici kurum bildirimleri", "duzenleyici kurum bildirimi"],
            "DG": ["diger"]
        }

       
        tokens = prompt_without_sirket.split()
   
       
        bildirim_tipi = None
        bildirim_token = None
        best_match_score = 0
        for token_index in range(len(tokens)):
            for length in range(1, 4):
                potential_name = " ".join(tokens[token_index:token_index+length])
                for adi, adlar in bildirim_turleri.items():
                    for adi_variation_eng in adlar:
                        score = 0
                        if potential_name.lower() in adi_variation_eng.lower():
                            score = 0.8
                        else:
                            matches = get_close_matches(potential_name.lower(), [adi_variation_eng.lower()], n=1, cutoff=0.85)
                            if matches:
                                score = 0.9
                        if score > best_match_score:
                            best_match_score = score
                            bildirim_tipi = adi
                            bildirim_token = tokens[token_index:token_index+length]
                     

        if bildirim_tipi:
            prompt_without_bildirim = prompt_without_sirket
        else:
            bildirim_tipi = "TB"
            prompt_without_bildirim = prompt_without_sirket
            
    
        #################################################
        
        
        
        
        
        
        
        ################## TARIHLER #####################
        
        
        dates, prompt_without_date, original_input = self.extract_dates(prompt_without_bildirim, original_input)
        
        
        #################################################
      
      
      
      
        # Extracted Params
        print(f"Bildirim Tipi : {bildirim_tipi}")
        print(f"Şirket Adı : {sirket_adi}")
        print(f"Borsa Adı : {borsa_adi}")
        print(f"Soru : {original_input}")
        print(f"Prompt : {prompt_without_date}")
      
        
        
        return {
            "notification_type": bildirim_tipi,
            "selected_name": sirket_adi,
            "extracted_dates": [date for date in dates],
            "selected_abbrev": borsa_adi,
            "question": original_input
        }
