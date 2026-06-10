"""
Fix pagine prenota mancanti per i ristoranti già contattati.
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys, sqlite3, time
from genera_preview_fullbooking import get_place_data, estrai_dati_sito, genera_slug, genera_html_prenota, OUTPUT_DIR

conn = sqlite3.connect('leads.db')
conn.row_factory = sqlite3.Row

leads = conn.execute("""
    SELECT id, nome, citta, indirizzo, telefono, email,
           sito_web, rating, num_recensioni, google_place_id, note
    FROM leads
    WHERE stato = 'FB:inviato'
    AND google_place_id IS NOT NULL AND google_place_id != ''
""").fetchall()
leads = [dict(r) for r in leads]
conn.close()

print(f"Generazione pagine prenota per {len(leads)} ristoranti...")
ok = 0
skip = 0

for i, lead in enumerate(leads, 1):
    slug = genera_slug(lead['nome'])
    prenota_file = f'{slug}-prenota.html'
    filepath = os.path.join(OUTPUT_DIR, prenota_file)

    if os.path.exists(filepath):
        skip += 1
        continue

    print(f"[{i:3d}/{len(leads)}] {lead['nome'][:45]:<45}", end=' ', flush=True)
    foto_urls, place_data = get_place_data(lead['google_place_id'])
    brand = estrai_dati_sito(lead['sito_web'] or '')
    html_prenota = genera_html_prenota(lead, foto_urls, place_data, brand, slug)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_prenota)
    print('OK')
    ok += 1
    time.sleep(0.3)

print(f"\nFatto: {ok} pagine prenota generate, {skip} gia esistenti")
