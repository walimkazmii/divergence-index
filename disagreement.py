import pandas as pd

def compute_ndi(scored_headlines):
    if not scored_headlines:
        return None
    
    df = pd.DataFrame(scored_headlines)
    outlet_scores = df.groupby("outlet")["sentiment_score"].mean()
    
    if len(outlet_scores) < 2:
        return None
    
    ndi_score = float(outlet_scores.std())
    mean_sentiment = float(outlet_scores.mean())
    
    if ndi_score < 0.1:
        level = "low"
    elif ndi_score < 0.25:
        level = "moderate"
    else:
        level = "high"
    
    return {
        "ndi_score": round(ndi_score, 4),
        "mean_sentiment": round(mean_sentiment, 4),
        "outlet_count": len(outlet_scores),
        "disagreement_level": level,
        "outlet_breakdown": outlet_scores.to_dict()
    }