from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("Loading sentiment model...")
analyzer = SentimentIntensityAnalyzer()
print("Sentiment model ready")

def score_headline(headline):
    scores = analyzer.polarity_scores(headline)
    return round(scores["compound"], 4)

def score_headlines_batch(headlines):
    for item in headlines:
        item["sentiment_score"] = score_headline(item["headline"])
        print(f"Scored: {item['headline'][:50]}... → {item['sentiment_score']}")
    return headlines