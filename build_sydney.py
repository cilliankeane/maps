#!/usr/bin/env python3
"""Build sydney.html Leaflet map from sydney-places.json."""
import json, html

PLACES = "sydney-places.json"
OUT = "sydney.html"

# colour + legend label per category
CAT_STYLE = {
    "Dinner":    ("#8e24aa", "Dinner"),
    "Lunch/Cafe":("#e67e22", "Lunch / Cafe"),
    "Drinks":    ("#00838f", "Drinks"),
    "Cafe":      ("#e67e22", "Lunch / Cafe"),
    "Bakery":    ("#2e7d32", "Bakery / Patisserie"),
}
# fallback group for any uncategorised area
DEFAULT_CAT = ("#e67e22", "Lunch / Cafe")

def esc(s):
    return html.escape(str(s), quote=True)

def build():
    data = json.load(open(PLACES))
    pins = []
    for key, p in data.items():
        if p.get("lat") is None or p.get("lon") is None:
            continue
        cat = p.get("cat") or p.get("area") or "Cafe"
        color, label = CAT_STYLE.get(cat, DEFAULT_CAT)
        pins.append({
            "name": esc(p.get("display") or key),
            "addr": esc(p.get("addr") or ""),
            "cat":  esc(cat),
            "label": label,
            "color": color,
            "lat":  p["lat"],
            "lon":  p["lon"],
            "gm":   p.get("mapsUri") or "https://maps.google.com/",
        })

    js_pins = ",\n      ".join(
        '{name:%s,cat:%s,label:%s,color:%s,addr:%s,lat:%s,lon:%s,gm:%s}'
        % (json.dumps(p["name"]), json.dumps(p["cat"]), json.dumps(p["label"]),
           json.dumps(p["color"]), json.dumps(p["addr"]), p["lat"], p["lon"],
           json.dumps(p["gm"]))
        for p in pins
    )

    # build legend from pinned labels
    legend = []
    shown = set()
    for p in pins:
        if p["label"] not in shown:
            shown.add(p["label"])
            color = p["color"]
            legend.append(f'<span><span class="dot" style="background:{color}"></span> {p["label"]}</span>')
    legend_html = "</span><br>\n    <span>".join(legend)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sydney Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  html,body{{margin:0;padding:0;height:100%;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}}
  #map{{position:absolute;inset:0}}
  .pin-title{{font-weight:700}}
  .pin-cat{{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px}}
  .pin-desc{{color:#555;font-size:12px;margin-top:3px}}
  .back{{position:absolute;z-index:1000;top:10px;left:10px;background:#fff;border-radius:20px;padding:8px 14px;
    font-size:13px;font-weight:600;box-shadow:0 2px 10px rgba(0,0,0,.25);text-decoration:none;color:#333}}
  .legend{{position:absolute;z-index:999;bottom:18px;left:10px;background:rgba(255,255,255,.95);border-radius:8px;
    padding:10px 12px;box-shadow:0 2px 10px rgba(0,0,0,.25);font-size:12px;max-width:260px;line-height:1.75}}
  .legend b{{display:block;margin-bottom:4px;font-size:12.5px}}
  .legend .dot{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px;vertical-align:middle;
    border:1px solid rgba(0,0,0,.15)}}
</style>
</head>
<body>
  <div id="map"></div>
  <a class="back" href="index.html">← All cities</a>
  <div class="legend">
    <b>🍴 Sydney ({len(pins)} spots)</b>
    {legend_html}
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([-33.89, 151.23], 12);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const places = [
      {js_pins}
    ];
    places.forEach((p,i)=>{{
      const n=i+1;
      const html=`<div style="width:24px;height:24px;border-radius:50%;background:${{p.color}};border:2.5px solid #fff;
        box-shadow:0 2px 6px rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;
        font:700 11px/1 Arial;color:#fff">${{n}}</div>`;
      L.marker([p.lat,p.lon], {{icon: L.divIcon({{className:'',html,iconSize:[24,24],iconAnchor:[12,12]}})}}).addTo(map)
        .bindPopup(`<div class="pin-cat">${{p.cat}}</div><div class="pin-title">${{p.name}}</div>
                    <div class="pin-desc">${{p.addr}}</div>
                    <a href="${{p.gm}}" target="_blank" rel="noopener" style="display:inline-block;margin-top:8px;padding:6px 12px;background:#4285F4;color:#fff;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600">📍 Open in Google Maps</a>`);
    }});
  </script>
</body>
</html>
"""
    open(OUT, "w").write(html_doc)
    print(f"Wrote {OUT} with {len(pins)} pins", flush=True)

build()
