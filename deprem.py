import requests
import json
from datetime import datetime, timedelta
import time
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def sms_gonder(mesaj):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mesaj}
    response = requests.get(url, params=params)
    print(response.json(), flush=True)

def onceki_veri_yukle():
    try:
        if os.path.exists("son_sms.json"):
            with open("son_sms.json", "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
                # Sadece ID'leri döndür (eski formatı desteklemek için)
                return [k.get("ID", k.get("kimlik", "").split(" | ")[0] if isinstance(k.get("kimlik"), str) else "") for k in kayitlar]
        return []
    except Exception as e:
        print(f"Önceki veri yüklenirken hata: {e}")
        return []

def veri_kaydet(veri):
    try:
        # Mevcut kayıtları yükle
        if os.path.exists("son_sms.json"):
            with open("son_sms.json", "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
        else:
            kayitlar = []
        
        # Yeni kaydı oluştur
        yeni_kayit = {
            "ID": veri['ID'],
            "Tarih": veri['Tarih'],
            "Yer": veri['Yer'],
            "ML": veri['ML'],
            "zaman": datetime.now().isoformat()
        }
        
        # Aynı ID'ye sahip eski kaydı sil
        kayitlar = [k for k in kayitlar if k.get("ID") != veri['ID']]
        
        # Yeni kaydı ekle
        kayitlar.append(yeni_kayit)
        
        # 5 günden eski kayıtları temizle
        kayitlar = [k for k in kayitlar 
                   if (datetime.now() - datetime.fromisoformat(k["zaman"])) < timedelta(days=5)]
        
        # Kaydet
        with open("son_sms.json", "w", encoding="utf-8") as f:
            json.dump(kayitlar, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Veri kaydedilirken hata: {e}")

def get_deprem_data():
    url = "https://deprem.afad.gov.tr/last-earthquakes.html"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='content-table')
        if not table:
            raise ValueError("Tablo bulunamadı")
            
        rows = table.find_all('tr')[1:]
        parsed_data = []
        
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) < 7:
                    continue
                    
                ml = float(cols[5].text.strip())
                enlem = float(cols[1].text.strip())
                boylam = float(cols[2].text.strip())
                detay_button = row.find('a', class_='routeButton')
                deprem_id = detay_button['href'].split('/')[-1] if detay_button else None
                
                parsed_data.append({
                    "Tarih": cols[0].text.strip(),
                    "Enlem": enlem,
                    "Boylam": boylam,
                    "Derinlik": float(cols[3].text.strip()),
                    "ML": ml,
                    "Yer": cols[6].text.strip(),
                    "ID": deprem_id,
                    "Harita": f"https://www.openstreetmap.org/?mlat={enlem}&mlon={boylam}&zoom=9"
                })
            except Exception as e:
                print(f"Satır işlenirken hata: {e}")
                continue
                
        return parsed_data
    except Exception as e:
        print(f"Deprem verisi alınırken hata: {e}")
        return []

if __name__ == "__main__":
    while True:
        try:
            veriler = get_deprem_data()
            onceki_ids = onceki_veri_yukle()
            
            # Verileri kaydet
            with open("veri.json", "w", encoding="utf-8") as f:
                json.dump(veriler, f, ensure_ascii=False, indent=2)
                
            print(f"Veri güncellendi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            
            # Yeni depremleri kontrol et
            for veri in veriler:
                try:
                    if float(veri["ML"]) >= 3.5 and veri["ID"] not in onceki_ids:
                        mesaj = (f"⚠️ {veri['Yer']} bölgesinde {veri['ML']} büyüklüğünde deprem meydana geldi!\n"
                                f"Tarih: {veri['Tarih']}\n"
                                f"Derinlik: {veri['Derinlik']} km\n"
                                f"Harita: {veri['Harita']}\n")
                        sms_gonder(mesaj)
                        veri_kaydet(veri)
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Deprem işlenirken hata: {e}")
                    continue
                    
            time.sleep(30)
        except KeyboardInterrupt:
            print("Program sonlandırılıyor...")
            break
        except Exception as e:
            print(f"Ana döngüde hata: {e}")
            time.sleep(60)
