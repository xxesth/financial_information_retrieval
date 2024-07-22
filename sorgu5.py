# 0 - KUTUPHANELER

import requests
import json
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import os
import time
import traceback

class Sorgu:

    def __init__(self, stock, fromdate, todate, bildirim='', index='', sector='', market=''):
        self.stock = stock
        self.fromdate = fromdate
        self.todate = todate
        self.bildirim = bildirim
        self.index = index
        self.sector = sector
        self.market = market

    def getCompanyNames(self):
        urll = 'https://www.kap.org.tr/tr/api/kapmembers/IGS/A'
        members = requests.get(urll).json()

        extracted_data = [{"mkkMemberOid": member["mkkMemberOid"], "kapMemberTitle": member["kapMemberTitle"], "stockCode": member["stockCode"]} for member in members]
        kap_member_titles = [entry['kapMemberTitle'] for entry in extracted_data]
        return kap_member_titles
    
    def getCompanyOids(self):
        urll = 'https://www.kap.org.tr/tr/api/kapmembers/IGS/A'
        members = requests.get(urll).json()

        extracted_data = [{"mkkMemberOid": member["mkkMemberOid"], "kapMemberTitle": member["kapMemberTitle"], "stockCode": member["stockCode"]} for member in members]
        kap_mkkMemberOids = [entry['mkkMemberOid'] for entry in extracted_data]
        return kap_mkkMemberOids
    
    def getStockCodes(self):
        urll = 'https://www.kap.org.tr/tr/api/kapmembers/IGS/A'
        members = requests.get(urll).json()

        extracted_data = [{"mkkMemberOid": member["mkkMemberOid"], "kapMemberTitle": member["kapMemberTitle"], "stockCode": member["stockCode"]} for member in members]
        kap_stockCodes = [entry['stockCode'] for entry in extracted_data]
        return kap_stockCodes
        
    def codeOids(self):
        def find_index_of_element(element, lst):
            try:
                index = lst.index(str(element))
                return int(index)
            except ValueError:
                return None 

        lst = self.getStockCodes()
        element = str(self.stock)
        indeks = find_index_of_element(element,lst)
        oid = self.getCompanyOids()[indeks]
        return oid
    
    def downloadQuery(self):
        url: str = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"

        from_date = self.fromdate
        to_date = self.todate
        bildirimtipi = self.bildirim
        index = self.index
        market = self.market
        sector = self.sector
        hisse = self.codeOids()


        headers_post = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '394',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': '_ga=GA1.1.1320575248.1719242282; NSC_xxx.lbq.psh.us_tjuf=37cda3dd8e73a26012fe00f5ea2bbe77b978ae0b3749d4a15bf7afc53c8740c3665c4aa1; _ga_MBNFVK7SX4=GS1.1.1719242281.1.1.1719242892.60.0.0; KAP=AAU7KI55Zjv3oCoAAAAAADsUL9ZOBg_0wi2-O8TBNPmu2pvA4Su5CZ-1pHShUHLuOw==h5R5Zg==Elzk9g3efw-jSKp-q88wsR_TjP4=; KAP_.kap.org.tr_%2F_wlf=AAAAAAX071DV2OS6TD-RdOb3jaRgKtJfRjmNCdam_wSxqim7vCpgVmgdBF5VrmWuSRUEVxGAottDYKyaO22S2jx2jPCX7Ct06D_0wMsQV6PPLatCEg==&',
            'Host': 'www.kap.org.tr',
            'Origin': 'https://www.kap.org.tr',
            'Referer': 'https://www.kap.org.tr/tr/bildirim-sorgu',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

        data = {
            "fromDate": from_date,
            "toDate": to_date,
            "year":"",
            "prd":"",
            "term":"",
            "ruleType":"",
            "bdkReview":"",
            "disclosureClass": bildirimtipi,
            "index": index,
            "market": market,
            "isLate":"",
            "subjectList":[],
            "mkkMemberOidList":[hisse],
            "inactiveMkkMemberOidList":[],
            "bdkMemberOidList":[],
            "mainSector":"",
            "sector": sector,
            "subSector":"",
            "memberType":"IGS",
            "fromSrc":"N",
            "srcCategory":"",
            "discIndex":[]
        }

        cookies_post = {
            'KAP' : 'AAU7KI55Zjv3oCoAAAAAADsUL9ZOBg_0wi2-O8TBNPmu2pvA4Su5CZ-1pHShUHLuOw==h5R5Zg==Elzk9g3efw-jSKp-q88wsR_TjP4=',
            'KAP_.kap.org.tr_%2F_wlf' : 'AAAAAAX071DV2OS6TD-RdOb3jaRgKtJfRjmNCdam_wSxqim7vCpgVmgdBF5VrmWuSRUEVxGAottDYKyaO22S2jx2jPCX7Ct06D_0wMsQV6PPLatCEg==&',
            'NSC_xxx.lbq.psh.us_tjuf' : '37cda3dd8e73a26012fe00f5ea2bbe77b978ae0b3749d4a15bf7afc53c8740c3665c4aa1',
            '_ga' : 'GA1.1.1320575248.1719242282',
            '_ga_MBNFVK7SX4' : 'GS1.1.1719242281.1.1.1719242892.60.0.0'
        }

        json_data = json.dumps(data)
        post_res = requests.post(url, headers=headers_post, data=json_data, cookies=cookies_post)

        sirketler = 'sirketler'
        sirket_adi = os.path.join(sirketler, self.stock)
        os.makedirs(sirket_adi, exist_ok=True)

        def pdfindir(url):
            try:
                pdf_number = url.split('/')[-1]
                pdf_filename = f"{url.split('/')[-1]}.pdf"

                pdf_url = f"https://www.kap.org.tr/BildirimPdf/{pdf_number}"
                
                # PDF dosyasını indirin
                pdf_response = requests.get(pdf_url)

                # PDF dosyasını apdf klasöründe kaydedin
                pdf_path = os.path.join(alt_bildirimler_yolu, pdf_filename)

                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)

                print(f'PDF dosyası "{pdf_filename}" başarıyla indirildi ve "{alt_bildirimler_yolu}" klasörüne kaydedildi.')
            except Exception:
                traceback.print_exc()
                print(f"{pdf_filename} pdf indirilemedi, sebep: {Exception.__str__}, {Exception.args}")

        def ekindir(ekler):
            i = 0
            for ekcik in ekler:
                try:
                    indirilecek_link = f"https://www.kap.org.tr{ekcik['href']}"
                    file_response = requests.get(indirilecek_link)
                    filename = os.path.join(alt_bildirimler_yolu, indirilecek_link.split('/')[-1])
                    with open(f"{filename}.pdf", 'wb') as file:
                        file.write(file_response.content)
                
                    print(f'{filename} ek indirildi.')
                except Exception:
                    traceback.print_exc()
                    print(f"{ekcik} ek indirilemedi, sebep: {Exception.__str__}, {Exception.args}")
                    
                # if i%6==0:
                    # time.sleep(10)
                i += 1

        def ozetle(financial_tables, general_tables, get_url, tip, sirketkodu, sirketadi, tarih, ilgili_sirketler, ozet_bilgi, aciklama, modal_info_title):
            tablo = {}
            if (financial_tables):
                try:
                    try:
                        if general_tables:
                            tablocuk = 'DIGER_TABLOCUK'
                            tablo[tablocuk] = {}
                            target_rows = []

                            for table in general_tables:
                                rows = table.find_all(class_='gwt-HTML')
                                target_rows.extend(rows)

                            target_rows = [target_row.text.strip() for target_row in target_rows]

                            for row in target_rows:
                                tablo[tablocuk][row[:10]] = row

                    except:
                        pass

                    try:
                        tablocuk = "TABLOCUK"
                        tablo[tablocuk] = {}
                        for table in financial_tables:
                            rows = table.find_all('tr', class_='presentation-enabled')
                            target_rows.extend(rows)
                        
                        for row in target_rows:
                            try:
                                baslik = row.find('td', class_='taxonomy-field-title').findChild("table").findChild("tbody").findChild("tr").findChild("div", class_='content-tr').text.strip()
                                cevap = row.find('div',class_='taxonomy-label-field').text.strip()
                                tablo[tablocuk][baslik] = cevap
                            except:
                                pass
                    except:
                        pass


                    try:
                        yenidonem = financial_tables[0].findAll("td", class_='context-header')[0].findChild("br").next_sibling.strip()
                    except:
                        yenidonem = ''
                    try:
                        eskidonem = financial_tables[0].findAll("td", class_='context-header')[1].findChild("br").next_sibling.strip()
                    except:
                        eskidonem = ''

                    target_rows = []

                    for table in financial_tables:
                        rows = table.find_all('tr', class_='presentation-enabled')
                        target_rows.extend(rows)
                        
                    for row in target_rows:
                        previous_sibling = row.previous_sibling.previous_sibling
                        if previous_sibling and previous_sibling.name == 'tr' and 'abstract-row' in previous_sibling.get('class', []):
                            buyuk_baslik = previous_sibling.findChild("div", class_="content-tr").text.strip()
                            tablo[buyuk_baslik] = {}
                            baslik = row.find('td', class_='taxonomy-field-title').findChild("table").findChild("tbody").findChild("tr").findChild("div", class_='content-tr').text.strip()
                            yenimiktar = row.find_all('div',class_='taxonomy-label-field')[0].text.strip().replace('.', '').replace(',', '.')
                            eskimiktar = row.find_all('div',class_='taxonomy-label-field')[1].text.strip().replace('.', '').replace(',', '.')
                            tablo[buyuk_baslik][baslik] = {
                                f"{yenidonem}": yenimiktar,
                                f"{eskidonem}": eskimiktar
                            }
                        elif row.find_all('div',class_='taxonomy-label-field')[0].text.strip() != None:
                            baslik = row.find('td', class_='taxonomy-field-title').findChild("table").findChild("tbody").findChild("tr").findChild("div", class_='content-tr').text.strip()
                            yenimiktar = row.find_all('div',class_='taxonomy-label-field')[0].text.strip().replace('.', '').replace(',', '.')
                            eskimiktar = row.find_all('div',class_='taxonomy-label-field')[1].text.strip().replace('.', '').replace(',', '.')
                            tablo[buyuk_baslik][baslik] = {
                                f"{yenidonem}": yenimiktar,
                                f"{eskidonem}": eskimiktar
                            }
                        else:
                            pass
                    

                    girizgah = {
                        "baslik":modal_info_title,
                        "bildirim_türü": tip,
                        "kod": sirketkodu,
                        "ad": sirketadi,
                        "tarih": tarih,
                        "ilgili_sirketler" : ilgili_sirketler,
                        "cari_dönem": yenidonem,
                        "önceki_dönem": eskidonem
                    }
                    yazi = {
                        "ozet" : ozet_bilgi,
                        "aciklama" : aciklama
                    }

                except:
                    try:
                        tablocuk = "TABLOCUK"
                        tablo[tablocuk] = {}
                        for table in financial_tables:
                            rows = table.find_all('tr', class_='presentation-enabled')
                            target_rows.extend(rows)
                        
                        for row in target_rows:
                            try:
                                baslik = row.find('td', class_='taxonomy-field-title').findChild("table").findChild("tbody").findChild("tr").findChild("div", class_='content-tr').text.strip()
                                cevap = row.find('div',class_='taxonomy-label-field').text.strip()
                                tablo[tablocuk][baslik] = cevap
                            except:
                                pass
                    except:
                        pass

                    try:
                        if general_tables:
                            tablocuk = 'DIGER_TABLOCUK'
                            tablo[tablocuk] = {}
                            target_rows = []

                            for table in general_tables:
                                rows = table.find_all(class_='gwt-HTML')
                                target_rows.extend(rows)

                            target_rows = [target_row.text.strip() for target_row in target_rows]
                            print(target_rows)
                            for row in target_rows:
                                tablo[tablocuk][row[:10]] = row

                    except:
                        pass

                    try:
                        girizgah = {
                                "baslik":modal_info_title,
                                "bildirim_türü": tip,
                                "kod": sirketkodu,
                                "ad": sirketadi,
                                "tarih": tarih,
                                "ilgili_sirketler" : ilgili_sirketler
                            }
                        yazi = {
                                        "ozet" : ozet_bilgi,
                                        "aciklama" : aciklama
                                    }
                        tablo = tablo

                        # JSON yapısı oluşturma
                        json_data = {
                            "girizgah": girizgah,
                            "yazi" : yazi,
                            "tablo": tablo
                        }

                        linkkodu = get_url.split('/')[-1]
                        filename = f"{os.path.join(alt_bildirimler_yolu, linkkodu)}.json"

                        # JSON dosyasına yazma
                        with open(filename, 'w', encoding='utf-8') as json_file:
                            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

                        print(f"{get_url} JSON dosyası başarıyla oluşturuldu.")
                    except Exception:
                        traceback.print_exc()
                        print(f"{get_url} ozet ziyan oldu. Hata : {Exception.__str__}, {Exception.args}")
            else:
                try:
                    if general_tables:
                        tablocuk = 'DIGER_TABLOCUK'
                        tablo[tablocuk] = {}
                        target_rows = []

                        for table in general_tables:
                            rows = table.find_all(class_='gwt-HTML')
                            target_rows.extend(rows)

                        target_rows = [target_row.text.strip() for target_row in target_rows]
                        
                        for row in target_rows:
                            tablo[tablocuk][row[:10]] = row

                except:
                    pass

                girizgah = {
                                "baslik":modal_info_title,
                                "bildirim_türü": tip,
                                "kod": sirketkodu,
                                "ad": sirketadi,
                                "tarih": tarih,
                                "ilgili_sirketler" : ilgili_sirketler
                            }
                yazi = {
                                "ozet" : ozet_bilgi,
                                "aciklama" : aciklama
                            }
                tablo = tablo

            # JSON yapısı oluşturma
            json_data = {
                "girizgah": girizgah,
                "yazi" : yazi,
                "tablo": tablo
            }

            linkkodu = get_url.split('/')[-1]
            filename = f"{os.path.join(alt_bildirimler_yolu, linkkodu)}.json"

            # JSON dosyasına yazma
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)

            print(f"{get_url} JSON dosyası başarıyla oluşturuldu.")
        
        tex = post_res.text
        haberler: list = json.loads(tex) # response'dan donen listedir, icinde dictler var her dict bir haberi temsil eder

        codes = [int(haber["disclosureIndex"]) for haber in haberler]

        for haber in haberler:
            
            # haber icin headers, url vs. ayarla
            code: int = haber["disclosureIndex"] # haber kodu

            # Bildirim Klasoru
            bildirimler_dir = str(code)
            alt_bildirimler_yolu = os.path.join(sirket_adi, bildirimler_dir)
            os.makedirs(alt_bildirimler_yolu, exist_ok=True)

            get_url = 'https://www.kap.org.tr/tr/BildirimPopup/' + str(code)
            referer = 'https://www.kap.org.tr/tr/Bildirim/' + str(code)

            headers_get = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Connection': 'keep-alive',
            'Cookie' : '_ga=GA1.1.1320575248.1719242282; _ga_MBNFVK7SX4=GS1.1.1719246406.2.1.1719246415.51.0.0; KAP=AAQ7Qp55Zju3fpkAAAAAADsUL9ZOBg_0wi2-O_NZn3ziBLIQl_amDRn74s3O53HtOw==3aF5Zg==N9kUs6b78jYaowG779RALT4mf6A=; KAP_.kap.org.tr_%2F_wlf=AAAAAAW_YtyW7R1dWuQZtgW00I9y00NlnrQYJvNqFxtT5VGMkHEYS6TyGflIPPIKUEIz_n9jGTqwU_yEs9x6-m11kMoA46Oqf2BIYm6npt15FVFEhQ==&',
            'Host' : 'www.kap.org.tr',
            'If-None-Match' : '"KXBBPGFIFNOMQURV"',
            'Referer' : referer,
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

            cookies_get = {
            '_ga' : 'GA1.1.1320575248.1719242282',
            '_ga_MBNFVK7SX4' : 'GS1.1.1719246406.2.1.1719246415.51.0.0',
            'KAP' : 'AAQ7Qp55Zju3fpkAAAAAADsUL9ZOBg_0wi2-O_NZn3ziBLIQl_amDRn74s3O53HtOw==3aF5Zg==N9kUs6b78jYaowG779RALT4mf6A=',
            'KAP_.kap.org.tr_%2F_wlf' : 'AAAAAAW_YtyW7R1dWuQZtgW00I9y00NlnrQYJvNqFxtT5VGMkHEYS6TyGflIPPIKUEIz_n9jGTqwU_yEs9x6-m11kMoA46Oqf2BIYm6npt15FVFEhQ==&'
        }


            # haber icin get request at
            get_res = requests.get(url=get_url, headers=headers_get, cookies=cookies_get)

            # haberi yazdir
            print(f"\n----------------------------------------------------- ({code})")
            try:
                soup = bs4(get_res.content, 'html.parser')

                pdfindir(get_url)

                # bildirideki ekler, eklerin kaydedilmesi
                ek_bulucu = soup.find_all('a', class_='modal-attachment type-xsmall bi-sky-black maximize')
                ekindir(ek_bulucu)

                # haber basliklari
                try:
                    ilgili_sirketler = soup.findAll('div', class_='gwt-Label')[2].text.strip()
                except:
                    ilgili_sirketler = ''

                try:
                    tip = soup.find_all('div', class_='w-col w-col-3 modal-briefsumcol')[1].findChild("div",class_='type-medium bi-sky-black').text.strip()
                except:
                    tip = ''
                
                try:
                    sirketkodu = soup.find('div', class_='type-medium bi-dim-gray').text.strip()
                except:
                    sirketkodu = ''
                
                try:
                    sirketadi = soup.find('div', class_='type-medium type-bold bi-sky-black').findChild('a').text.strip()
                except:
                    sirketadi = ''
                
                try:
                    tarih = soup.find('div', class_='w-col w-col-3 modal-briefsumcol').findChild("div",class_='type-medium bi-sky-black').text.strip()
                except:
                    tarih = ''

                try:
                    ozet_bilgi = soup.find('div', class_='disclosureSummary').get_text().strip()
                except:
                    ozet_bilgi = ''

                try:
                    aciklama = soup.find('div', class_='text-block-value').text.strip()
                except:
                    aciklama = ''

                try:
                    modal_info_title = soup.find('div', class_='modal-info').findChild('h1').text.strip().split('\n')[0].strip()
                except:
                    modal_info_title = ''

                try:
                    financial_tables = soup.find_all('table', class_='financial-table')
                except:
                    financial_tables = None
                
                try:
                    general_tables = soup.find_all('table', class_='tbl_GK_Report_ID')
                except:
                    general_tables = None

                # JSON
                ozetle(financial_tables,general_tables,get_url,tip,sirketkodu,sirketadi,tarih,ilgili_sirketler,ozet_bilgi,aciklama,modal_info_title)
                    
            except:
                print("HATA!!! Haber dogruca yazdirilamadi. Haber linki: {}".format(get_url))
                if "Bilanço" not in ilgili_sirketler:
                    table = soup.find('div', class_='disclosureScrollableArea').text
                    table_to_print = " ".join(table.split())
                    print("\nBelki:\n",table_to_print)
                    try:
                        aciklama = table_to_print
                    except:
                        aciklama = ""
                
                try:
                    financial_tables = soup.find_all('table', class_='financial-table')
                except: 
                    financial_tables = None
                
                try:
                    general_tables = soup.find_all('table', class_='tbl_GK_Report_ID')
                except:
                    general_tables = None
                    
                ozetle(financial_tables,general_tables,get_url,tip,sirketkodu,sirketadi,tarih,ilgili_sirketler,ozet_bilgi,aciklama, modal_info_title)
                    
        if len(haberler) == 0:
            print("haber bulunamadi")

        return codes      

    def getQuery(self):
        url: str = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"

        from_date = self.fromdate
        to_date = self.todate
        bildirimtipi = self.bildirim
        index = self.index
        market = self.market
        sector = self.sector
        hisse = self.codeOids()


        headers_post = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '394',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': '_ga=GA1.1.1320575248.1719242282; NSC_xxx.lbq.psh.us_tjuf=37cda3dd8e73a26012fe00f5ea2bbe77b978ae0b3749d4a15bf7afc53c8740c3665c4aa1; _ga_MBNFVK7SX4=GS1.1.1719242281.1.1.1719242892.60.0.0; KAP=AAU7KI55Zjv3oCoAAAAAADsUL9ZOBg_0wi2-O8TBNPmu2pvA4Su5CZ-1pHShUHLuOw==h5R5Zg==Elzk9g3efw-jSKp-q88wsR_TjP4=; KAP_.kap.org.tr_%2F_wlf=AAAAAAX071DV2OS6TD-RdOb3jaRgKtJfRjmNCdam_wSxqim7vCpgVmgdBF5VrmWuSRUEVxGAottDYKyaO22S2jx2jPCX7Ct06D_0wMsQV6PPLatCEg==&',
            'Host': 'www.kap.org.tr',
            'Origin': 'https://www.kap.org.tr',
            'Referer': 'https://www.kap.org.tr/tr/bildirim-sorgu',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

        data = {
            "fromDate": from_date,
            "toDate": to_date,
            "year":"",
            "prd":"",
            "term":"",
            "ruleType":"",
            "bdkReview":"",
            "disclosureClass": bildirimtipi,
            "index": index,
            "market": market,
            "isLate":"",
            "subjectList":[],
            "mkkMemberOidList":[hisse],
            "inactiveMkkMemberOidList":[],
            "bdkMemberOidList":[],
            "mainSector":"",
            "sector": sector,
            "subSector":"",
            "memberType":"IGS",
            "fromSrc":"N",
            "srcCategory":"",
            "discIndex":[]
        }

        cookies_post = {
            'KAP' : 'AAU7KI55Zjv3oCoAAAAAADsUL9ZOBg_0wi2-O8TBNPmu2pvA4Su5CZ-1pHShUHLuOw==h5R5Zg==Elzk9g3efw-jSKp-q88wsR_TjP4=',
            'KAP_.kap.org.tr_%2F_wlf' : 'AAAAAAX071DV2OS6TD-RdOb3jaRgKtJfRjmNCdam_wSxqim7vCpgVmgdBF5VrmWuSRUEVxGAottDYKyaO22S2jx2jPCX7Ct06D_0wMsQV6PPLatCEg==&',
            'NSC_xxx.lbq.psh.us_tjuf' : '37cda3dd8e73a26012fe00f5ea2bbe77b978ae0b3749d4a15bf7afc53c8740c3665c4aa1',
            '_ga' : 'GA1.1.1320575248.1719242282',
            '_ga_MBNFVK7SX4' : 'GS1.1.1719242281.1.1.1719242892.60.0.0'
        }

        json_data = json.dumps(data)
        post_res = requests.post(url, headers=headers_post, data=json_data, cookies=cookies_post)

        tex = post_res.text
        haberler: list = json.loads(tex) # response'dan donen listedir, icinde dictler var her dict bir haberi temsil eder

        codes = [int(haber["disclosureIndex"]) for haber in haberler]
        return codes


# sorgu = Sorgu("EREGL","2024-01-01","2024-07-22")
# sorgu.downloadQuery()

# ---------------------------------------------------------------------------

# REHBER

# Sorgu(sirketkodu,hangitarihten(yil-ay-gun),hangitarihe(yil-ay-gun), bildirimturu, indeks, sektor, pazar)
# Sorgu(sirketkodu, hangitarihten, hangitarihe) YETERLI

# getCompanyNames() : sirket isimlerini liste halinde dondurur
# getCompanyOids() : query icin gerekli sirket numaralarini dondurur
# getStockCodes() : sirketlerin kodlarini dondurur
# codeOids() : kodu verilmis sirketin query numarasini dondurur

# EN COK KULLANILACAKLAR

# downloadQuery() : verilen bilgilere gore bildirim, ek, json dosyasini indirir ve klasor isimlerini dondurur
# getQuery() : verilen bilgilerle uyumlu klasor isimlerini dondurur