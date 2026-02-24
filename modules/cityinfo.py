import requests

def get_city_info(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results")
    if not results:
        return None

    item = results[0]
    lat = item["latitude"]
    hemisphere = "Northern" if lat >= 0 else "Southern"

    return {
        "city": item.get("name", city),
        "country": item.get("country", "Unknown"),
        "latitude": lat,
        "longitude": item["longitude"],
        "hemisphere": hemisphere,
        "timezone": item.get("timezone", "Unknown"),
    }
