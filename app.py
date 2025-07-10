# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, jsonify, send_file
import os
import requests
from datetime import datetime
import time
from bs4 import BeautifulSoup
from threading import Thread
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
                return [k.get("ID") for k in kayitlar]
        return []
    except Exception as e:
        print(f"Önceki veri yüklenirken hata: {e}")
        return []

def veri_kaydet(veri):
    try:
        kayitlar = []
        if os.path.exists("son_sms.json"):
            with open("son_sms.json", "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
        
        kayitlar = [k for k in kayitlar if k.get("ID") != veri['ID']]
        kayitlar.append({
            "ID": veri['ID'],
            "Tarih": veri['Tarih'],
            "Yer": veri['Yer'],
            "ML": veri['ML'],
            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open("son_sms.json", "w", encoding="utf-8") as f:
            json.dump(kayitlar, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Veri kaydedilirken hata: {e}")

def get_deprem_data():
    url = "https://deprem.afad.gov.tr/last-earthquakes.html"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'  # Türkçe karakter desteği için bunu ekle
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='content-table')
        rows = table.find_all('tr')[1:]
        
        parsed_data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 7:
                continue
            ml=float(cols[5].text.strip())    
            detay_button = row.find('a', class_='routeButton')
            deprem_id = detay_button['href'].split('/')[-1] if detay_button else None
            if ml >=2:
                parsed_data.append({
                    "Tarih": cols[0].text.strip(),
                    "Enlem": float(cols[1].text.strip()),
                    "Boylam": float(cols[2].text.strip()),
                    "Derinlik": float(cols[3].text.strip()),
                    "ML": ml,
                    "Yer": cols[6].text.strip(),
                    "ID": deprem_id,
                    "Harita": f"https://www.openstreetmap.org/?mlat={cols[1].text.strip()}&mlon={cols[2].text.strip()}&zoom=9"
                })
        return parsed_data
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []

# --- Arka planda veri güncelleyen fonksiyon ---
def arkaplan_guncelle():
    while True:
        try:
            veriler = get_deprem_data()
            onceki_ids = onceki_veri_yukle()
            
            # veri.json'a kaydet
            with open("veri.json", "w", encoding="utf-8") as f:
                json.dump(veriler, f, ensure_ascii=False, indent=2)
            
            # Yeni deprem bildirimi
            for veri in veriler:
                if veri["ML"] >= 3.5 and veri["ID"] not in onceki_ids:
                    mesaj = f"⚠️ D E P R E M !\nYeri: {veri['Yer']}\nŞiddeti: {veri['ML']} \nZamanı: {veri['Tarih']}\nHarita:{veri['Harita']}\n"
                    sms_gonder(mesaj)
                    veri_kaydet(veri)
            print("Son Veri: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),flush=True)
            time.sleep(60)  # 1 dakikada bir güncelle
        except Exception as e:
            print(f"Güncelleme hatası: {e}")
            time.sleep(30)
app = Flask(__name__)

def start_background_thread_once():
    if not hasattr(app, "background_thread_started"):
        app.background_thread_started = True
        Thread(target=arkaplan_guncelle, daemon=True).start()
        print("Arkaplan güncelleme başlatıldı", flush=True)

start_background_thread_once()

# --- Flask Route'ları ---
@app.route("/")
def index():
    with open("veri.json", "r", encoding="utf-8") as f:
        veriler = json.load(f)
    return render_template("index.html", veriler=veriler)

@app.route("/deprem")
def deprem_verileri():
    with open("veri.json", "r", encoding="utf-8") as f:
        veriler = json.load(f)
    return jsonify(veriler)

@app.route("/download")
def download_page():
    files = os.listdir("static/download")  # static klasöründeki dosyaları listele
    return render_template("download.html", files=files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(f"static/download/{filename}", as_attachment=True)

# --- Uygulama Başlatma ---
if __name__ == "__main__":
    # Flask'ı çalıştır
    app.run(debug=False, host="0.0.0.0", port=5000)
