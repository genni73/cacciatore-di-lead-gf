# Prepara cartella Netlify Full Booking

import sqlite3
import shutil
import os

SRC_DIR    = "preview_fullbooking"
DEPLOY_DIR = "C:/Users/genna/Desktop/fullbooking-deploy"

os.makedirs(DEPLOY_DIR, exist_ok=True)

conn = sqlite3.connect("leads.db")
rows = conn.execute(
    "SELECT nome, fb_token, note FROM leads "
    "WHERE fb_token IS NOT NULL AND fb_token != '' AND note LIKE 'FB:%'"
).fetchall()
conn.close()

copiati   = 0
mancanti  = 0
errori    = []

for nome, token, note in rows:
    filename = note.replace("FB:preview:", "").replace("FB:inviato:", "").strip()
    src_path = os.path.join(SRC_DIR, filename)
    dst_path = os.path.join(DEPLOY_DIR, f"{token}.html")

    if not os.path.exists(src_path):
        mancanti += 1
        errori.append(f"MANCANTE: {filename} ({nome})")
        continue

    shutil.copy2(src_path, dst_path)
    copiati += 1

# File _redirects → URL senza .html (es: /vUiflNd → /vUiflNd.html)
redirects_path = os.path.join(DEPLOY_DIR, "_redirects")
with open(redirects_path, "w", encoding="utf-8") as f:
    f.write("# Netlify redirects — URL senza .html\n")
    f.write("/:token  /:token.html  200\n")

# index.html — pagina principale Full Booking
index_path = os.path.join(DEPLOY_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Full Booking — Sistema Prenotazioni</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', sans-serif;
    background: #0a0f2e;
    color: #e8f0ff;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px;
  }
  .logo { font-size: 2.4rem; font-weight: 800; color: #1a8fff; margin-bottom: 12px; }
  .tagline { font-size: 1.1rem; opacity: 0.7; }
</style>
</head>
<body>
  <div>
    <div class="logo">Full Booking</div>
    <div class="tagline">Sistema di prenotazione online per ristoranti</div>
  </div>
</body>
</html>
""")

print(f"\n{'='*55}")
print(f"  NETLIFY DEPLOY PRONTO")
print(f"{'='*55}")
print(f"  Cartella:   {DEPLOY_DIR}")
print(f"  Copiati:    {copiati} file HTML")
print(f"  Mancanti:   {mancanti}")
if errori:
    for e in errori[:5]:
        print(f"  - {e}")
print(f"{'='*55}")
print(f"""
PROSSIMI PASSI:
  1. Vai su https://app.netlify.com
  2. Trascina la cartella 'fullbooking-deploy'
     sul riquadro "Drag and drop your site folder here"
  3. Il sito prende un nome tipo: random-name-123456.netlify.app
  4. Nelle impostazioni cambia il nome in: fullbooking-preview
  5. Dimmi il nome finale e aggiorno tutti i link!
""")
