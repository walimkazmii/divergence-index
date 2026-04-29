import requests

def get_polymarket(keyword=""):
    try:
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "limit": 50,
                "active": "true",
                "closed": "false"
            }
        )

        if response.status_code != 200:
            print(f"Polymarket error: {response.status_code}")
            return []

        markets = response.json()

        if keyword:
            markets = [
                m for m in markets
                if keyword.lower() in m.get("question", "").lower()
            ]

        results = []
        for m in markets[:10]:
            results.append({
                "source": "Polymarket",
                "title": m.get("question", ""),
                "yes_price": m.get("outcomePrices", ["0"])[0],
                "no_price": m.get("outcomePrices", ["0", "0"])[1]
                    if len(m.get("outcomePrices", [])) > 1 else "0",
                "url": f"https://polymarket.com/event/{m.get('slug', '')}"
            })

        return results

    except Exception as e:
        print(f"Polymarket error: {e}")
        return []


def get_metaculus(keyword=""):
    try:
        params = {
            "limit": 10,
            "status": "open",
            "order_by": "-activity"
        }

        if keyword:
            params["search"] = keyword

        response = requests.get(
            "https://www.metaculus.com/api2/questions/",
            params=params,
            headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            print(f"Metaculus error: {response.status_code}")
            return []

        questions = response.json().get("results", [])

        results = []
        for q in questions:
            community = q.get("community_prediction", {})
            prediction = community.get("full", {}).get("q2", None)

            results.append({
                "source": "Metaculus",
                "title": q.get("title", ""),
                "yes_price": round(prediction * 100) if prediction else "?",
                "no_price": round((1 - prediction) * 100) if prediction else "?",
                "url": f"https://metaculus.com{q.get('page_url', '')}"
            })

        return results

    except Exception as e:
        print(f"Metaculus error: {e}")
        return []


def get_markets(keyword=""):
    poly = get_polymarket(keyword)
    meta = get_metaculus(keyword)
    return poly + meta