import re
from datetime import datetime, timedelta
from difflib import get_close_matches
from dateutil import parser
import traceback
import sorgu5
import pandas as pd
import ast


def csvtodict(csv_path='promptdict.csv'):
    df = pd.read_csv(csv_path)

    company_dict = {}

    for index, row in df.iterrows():
        company_name = row[0]
        abbreviations = ast.literal_eval(row[1])
        company_dict[company_name] = abbreviations

    return company_dict

def turkce_to_ingilizce(text):
    turkish_chars = "çÇğĞıİöÖşŞüÜ"
    english_equivalents = "cCgGiIoOsSuU"
    tr_to_eng_map = str.maketrans(turkish_chars, english_equivalents)
    return text.translate(tr_to_eng_map)

def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()  # Start with dict1's keys and values
    for key, value in dict2.items():
        if key in merged_dict:
            if isinstance(merged_dict[key], list):
                if isinstance(value, list):
                    merged_dict[key].extend(value)
                else:
                    merged_dict[key].append(value)
            else:
                merged_dict[key] = [merged_dict[key], value] if not isinstance(value, list) else [merged_dict[key]] + value
        else:
            merged_dict[key] = value
    return merged_dict

def extract_dates(prompt):
    today = datetime.now()
    date_formats = {
        "bu sene": (datetime(today.year, 1, 1), today),
        "gecen sene": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 12, 31)),
        "son ceyrek": (datetime(today.year, ((today.month - 1) // 3) * 3 + 1, 1), today),
        "bu yilin birinci ceyregi": (datetime(today.year, 1, 1), datetime(today.year, 3, 31)),
        "bu yilin ikinci ceyregi": (datetime(today.year, 4, 1), datetime(today.year, 6, 30)),
        "bu yilin ucuncu ceyregi": (datetime(today.year, 7, 1), datetime(today.year, 9, 30)),
        "bu yilin dorduncu ceyregi": (datetime(today.year, 10, 1), datetime(today.year, 12, 31)),
        "gecen yilin birinci ceyregi": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 3, 31)),
        "gecen yilin ikinci ceyregi": (datetime(today.year - 1, 4, 1), datetime(today.year - 1, 6, 30)),
        "gecen yilin ucuncu ceyregi": (datetime(today.year - 1, 7, 1), datetime(today.year - 1, 9, 30)),
        "gecen yilin dorduncu ceyregi": (datetime(today.year - 1, 10, 1), datetime(today.year - 1, 12, 31)),
    }
    
    # Dinamik çeyrek ve yıl belirleme
    date_patterns = [
        (r"(\d{4}) yili", lambda m: (datetime(int(m.group(1)), 1, 1), datetime(int(m.group(1)), 12, 31))),
        (r"(\d{4}) yilinin birinci ceyregi", lambda m: (datetime(int(m.group(1)), 1, 1), datetime(int(m.group(1)), 3, 31))),
        (r"(\d{4}) yilinin ikinci ceyregi", lambda m: (datetime(int(m.group(1)), 4, 1), datetime(int(m.group(1)), 6, 30))),
        (r"(\d{4}) yilinin ucuncu ceyregi", lambda m: (datetime(int(m.group(1)), 7, 1), datetime(int(m.group(1)), 9, 30))),
        (r"(\d{4}) yilinin dorduncu ceyregi", lambda m: (datetime(int(m.group(1)), 10, 1), datetime(int(m.group(1)), 12, 31)))
    ]
    
    for key, (start_date, end_date) in date_formats.items():
        if key in prompt:
            return start_date, end_date, prompt.replace(key, "").strip()
    
    for pattern, func in date_patterns.items():
        match = re.search(pattern, prompt)
        if match:
            return func(match) + (re.sub(pattern, "", prompt).strip(),)
    
    return None, None, prompt

# Şirket listesi ve borsadaki kısaltmaları

sorgu = sorgu5.Sorgu("ADEL","2024-03-27","2024-07-12")
sirketisimleri = sorgu.getCompanyNames()
sirketkodlari = sorgu.getStockCodes()
csv_dict = csvtodict()
sirketler = dict(zip(sirketisimleri, sirketkodlari))
sirketler = merge_dicts(sirketler, csv_dict)

# Prompt ==============================================================================
prompt = "turk telekom mart 2024 - nisan 2024 arasi finansal rapor falan filan"

def parse_date(date_str):
    months = {
        "ocak": "01", "subat": "02", "mart": "03", "nisan": "04", "mayis": "05", "haziran": "06",
        "temmuz": "07", "agustos": "08", "eylul": "09", "ekim": "10", "kasim": "11", "aralik": "12"
    }
    
    parts = date_str.split()
    day = parts[0]
    month = months.get(parts[1].lower())
    year = parts[2]
    
    return f"{day}.{month}.{year}"

def extract_info(prompt):
    prompt = turkce_to_ingilizce(prompt)

    # Bildirim türünü belirlemek
# ILGILI KELIMELER !====================================================================
    bildirim_turleri = {
        "FR": ["finansal raporlar", "finansal rapor", "finans", "bilanco", "gelir tablosu", "finansal durum", 'gelir','gider','duran varliklar','donen varliklar','nakit akisi','net kar','brut kar','ozsermaye','borc','karlilik','yukumluluk','kisa vadeli yukumluluk', 'uzun vadeli yukumluluk','cari oran'],
        "ÖDA": ["ozel durum", "aciklama", "yeni is iliskisi", "is iliskisi", "ozel durum aciklamalari", "ozel durum aciklamasi"],
        "DKM": ["duzenleyici kurum", "duzenleyici kurum bildirimleri", "duzenleyici kurum bildirimi"],
        "DG": ["diger"]
    }
    

    bildirim_turu = None
    matched_word = None
    tokens = prompt.split()

    for token in tokens:
        for tur, kelimeler in bildirim_turleri.items():
            for kelime in kelimeler:
                if token.lower() in kelime or difflib.get_close_matches(token.lower(), [kelime], n=1, cutoff=0.8):
                    bildirim_turu = tur
                    matched_word = kelime
                    break
            if bildirim_turu:
                break
        if bildirim_turu:
            break

    if bildirim_turu is None:
        bildirim_turu = ''

    # Remove the matched word from the prompt
    if matched_word:
        prompt = ' '.join([token for token in tokens if token.lower() not in matched_word])
        print(prompt)
    
    # Tarih aralığını belirlemek
    try:
        baslangic_tarihi, bitis_tarihi, prompt = extract_dates(prompt)
    except:
        baslangic_tarihi = None
        bitis_tarihi = None

    if not baslangic_tarihi and not bitis_tarihi:
        tarih_araligi = re.search(r"(\d{1,2}\s+\w+\s+\d{4})\s*-\s*(\d{1,2}\s+\w+\s+\d{4})", prompt)
        if not tarih_araligi:
            tarih_araligi = re.search(r"(\d{1,2}\s+\w+\s+\d{4})\s+(\d{1,2}\s+\w+\s+\d{4})", prompt)
        if not tarih_araligi:
            tek_tarih = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", prompt)
            if tek_tarih:
                baslangic_tarihi_str = tek_tarih.group(1)
                bitis_tarihi_str = baslangic_tarihi_str
                baslangic_tarihi = datetime.strptime(parse_date(baslangic_tarihi_str), "%d.%m.%Y")
                bitis_tarihi = baslangic_tarihi
            else:
                # Tarih aralığı bulunamazsa bugünü ve üç ay öncesini al
                bitis_tarihi = datetime.now()
                baslangic_tarihi = bitis_tarihi - timedelta(days=90)
        else:
            baslangic_tarihi_str = tarih_araligi.group(1)
            bitis_tarihi_str = tarih_araligi.group(2)
            baslangic_tarihi = datetime.strptime(parse_date(baslangic_tarihi_str), "%d.%m.%Y")
            bitis_tarihi = datetime.strptime(parse_date(bitis_tarihi_str), "%d.%m.%Y")
        
        # Tarih girdisini prompt'tan çıkar
        prompt_without_dates = re.sub(r"(\d{1,2}\s+\w+\s+\d{4})\s*-\s*(\d{1,2}\s+\w+\s+\d{4})", "", prompt)
        prompt_without_dates = re.sub(r"(\d{1,2}\s+\w+\s+\d{4})\s+(\d{1,2}\s+\w+\s+\d{4})", "", prompt_without_dates)
        prompt_without_dates = re.sub(r"(\d{1,2}\s+\w+\s+\d{4})", "", prompt_without_dates)
    else:
        prompt_without_dates = prompt
    

    # Prompt'ı tokenlere ayır
    tokens = prompt_without_dates.split()
    print(prompt_without_dates)

    # Şirket adını belirlemek
    sirket_adi = None
    adli_token = None
    best_match_score = 0
    for token_index in range(len(tokens)):
        for length in range(1, 4):
            potential_name = " ".join(tokens[token_index:token_index+length])
            for adi, adlar in sirketler.items():
                for adi_variation in adlar:
                    adi_variation_eng = turkce_to_ingilizce(adi_variation)
                    score = 0
                    if potential_name.lower() in adi_variation_eng.lower():
                        score = 0.8
                    else:
                        matches = get_close_matches(potential_name.lower(), [adi_variation_eng.lower()], n=1, cutoff=0.85)
                        if matches:
                            score = 0.9
                    if score > best_match_score:
                        best_match_score = score
                        sirket_adi = adi
                        adli_token = tokens[token_index:token_index+length]

    # Şirket adını prompt'tan çıkar
    if sirket_adi:
        prompt_without_sirket = prompt_without_dates
        for token in adli_token:
            prompt_without_sirket = prompt_without_sirket.replace(token, "", 1)
        prompt_without_sirket = ' '.join(prompt_without_sirket.split())
    else:
        prompt_without_sirket = prompt_without_dates

    
    return bildirim_turu, baslangic_tarihi, bitis_tarihi, sirket_adi, prompt_without_sirket


# Fonksiyonu çağır ve sonuçları yazdır
try:
    bildirim_turu, baslangic_tarihi, bitis_tarihi, sirket_adi, remaining_prompt = extract_info(prompt)
    if sirket_adi == None:
        sirket_adi = ''
    print("Bildirim Türü:", bildirim_turu)
    print("Başlangıç Tarihi:", baslangic_tarihi.strftime("%d.%m.%Y"))
    print("Bitiş Tarihi:", bitis_tarihi.strftime("%d.%m.%Y"))
    print("Şirket Adı:", sirket_adi)
    print("Kalan Prompt:", remaining_prompt)
except ValueError as e:
    traceback.print_exc()
    print("Hata:", e)