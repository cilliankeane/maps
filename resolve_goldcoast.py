#!/usr/bin/env python3
"""Resolve Gold Coast recs -> coords + googleMapsUri via Places API (Text Search).
Saves goldcoast-places.json INCREMENTALLY after every place (nothing lost on kill)."""
import os, json, time, urllib.request

KEY = os.environ["GOOGLE_PLACES_API_KEY"]
FIELD = "places(id,displayName,formattedAddress,googleMapsUri,location,rating)"
OUT = "goldcoast-places.json"

def text_search(q, rect):
    url = "https://places.googleapis.com/v1/places:searchText"
    body = {"textQuery": q, "maxResultCount": 3}
    if rect:
        body["locationBias"] = {"rectangle": {
            "low": {"latitude": rect[0], "longitude": rect[1]},
            "high": {"latitude": rect[2], "longitude": rect[3]}}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"X-Goog-Api-Key": KEY, "X-Goog-FieldMask": FIELD, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=20)).get("places", [])

# name -> (query, category, area)  category drives the pin colour
PLACES = [
  ("The Star Casino",              "The Star Gold Coast Broadbeach",            "Attraction", "Broadbeach"),
  ("Hideaway Kitchen and Bar",     "Hideaway Kitchen and Bar Broadbeach",       "Food",       "Broadbeach"),
  ("Mamasan",                      "Mamasan Broadbeach Gold Coast",             "Food",       "Broadbeach"),
  ("Kurrawa Surf Club",            "Kurrawa Surf Club Broadbeach",              "Food",       "Broadbeach"),
  ("Pacific Fair Shopping Centre", "Pacific Fair Shopping Centre Broadbeach",   "Shopping",   "Broadbeach"),
  ("Glenelg Public House",         "Glenelg Public House Broadbeach",           "Food",       "Broadbeach"),
  ("Etsu Izakaya",                 "Etsu Izakaya Mermaid Beach",                "Food",       "Broadbeach"),
  ("Koi",                          "Koi Broadbeach Gold Coast",                 "Food",       "Broadbeach"),
  ("Loose Moose Tap House",        "Loose Moose Tap House Broadbeach",          "Bar",        "Broadbeach"),
  ("Blowfish",                     "Blowfish Broadbeach Gold Coast",            "Food",       "Broadbeach"),
  ("Bam Bam Bakehouse",            "Bam Bam Bakehouse Mermaid Beach",           "Cafe",       "Broadbeach"),

  ("Sueno Rooftop",                "Sueno Rooftop Nobby Beach",                 "Bar",        "Nobby Beach"),
  ("Norte",                        "Norte Nobby Beach Gold Coast",              "Bar",        "Nobby Beach"),
  ("Lars Bar and Grill",           "Lars Bar and Grill Nobby Beach",            "Food",       "Nobby Beach"),
  ("Franc Jrs",                    "Franc Jrs Nobby Beach",                     "Food",       "Nobby Beach"),
  ("Ally Chow",                    "Ally Chow Nobby Beach",                     "Food",       "Nobby Beach"),
  ("Bine Bar and Dining",          "Bine Bar and Dining Nobby Beach",           "Food",       "Nobby Beach"),
  ("Nobby's Surf Club",            "Nobby Beach Surf Club Gold Coast",          "Food",       "Nobby Beach"),
  ("The Miami",                    "The Miami Nobby Beach Gold Coast",          "Bar",        "Nobby Beach"),

  ("Rick Shores",                  "Rick Shores Burleigh Heads",                "Food",       "Burleigh Heads"),
  ("Burleigh Pavilion",            "Burleigh Pavilion Burleigh Heads",          "Food",       "Burleigh Heads"),
  ("Mr Hizolas",                   "Mr Hizolas Burleigh Heads",                 "Food",       "Burleigh Heads"),
  ("Justin Lane",                  "Justin Lane Burleigh Heads",                "Food",       "Burleigh Heads"),
  ("The Local",                    "The Local Burleigh Heads",                  "Bar",        "Burleigh Heads"),
  ("Malibu Racquet Club",          "Malibu Racquet Club Burleigh Heads",        "Bar",        "Burleigh Heads"),
  ("Rosellas",                     "Rosellas Burleigh Heads Gold Coast",        "Food",       "Burleigh Heads"),
  ("Paloma Wine Bar",              "Paloma Wine Bar Burleigh Heads",            "Bar",        "Burleigh Heads"),
  ("Jimmy Wahs",                   "Jimmy Wahs Burleigh Heads",                 "Food",       "Burleigh Heads"),
  ("Light Years",                  "Light Years Burleigh Heads",                "Food",       "Burleigh Heads"),
  ("Apres Surf",                   "Apres Surf Burleigh Heads",                 "Food",       "Burleigh Heads"),

  ("Palm Springs",                 "Palm Springs Burleigh Heads cafe",          "Cafe",       "North Burleigh"),
  ("Paddock Bakery",               "Paddock Bakery Burleigh Heads",             "Cafe",       "North Burleigh"),
  ("Hard Fizz Brewery",            "Hard Fizz Brewery Burleigh Heads",          "Bar",        "North Burleigh"),
  ("Black Hops Brewery",           "Black Hops Brewery Burleigh Heads",         "Bar",        "North Burleigh"),
  ("Precinct Brewery",             "Precinct Brewery Burleigh Heads",           "Bar",        "North Burleigh"),
  ("Padre Brewery",                "Padre Brewery Burleigh Heads",              "Bar",        "North Burleigh"),
  ("Miami Marketta",               "Miami Marketta Gold Coast",                 "Attraction", "North Burleigh"),

  ("Kirra Beach Hotel",            "Kirra Beach Hotel Coolangatta",             "Food",       "Southern GC"),
  ("Siblings Kirra",               "Siblings Kirra Coolangatta",                "Food",       "Southern GC"),
  ("Salt Mill",                    "Salt Mill Currumbin Beach",                 "Cafe",       "Southern GC"),
  ("Tommy's Italian",              "Tommy's Italian Currumbin",                 "Food",       "Southern GC"),
  ("Custard Canteen",              "Custard Canteen Tallebudgera",              "Cafe",       "Southern GC"),
  ("Tallebudgera Surf Club",       "Tallebudgera Surf Club Gold Coast",         "Food",       "Southern GC"),

  ("Q1 Viewpoint Tower",           "SkyPoint Observation Deck Q1 Surfers Paradise", "Attraction", "Surfers Paradise"),
  ("Main Beach",                   "Main Beach Gold Coast",                     "Attraction", "Main Beach"),
  ("Sea World",                    "Sea World Gold Coast",                      "Attraction", "Main Beach"),
  ("Mount Tamborine",              "Mount Tamborine Queensland",                "Attraction", "Hinterland"),
  ("Topgolf",                      "Topgolf Gold Coast",                        "Attraction", "Gold Coast"),
]

RECT = (-28.30, 153.20, -27.85, 153.60)  # Gold Coast region bias

def load():
    try: return json.load(open(OUT))
    except FileNotFoundError: return {}

def save(out):
    json.dump(out, open(OUT, "w"), indent=2)

def main():
    out = load()
    for name, q, cat, area in PLACES:
        if name in out and out[name].get("lat") is not None:
            continue
        try:
            res = text_search(q, RECT)
        except Exception as e:
            print(f"ERR {name}: {e}", flush=True)
            time.sleep(1.5)
            continue
        if not res:
            print(f"MISS {name} ({q})", flush=True)
            continue
        p = res[0]
        loc = p.get("location", {})
        out[name] = {
            "display": p.get("displayName", {}).get("text", name),
            "addr": p.get("formattedAddress", ""),
            "cat": cat,
            "area": area,
            "rating": p.get("rating"),
            "mapsUri": p.get("googleMapsUri", ""),
            "placeId": p.get("id", ""),
            "lat": loc.get("latitude"),
            "lon": loc.get("longitude"),
        }
        print(f"OK   {name} -> {out[name]['display']} | {out[name]['addr']}", flush=True)
        save(out)
        time.sleep(0.3)
    save(out)
    print(f"DONE: {len(out)}/{len(PLACES)} resolved", flush=True)

main()
