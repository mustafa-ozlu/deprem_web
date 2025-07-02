import json
from flask import Flask, render_template, jsonify, send_from_directory, current_app, request, send_file
import os

app = Flask(__name__)

def get_deprem_data():
    with open("veri.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    veriler = get_deprem_data()
    return render_template("index.html", veriler=veriler)

@app.route("/deprem")
def deprem_verileri():
    with open("veri.json", "r", encoding="utf-8") as f:
        veriler = json.load(f)
    return jsonify(veriler)

# Dosya listesini döndüren route
@app.route("/download")
def download_page():
    files = os.listdir("static")  # static klasöründeki dosyaları listele
    return render_template("download.html", files=files)

# Kullanıcı seçtiği dosyayı indiriyor
@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join("static", filename)
    
    # Dosyanın olup olmadığını kontrol et
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Dosya bulunamadı.", 404

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0",port=5000)
