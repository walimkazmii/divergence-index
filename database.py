import sqlite3
from datetime import datetime

DB_PATH = "divergence.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            outlet TEXT,
            headline TEXT,
            published_at TEXT,
            sentiment_score REAL,
            date_collected TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ndi_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            date TEXT,
            ndi_score REAL,
            mean_sentiment REAL,
            outlet_count INTEGER,
            disagreement_level TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database ready")

def save_headlines(headlines):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for h in headlines:
        c.execute('''
            INSERT INTO headlines 
            (company, outlet, headline, published_at, 
             sentiment_score, date_collected)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            h["company"], h["outlet"], h["headline"],
            h["published_at"], h["sentiment_score"],
            datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()

def save_ndi(company, date, ndi):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO ndi_scores 
        (company, date, ndi_score, mean_sentiment, 
         outlet_count, disagreement_level)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        company, date, ndi["ndi_score"],
        ndi["mean_sentiment"], ndi["outlet_count"],
        ndi["disagreement_level"]
    ))
    conn.commit()
    conn.close()

def get_ndi_history(company, limit=30):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT date, ndi_score, mean_sentiment, disagreement_level
        FROM ndi_scores WHERE company = ?
        ORDER BY date DESC LIMIT ?
    ''', (company, limit))
    rows = c.fetchall()
    conn.close()
    return rows