import requests

def get_deprem_data():
    url = "http://www.koeri.boun.edu.tr/scripts/lst6.asp"
    response = requests.get(url)
    response.encoding = "ISO-8859-9"

    data = response.text
    start_index = data.find("..................TÜRKİYE VE YAKIN ÇEVRESİNDEKİ SON DEPREMLER....................")
    if start_index != -1:
        data = data[start_index:]
        lines = data.split("\n")[6:]
    else:
        lines = []

    parsed_data = []
    for line in lines[:250]:
        parts = line.split()
        if len(parts) < 10:
            continue
        tarih, saat = parts[0], parts[1]
        enlem, boylam, derinlik = parts[2], parts[3], parts[4]
        md, ml, mw = parts[5], parts[6], parts[7]
        yer = " ".join(parts[8:-1])
        harita = f"https://www.openstreetmap.org/?mlat={enlem}&mlon={boylam}&zoom=9"
        parsed_data.append({
            "tarih": tarih, "saat": saat, "enlem": enlem, "boylam": boylam,
            "derinlik": derinlik, "ml": ml, "mw": mw, "yer": yer, "harita": harita
        })

    return parsed_data
