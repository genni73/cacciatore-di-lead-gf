"""Test generazione per un singolo ristorante."""
import sqlite3, os
from genera_preview_fullbooking import (
    get_place_data, estrai_dati_sito,
    genera_html_landing, genera_html_prenota,
    genera_slug, OUTPUT_DIR
)

conn = sqlite3.connect("leads.db")
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT * FROM leads WHERE id = 2473").fetchone()
lead = {k: row[k] for k in row.keys()}
conn.close()

print(f"Test: {lead['nome']} ({lead['citta']})")
print(f"Sito: {lead['sito_web']}")

foto_urls, place_data = get_place_data(lead["google_place_id"])
print(f"Foto Google: {len(foto_urls)}")

brand = estrai_dati_sito(lead["sito_web"] or "")
print(f"Logo: {brand.get('logo_url') or '—'}")
print(f"Tagline: {(brand.get('tagline') or '—')[:70]}")

slug = genera_slug(lead["nome"])
print(f"Slug: {slug}")

html_l = genera_html_landing(lead, foto_urls, place_data, brand, slug)
html_p = genera_html_prenota(lead, foto_urls, place_data, brand, slug)

lp = os.path.join(OUTPUT_DIR, slug + ".html")
pp = os.path.join(OUTPUT_DIR, slug + "-prenota.html")

with open(lp, "w", encoding="utf-8") as f:
    f.write(html_l)
with open(pp, "w", encoding="utf-8") as f:
    f.write(html_p)

print(f"\nFATTO!")
print(f"Landing ({len(html_l)//1024}KB): {lp}")
print(f"Prenota ({len(html_p)//1024}KB): {pp}")

import subprocess
subprocess.Popen(["start", lp], shell=True)
print("\nAperto nel browser!")
