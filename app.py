from flask import Flask, render_template
from deprem import get_deprem_data

app = Flask(__name__)

@app.route("/")
def index():
    veriler = get_deprem_data()
    return render_template("index.html", veriler=veriler)

if __name__ == "__main__":
    app.run(debug=True)
