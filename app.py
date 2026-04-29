import os

from predictor import predict
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

from news_collector import fetch_headlines, COMPANIES
from sentiment import score_headlines_batch
from disagreement import compute_ndi
from markets import get_markets
from database import init_db, save_headlines, save_ndi, get_ndi_history

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)
init_db()

def run_pipeline():
    print(f"\n--- Running pipeline at {datetime.now()} ---")
    today = datetime.now().strftime('%Y-%m-%d')

    for company in COMPANIES:
        print(f"\nProcessing {company}...")
        headlines = fetch_headlines(company)

        if not headlines:
            print(f"No headlines found for {company}")
            continue

        scored = score_headlines_batch(headlines)
        save_headlines(scored)

        ndi = compute_ndi(scored)
        if ndi:
            save_ndi(company, today, ndi)
            print(f"NDI for {company}: {ndi['ndi_score']} ({ndi['disagreement_level']})")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/companies")
def get_companies():
    return jsonify({"companies": COMPANIES})

@app.route("/api/ndi/<company>")
def get_ndi(company):
    history = get_ndi_history(company)
    return jsonify({
        "company": company,
        "history": [
            {
                "date": row[0],
                "ndi_score": row[1],
                "mean_sentiment": row[2],
                "disagreement_level": row[3]
            } for row in history
        ]
    })

@app.route("/api/markets/<keyword>")
def search_markets(keyword):
    return jsonify({"markets": get_markets(keyword)})

@app.route("/api/run")
def trigger_run():
    run_pipeline()
    return jsonify({"status": "done"})

@app.route("/api/predict/<company>")
def get_prediction(company):
    result = predict(company)
    return jsonify(result)

if __name__ == "__main__":
    run_pipeline()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)