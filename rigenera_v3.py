"""
Rigenera TUTTE le pagine (landing + prenota) per i 53 ristoranti
contattati usando il template v3 nero/oro (stile La Baita).
Sovrascrive i file esistenti generati con il vecchio template verde.
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys, sqlite3, time
from genera_preview_fullbooking import (
    get_place_data, estrai_dati_sito, genera_slug,
    genera_html_landing, genera_html_prenota, OUTPUT_DIR
)

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

print(f"Rigenerazione v3 per {len(leads)} ristoranti (landing + prenota)...")
ok = 0
err = 0

for i, lead in enumerate(leads, 1):
    print(f"[{i:3d}/{len(leads)}] {lead['nome'][:45]:<45}", end=' ', flush=True)
    try:
        slug = genera_slug(lead['nome'])
        foto_urls, place_data = get_place_data(lead['google_place_id'])
        brand = estrai_dati_sito(lead['sito_web'] or '')

        html_landing = genera_html_landing(lead, foto_urls, place_data, brand, slug)
        html_prenota = genera_html_prenota(lead, foto_urls, place_data, brand, slug)

        landing_file = os.path.join(OUTPUT_DIR, f'{slug}.html')
        prenota_file = os.path.join(OUTPUT_DIR, f'{slug}-prenota.html')

        with open(landing_file, 'w', encoding='utf-8') as f:
            f.write(html_landing)
        with open(prenota_file, 'w', encoding='utf-8') as f:
            f.write(html_prenota)

        print(f'OK | {len(foto_urls)} foto')
        ok += 1
    except Exception as e:
        print(f'ERRORE: {e}')
        err += 1

    time.sleep(0.3)

print(f"\nFatto: {ok} rigenerati, {err} errori")
print(f"Ora esegui il deploy su Netlify!")
