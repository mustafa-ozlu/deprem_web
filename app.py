import json
from flask import Flask, render_template

app = Flask(__name__)

def get_deprem_data():
    with open("veri.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    veriler = get_deprem_data()
    return render_template("index.html", veriler=veriler)

if __name__ == "__main__":
    app.run(debug=True)
