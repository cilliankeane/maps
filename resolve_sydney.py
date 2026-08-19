#!/usr/bin/env python3
"""Resolve Sydney food recs -> coords + googleMapsUri via Places API (Text Search).
Saves sydney-places.json INCREMENTALLY after every place (nothing lost on kill)."""
import os, json, re, time, urllib.request, urllib.parse

KEY = os.environ["GOOGLE_PLACES_API_KEY"]
FIELD = "places(id,displayName,formattedAddress,googleMapsUri,location)"
OUT = "sydney-places.json"

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

AREAS = {
  "Dinner":   (-33.8696,151.2070,["sydney cbd","SYDNEY"]), "Lunch/cafe":(-33.8681,151.2050,["sydney cbd","SYDNEY"]),
  "Drinks":   (-33.8696,151.2070,["sydney cbd bar","SYDNEY"]), "Paddington":(-33.8840,151.2270,["paddington sydney"]),
  "Maroubra": (-33.9503,151.2558,["maroubra"]), "Coogee":(-33.9203,151.2555,["coogee"]),
  "Clovelly": (-33.9128,151.2580,["clovelly"]), "Bondi":(-33.8914,151.2767,["bondi"]),
  "Bondi Junction":(-33.8925,151.2490,["bondi junction"]), "Double Bay":(-33.8785,151.2420,["double bay"]),
  "Randwick": (-33.9130,151.2420,["randwick"]), "Surry Hills":(-33.8840,151.2130,["surry hills"]),
  "Bronte":   (-33.9039,151.2630,["bronte"]), "Manly":(-33.7965,151.2863,["manly"]),
  "Mascot":   (-33.9337,151.2077,["mascot"]), "Marrickville":(-33.9100,151.1550,["marrickville"]),
  "La Perouse":(-33.9880,151.2350,["la perouse"]), "Redfern":(-33.8880,151.2060,["redfern"]),
  "North Strathfield":(-33.8560,151.0880,["north strathfield"]), "Ramsgate":(-33.9830,151.1370,["ramsgate"]),
  "Newtown":  (-33.8960,151.1800,["newtown"]), "Rosebery":(-33.9190,151.2050,["rosebery"]),
  "Alexandria":(-33.9030,151.1970,["alexandria"]), "Caringbah":(-34.0460,151.1210,["caringbah"]),
  "Wollongong":(-34.4278,150.8931,["wollongong"]), "Brighton":(-33.9590,151.2570,["brighton le sands"]),
  "Botany":   (-33.9500,151.2010,["botany"]), "Inner West":(-33.8870,151.1700,["inner west sydney"]),
}

OVERRIDES = {
  "Naples (APPIZZA)": "APPIZZA Darlinghurst",
  "The Gidley": "The Gidley restaurant Sydney",
  "Grace of India": "Grace of India Kirribilli",
  "Elliott's": "Elliott's Balmain",
  "The Fenwick": "The Fenwick Balmain",
  "The Fenwick Cafe": "The Fenwick Cafe Balmain East",
  "Bourke Street Bakery Banksmeadow": "Bourke Street Bakery Banksmeadow",
  "Bangkok Bites Macelleria": "Bangkok Bites Newtown",
  "Bills Coffee": "Bills Bondi",
  "Vacanza Pizza": "Vacanza Bronte",
  "Tonton Bread Newtown": "Tonton Bread Newtown",
  "Uncle George's": "Uncle George's Wollongong",
  "Bay Vista": "Bay Vista Brighton Le Sands",
  "Queens Pastry House": "Queens Pastry House Ramsgate",
}

def load():
    try: return json.load(open(OUT))
    except FileNotFoundError: return {}

def save(out):
    json.dump(out, open(OUT,"w"), indent=2)

# category (cat) for colour-coding — mapped from area name
CAT = {
  "Dinner": "Dinner", "Lunch/cafe": "Lunch/Cafe", "Drinks": "Drinks",
  "Paddington": "Dinner", "Maroubra": "Cafe", "Coogee": "Cafe",
  "Clovelly": "Cafe", "Bondi": "Cafe", "Bondi Junction": "Cafe",
  "Double Bay": "Bakery", "Randwick": "Cafe", "Surry Hills": "Cafe",
  "Bronte": "Cafe", "Manly": "Cafe", "Mascot": "Bakery",
  "Marrickville": "Cafe", "La Perouse": "Dinner", "Redfern": "Cafe",
  "North Strathfield": "Cafe", "Ramsgate": "Bakery", "Newtown": "Dinner",
  "Rosebery": "Cafe", "Alexandria": "Cafe", "Caringbah": "Bakery",
  "Wollongong": "Dinner", "Brighton": "Dinner", "Botany": "Bakery",
  "Inner West": "Bakery",
}

# a saved but generic link means it needs a proper refetch on the next run
GENERIC = ("https://maps.google.com/", "")  # exact per-place link required

def parse():
    areas, current, order = {}, None, []
    for ln in open("sydney-recs.txt").read().splitlines():
        ln = ln.strip()
        if not ln: continue
        m = re.match(r"^#?\s*\[(.+)\]$", ln)
        if m:
            current = m.group(1).strip()
            if current not in areas: areas[current]=[]; order.append(current)
            continue
        if ln.startswith(("#","Format","Categories")): continue
        if current: areas[current].append(ln)
    return areas, order

def best(places, root):
    if not places: return None
    low = root.lower()
    for p in places:
        if (p.get("displayName") or {}).get("text","").lower()==low: return p
    for p in places:
        nm=(p.get("displayName") or {}).get("text","").lower()
        if low.split()[0] in nm or nm.split()[0] in low: return p
    return places[0]

def main():
    out = load()
    areas, order = parse()
    for area in order:
        c = AREAS.get(area)
        if not c: continue
        rect=(c[0]-0.12,c[1]-0.12,c[0]+0.12,c[1]+0.12)
        for entry in areas.get(area,[]):
            key = entry.split("✅")[0].split("*")[0].strip()
            # skip only if we already have a REAL link + cat + coords
            cur = out.get(key) or {}
            uri = (cur.get("mapsUri") or "").split("?")[0]
            if cur.get("cat") and cur.get("lat") is not None and uri and uri not in GENERIC:
                continue
            q = OVERRIDES.get(key, f"{key} {c[2]}")
            try:
                p = best(text_search(q, rect), key)
                if p:
                    out[key]={
                      "name":key,
                      "display":(p.get("displayName") or {}).get("text"),
                      "addr":p.get("formattedAddress"),
                      "mapsUri":p.get("googleMapsUri") or "",
                      "placeId":p.get("id"),
                      "lat":(p.get("location") or {}).get("latitude"),
                      "lon":(p.get("location") or {}).get("longitude"),
                      "area":area,
                      "cat":CAT.get(area, area),
                    }
                    print(f"OK  [{area}] {key} -> {out[key]['display']} | {out[key]['lat']:.4f},{out[key]['lon']:.4f}", flush=True)
                else:
                    print(f"MISS [{area}] {key}", flush=True)
            except Exception as e:
                print(f"ERR  [{area}] {key}: {e}", flush=True)
            save(out)  # incremental — nothing lost on kill
            time.sleep(0.25)
    print(f"\nDONE: {len(out)} places saved to {OUT}", flush=True)

main()
