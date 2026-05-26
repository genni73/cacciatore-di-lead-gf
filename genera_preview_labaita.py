"""
LEONARDO — Generatore Preview Personalizzate Full Booking
Per ogni ristorante target genera una pagina HTML con:
- Foto reali da Google Places
- Nome, rating, indirizzo personalizzati
- Form di prenotazione mock Full Booking
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import requests
import os
import time
from config import GOOGLE_MAPS_API_KEY

PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places/{place_id}"
PHOTO_URL = "https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key=" + GOOGLE_MAPS_API_KEY

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "preview_fullbooking")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_place_photos(place_id: str) -> list:
    """Recupera le URL delle foto reali da Google Places."""
    url = PLACES_DETAIL_URL.format(place_id=place_id)
    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "photos,displayName,rating,userRatingCount,formattedAddress,regularOpeningHours"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        photos = data.get("photos", [])
        foto_urls = []
        for p in photos[:4]:  # max 4 foto
            nome = p.get("name", "")
            if nome:
                foto_url = PHOTO_URL.format(photo_name=nome)
                foto_urls.append(foto_url)
        return foto_urls, data
    except Exception as e:
        return [], {}


def genera_html(lead: dict, foto_urls: list, place_data: dict) -> str:
    """Genera l'HTML della preview personalizzata."""

    nome = lead["nome"]
    citta = lead["citta"]
    indirizzo = lead.get("indirizzo", citta)
    rating = lead.get("rating") or 4.5
    recensioni = lead.get("num_recensioni") or 0
    stelle = "★" * int(rating) + ("½" if rating % 1 >= 0.5 else "") + "☆" * (5 - int(rating))

    # Orari apertura
    orari_html = ""
    orari = place_data.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    if orari:
        orari_items = "".join([f"<li>{o}</li>" for o in orari[:4]])
        orari_html = f"<ul class='orari-list'>{orari_items}</ul>"
    else:
        orari_html = "<p class='orari-nd'>Contatta il ristorante per gli orari</p>"

    # Foto principali
    if foto_urls:
        hero_foto = foto_urls[0]
        gallery_html = ""
        for i, url in enumerate(foto_urls[1:3], 1):
            gallery_html += f'<div class="gallery-img"><img src="{url}" alt="Foto {nome}" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>'
    else:
        hero_foto = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800"
        gallery_html = ""

    # stelle rating visivo
    rating_float = float(rating)
    stars_html = ""
    for i in range(1, 6):
        if i <= int(rating_float):
            stars_html += '<span class="star full">★</span>'
        elif i - rating_float < 1 and rating_float % 1 >= 0.5:
            stars_html += '<span class="star half">★</span>'
        else:
            stars_html += '<span class="star empty">☆</span>'

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} — Prenota su Full Booking</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', sans-serif;
    background: #f7f5f0;
    color: #2c2c2c;
    min-height: 100vh;
  }}

  /* ── HEADER FULL BOOKING ── */
  .header {{
    background: #1a3a2a;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3);
  }}
  .logo {{
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: #c9a84c;
    letter-spacing: 1px;
  }}
  .logo span {{ color: #fff; font-size: 13px; display: block; font-family: 'Inter', sans-serif; font-weight: 300; letter-spacing: 2px; }}
  .header-cta {{
    background: #c9a84c;
    color: #fff;
    border: none;
    padding: 10px 22px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.5px;
  }}

  /* ── ANTEPRIMA BADGE ── */
  .preview-banner {{
    background: linear-gradient(135deg, #c9a84c, #e8c875);
    color: #1a3a2a;
    text-align: center;
    padding: 10px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }}

  /* ── HERO ── */
  .hero {{
    position: relative;
    height: 380px;
    overflow: hidden;
  }}
  .hero img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .hero-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.1) 60%);
  }}
  .hero-info {{
    position: absolute;
    bottom: 28px;
    left: 28px;
    right: 28px;
    color: white;
  }}
  .hero-info h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(22px, 4vw, 36px);
    margin-bottom: 8px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }}
  .hero-meta {{
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .rating-box {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(4px);
    padding: 5px 12px;
    border-radius: 20px;
  }}
  .star {{ font-size: 16px; }}
  .star.full {{ color: #f5c518; }}
  .star.half {{ color: #f5c518; }}
  .star.empty {{ color: rgba(255,255,255,0.4); }}
  .rating-num {{ color: white; font-weight: 600; font-size: 15px; }}
  .rating-count {{ color: rgba(255,255,255,0.8); font-size: 12px; }}
  .hero-citta {{
    color: rgba(255,255,255,0.9);
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  /* ── CONTENUTO ── */
  .content {{
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 20px;
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 28px;
  }}
  @media(max-width: 700px) {{
    .content {{ grid-template-columns: 1fr; }}
  }}

  /* ── GALLERY ── */
  .gallery {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 24px;
    border-radius: 10px;
    overflow: hidden;
  }}
  .gallery-img img {{
    width: 100%;
    height: 140px;
    object-fit: cover;
    display: block;
  }}

  /* ── INFO RISTORANTE ── */
  .info-card {{
    background: white;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  }}
  .info-card h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    color: #1a3a2a;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0ebe0;
  }}
  .info-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
    font-size: 14px;
    color: #555;
  }}
  .info-icon {{ font-size: 18px; flex-shrink: 0; margin-top: 1px; }}
  .orari-list {{ list-style: none; font-size: 13px; color: #555; line-height: 1.8; padding-left: 4px; }}
  .orari-nd {{ font-size: 13px; color: #999; font-style: italic; }}

  /* ── FORM PRENOTAZIONE ── */
  .booking-card {{
    background: white;
    border-radius: 14px;
    padding: 26px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    border-top: 4px solid #1a3a2a;
    position: sticky;
    top: 80px;
    height: fit-content;
  }}
  .booking-card h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    color: #1a3a2a;
    margin-bottom: 6px;
  }}
  .booking-subtitle {{
    font-size: 13px;
    color: #888;
    margin-bottom: 22px;
  }}
  .form-group {{
    margin-bottom: 16px;
  }}
  .form-group label {{
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: #555;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .form-group input,
  .form-group select {{
    width: 100%;
    padding: 11px 14px;
    border: 1.5px solid #e8e0d5;
    border-radius: 8px;
    font-size: 14px;
    color: #2c2c2c;
    background: #fafaf8;
    font-family: 'Inter', sans-serif;
    appearance: none;
  }}
  .form-group input:focus,
  .form-group select:focus {{
    outline: none;
    border-color: #1a3a2a;
    background: white;
  }}
  .form-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }}
  .btn-prenota {{
    width: 100%;
    padding: 15px;
    background: #1a3a2a;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 8px;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.5px;
    transition: background 0.2s;
  }}
  .btn-prenota:hover {{ background: #2d6a4f; }}
  .booking-note {{
    text-align: center;
    font-size: 11px;
    color: #aaa;
    margin-top: 12px;
  }}
  .booking-note span {{ color: #c9a84c; font-weight: 600; }}

  /* ── FOOTER ── */
  .footer {{
    background: #1a3a2a;
    color: rgba(255,255,255,0.6);
    text-align: center;
    padding: 24px;
    font-size: 12px;
    margin-top: 40px;
  }}
  .footer strong {{ color: #c9a84c; }}

  /* ── DEMO WATERMARK ── */
  .demo-notice {{
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    font-size: 13px;
    color: #856404;
    text-align: center;
  }}
</style>
</head>
<body>

<!-- HEADER -->
<header class="header">
  <div class="logo">
    FULL BOOKING
    <span>PIATTAFORMA DI PRENOTAZIONE</span>
  </div>
  <button class="header-cta" onclick="document.querySelector('.booking-card').scrollIntoView({{behavior:'smooth'}})">
    Prenota Ora
  </button>
</header>

<!-- BANNER ANTEPRIMA -->
<div class="preview-banner">
  🎯 Questa è un'ANTEPRIMA esclusiva di come apparirebbe {nome} su Full Booking
</div>

<!-- HERO -->
<div class="hero">
  <img src="{hero_foto}" alt="{nome}" onerror="this.src='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800'">
  <div class="hero-overlay"></div>
  <div class="hero-info">
    <h1>{nome}</h1>
    <div class="hero-meta">
      <div class="rating-box">
        {stars_html}
        <span class="rating-num">{rating}</span>
        <span class="rating-count">({recensioni:,} recensioni)</span>
      </div>
      <div class="hero-citta">📍 {citta}</div>
    </div>
  </div>
</div>

<!-- CONTENUTO PRINCIPALE -->
<div class="content">

  <!-- COLONNA SINISTRA -->
  <div class="left-col">

    <!-- AVVISO DEMO -->
    <div class="demo-notice">
      ⭐ <strong>Anteprima riservata a {nome}</strong> — La tua pagina su Full Booking potrebbe apparire esattamente così, con le tue foto e informazioni reali.
    </div>

    <!-- GALLERY FOTO -->
    {f'<div class="gallery">{gallery_html}</div>' if gallery_html else ''}

    <!-- INFO RISTORANTE -->
    <div class="info-card">
      <h3>📍 Informazioni</h3>
      <div class="info-row">
        <span class="info-icon">🏠</span>
        <span>{indirizzo}</span>
      </div>
      <div class="info-row">
        <span class="info-icon">⭐</span>
        <span><strong>{rating}/5</strong> basato su {recensioni:,} recensioni Google</span>
      </div>
    </div>

    <!-- ORARI -->
    <div class="info-card">
      <h3>🕐 Orari di apertura</h3>
      {orari_html}
    </div>

    <!-- PERCHE FULL BOOKING -->
    <div class="info-card">
      <h3>🏔️ Perché scegliere Full Booking?</h3>
      <div class="info-row"><span class="info-icon">✅</span><span>Prenotazioni online 24/7 — anche quando sei chiuso</span></div>
      <div class="info-row"><span class="info-icon">✅</span><span>Zero commissioni per le prenotazioni dirette</span></div>
      <div class="info-row"><span class="info-icon">✅</span><span>Pagina attiva in 24 ore — senza costi di setup</span></div>
      <div class="info-row"><span class="info-icon">✅</span><span>Gestione tavoli e fasce orarie personalizzabili</span></div>
      <div class="info-row"><span class="info-icon">✅</span><span>Clienti ricevono conferma automatica via WhatsApp</span></div>
    </div>

  </div>

  <!-- COLONNA DESTRA — FORM PRENOTAZIONE -->
  <div class="right-col">
    <div class="booking-card">
      <h2>Prenota un Tavolo</h2>
      <p class="booking-subtitle">Disponibilità in tempo reale</p>

      <div class="form-group">
        <label>Data</label>
        <input type="date" id="data">
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Orario</label>
          <select>
            <option>12:30</option><option>13:00</option><option>13:30</option>
            <option selected>20:00</option><option>20:30</option>
            <option>21:00</option><option>21:30</option>
          </select>
        </div>
        <div class="form-group">
          <label>Persone</label>
          <select>
            <option>1</option><option selected>2</option>
            <option>3</option><option>4</option>
            <option>5</option><option>6+</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Nome e Cognome</label>
        <input type="text" placeholder="Es. Mario Rossi">
      </div>

      <div class="form-group">
        <label>Telefono</label>
        <input type="tel" placeholder="+39 333 000 0000">
      </div>

      <button class="btn-prenota">
        🗓️ Verifica Disponibilità
      </button>

      <p class="booking-note">
        Powered by <span>Full Booking</span> · Prenotazione gratuita · Nessuna commissione
      </p>
    </div>
  </div>

</div>

<!-- FOOTER -->
<footer class="footer">
  <strong>Full Booking</strong> — Piattaforma di prenotazione per ristoranti · Valle di Maddaloni, Caserta<br>
  Questa è un'anteprima dimostrativa creata per {nome} · Attiva la tua pagina su Full Booking oggi stesso
</footer>

<script>
  // Imposta data di oggi come default
  const oggi = new Date();
  const domani = new Date(oggi);
  domani.setDate(domani.getDate() + 1);
  const iso = domani.toISOString().split('T')[0];
  document.getElementById('data').value = iso;
  document.getElementById('data').min = iso;
</script>
</body>
</html>"""

    return html


def genera_slug(nome: str) -> str:
    """Genera un nome file pulito dal nome del ristorante."""
    import re
    slug = nome.lower()
    slug = re.sub(r"[àáâã]", "a", slug)
    slug = re.sub(r"[èéêë]", "e", slug)
    slug = re.sub(r"[ìíîï]", "i", slug)
    slug = re.sub(r"[òóôõ]", "o", slug)
    slug = re.sub(r"[ùúûü]", "u", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:60]


def main(limite: int = 50):
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, citta, indirizzo, telefono, email, sito_web,
               rating, num_recensioni, google_place_id
        FROM leads
        WHERE note = 'LABAITA:target'
        AND google_place_id IS NOT NULL AND google_place_id != ''
        ORDER BY num_recensioni DESC, rating DESC
        LIMIT ?
    """, (limite,))
    leads = cur.fetchall()

    print("=" * 60)
    print(f"  LEONARDO — Generatore Preview Full Booking")
    print(f"  Generando {len(leads)} preview personalizzate...")
    print("=" * 60)

    generate_ok = 0

    for i, lead in enumerate(leads, 1):
        print(f"[{i:3d}/{len(leads)}] {lead['nome'][:45]:<45}...", end=" ", flush=True)

        # Fetch foto da Google Places
        foto_urls, place_data = get_place_photos(lead["google_place_id"])

        # Genera HTML
        html = genera_html(dict(lead), foto_urls, place_data)

        # Salva file
        slug = genera_slug(lead["nome"])
        filename = f"{slug}-{lead['google_place_id'][-6:]}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        # Salva path nel DB
        cur.execute("UPDATE leads SET note = ? WHERE id = ?",
                    (f"LABAITA:preview:{filename}", lead["id"]))
        conn.commit()

        foto_count = len(foto_urls)
        print(f"OK ({foto_count} foto)")
        generate_ok += 1

        time.sleep(0.3)  # rispetta rate limit Google

    conn.close()

    print("\n" + "=" * 60)
    print(f"  COMPLETATO! {generate_ok} preview generate")
    print(f"  Cartella: {OUTPUT_DIR}")
    print("=" * 60)

    # Apri la prima preview nel browser
    if generate_ok > 0:
        import subprocess
        first_file = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.html')][0]
        first_path = os.path.join(OUTPUT_DIR, first_file)
        print(f"\n  Apertura anteprima: {first_file}")
        subprocess.Popen(["start", first_path], shell=True)


if __name__ == "__main__":
    import sys
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    main(limite)
