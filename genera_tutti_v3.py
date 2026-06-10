"""
Genera pagine v3 nero/oro per TUTTI i ristoranti non ancora processati.
Nessuna emoji nelle print per compatibilità Windows cp1252.
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sqlite3, time
from genera_preview_fullbooking import (
    get_place_data, estrai_dati_sito, genera_slug,
    genera_html_landing, genera_html_prenota, OUTPUT_DIR
)

conn = sqlite3.connect('leads.db')
conn.row_factory = sqlite3.Row

leads = conn.execute("""
    SELECT id, nome, citta, indirizzo, telefono, email,
           sito_web, rating, num_recensioni, google_place_id
    FROM leads
    WHERE (note IS NULL OR note = '' OR (note NOT LIKE 'FB:%' AND note NOT LIKE 'LABAITA:%'))
    AND google_place_id IS NOT NULL AND google_place_id != ''
    AND categoria = 'ristorante'
    ORDER BY num_recensioni DESC, rating DESC
""").fetchall()
leads = [dict(r) for r in leads]
conn.close()

print(f"Generazione v3 per {len(leads)} ristoranti da processare...")
print("=" * 60)

ok = 0
err = 0
for i, lead in enumerate(leads, 1):
    print(f"[{i:4d}/{len(leads)}] {lead['nome'][:45]:<45}", end=' ', flush=True)
    try:
        slug = genera_slug(lead['nome'])
        foto_urls, place_data = get_place_data(lead['google_place_id'])
        brand = estrai_dati_sito(lead['sito_web'] or '')

        html_l = genera_html_landing(lead, foto_urls, place_data, brand, slug)
        html_p = genera_html_prenota(lead, foto_urls, place_data, brand, slug)

        with open(os.path.join(OUTPUT_DIR, f'{slug}.html'), 'w', encoding='utf-8') as f:
            f.write(html_l)
        with open(os.path.join(OUTPUT_DIR, f'{slug}-prenota.html'), 'w', encoding='utf-8') as f:
            f.write(html_p)

        # Aggiorna nota nel DB
        conn2 = sqlite3.connect('leads.db')
        conn2.execute("UPDATE leads SET note = ? WHERE id = ?",
                      (f"FB:preview:{slug}.html", lead['id']))
        conn2.commit()
        conn2.close()

        print(f"OK | {len(foto_urls)}f")
        ok += 1
    except Exception as e:
        print(f"ERR: {e}")
        err += 1

    time.sleep(0.3)

print("=" * 60)
print(f"FATTO: {ok} generati, {err} errori")
print(f"Cartella: {OUTPUT_DIR}")
