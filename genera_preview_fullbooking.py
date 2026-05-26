"""
LEONARDO — Generatore Preview Personalizzate Full Booking v2
Estrae colori, logo e testo reale dal sito del ristorante
e genera una preview che sembra GIA' la loro pagina.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, requests, os, time, re
from urllib.parse import urljoin, urlparse
from config import GOOGLE_MAPS_API_KEY

PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places/{place_id}"
PHOTO_URL = "https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key=" + GOOGLE_MAPS_API_KEY
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "preview_fullbooking")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS_WEB = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
}

# Colori default Full Booking (usati se non troviamo quelli del sito)
DEFAULT_PRIMARY   = "#1a3a2a"
DEFAULT_SECONDARY = "#c9a84c"
DEFAULT_BG        = "#f7f5f0"


# ── ESTRAZIONE DATI DAL SITO DEL RISTORANTE ──────────────────

def estrai_dati_sito(sito_url: str) -> dict:
    """
    Visita il sito del ristorante ed estrae:
    - Colore primario (header/navbar)
    - Colore accent
    - URL logo
    - Tagline / descrizione breve
    """
    dati = {
        "color_primary": DEFAULT_PRIMARY,
        "color_secondary": DEFAULT_SECONDARY,
        "color_bg": DEFAULT_BG,
        "logo_url": None,
        "tagline": None,
        "descrizione": None,
    }

    if not sito_url or sito_url.strip() == "":
        return dati

    try:
        resp = requests.get(sito_url, headers=HEADERS_WEB, timeout=8, allow_redirects=True)
        html = resp.text
        base_url = resp.url

        # ── Cerca colori nel CSS inline ──
        # Cerca background-color del body / header / nav
        color_patterns = [
            r'(?:header|\.header|nav|\.nav|\.navbar)[^{]{0,80}background(?:-color)?:\s*(#[0-9a-fA-F]{3,8}|rgb[^;]+)',
            r'(?:body)[^{]{0,40}background(?:-color)?:\s*(#[0-9a-fA-F]{3,8})',
            r'--(?:primary|main|brand|color-primary)[^:]*:\s*(#[0-9a-fA-F]{3,8})',
            r'\.btn[^{]{0,60}background(?:-color)?:\s*(#[0-9a-fA-F]{3,8})',
        ]
        colori_trovati = []
        for pat in color_patterns:
            matches = re.findall(pat, html, re.IGNORECASE)
            colori_trovati.extend(matches)

        # Filtra colori validi (non bianco/nero/grigio)
        def is_interesting_color(c):
            c = c.strip().lower()
            if not c.startswith('#') or len(c) < 4:
                return False
            skip = ['#fff', '#ffffff', '#000', '#000000', '#333', '#333333',
                    '#eee', '#eeeeee', '#f0f0f0', '#fafafa', '#e0e0e0', '#ddd']
            return c not in skip

        colori_interessanti = [c for c in colori_trovati if is_interesting_color(c)]
        if colori_interessanti:
            dati["color_primary"] = colori_interessanti[0]
            if len(colori_interessanti) > 1:
                dati["color_secondary"] = colori_interessanti[1]

        # ── Cerca logo ──
        logo_patterns = [
            r'<img[^>]+(?:class|id|alt)=["\'][^"\']*logo[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]+(?:class|id|alt)=["\'][^"\']*logo[^"\']*["\']',
            r'<a[^>]+class=["\'][^"\']*(?:logo|brand|navbar-brand)[^"\']*["\'][^>]*>[\s\S]{0,200}?<img[^>]+src=["\']([^"\']+)["\']',
            r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)["\']',
        ]
        for pat in logo_patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                logo_raw = m.group(1)
                if not logo_raw.startswith('data:'):
                    dati["logo_url"] = urljoin(base_url, logo_raw)
                    break

        # ── Cerca tagline / meta description ──
        meta_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{10,200})["\']', html, re.IGNORECASE)
        if meta_desc:
            dati["tagline"] = meta_desc.group(1).strip()[:120]

        # Cerca og:description
        if not dati["tagline"]:
            og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']{10,200})["\']', html, re.IGNORECASE)
            if og_desc:
                dati["tagline"] = og_desc.group(1).strip()[:120]

        # ── Cerca og:image come foto hero alternativa ──
        og_image = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_image:
            dati["og_image"] = og_image.group(1)

    except Exception:
        pass

    return dati


# ── GOOGLE PLACES ─────────────────────────────────────────────

def get_place_photos(place_id: str):
    url = PLACES_DETAIL_URL.format(place_id=place_id)
    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "photos,rating,userRatingCount,formattedAddress,regularOpeningHours,websiteUri"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        foto_urls = []
        for p in data.get("photos", [])[:5]:
            nome = p.get("name", "")
            if nome:
                foto_urls.append(PHOTO_URL.format(photo_name=nome))
        return foto_urls, data
    except Exception:
        return [], {}


# ── GENERATORE HTML ────────────────────────────────────────────

def genera_html(lead: dict, foto_urls: list, place_data: dict, brand: dict) -> str:

    nome        = lead["nome"]
    citta       = lead["citta"]
    indirizzo   = lead.get("indirizzo") or citta
    telefono    = lead.get("telefono") or ""
    rating      = float(lead.get("rating") or 4.5)
    recensioni  = int(lead.get("num_recensioni") or 0)

    col_primary   = brand.get("color_primary", DEFAULT_PRIMARY)
    col_secondary = brand.get("color_secondary", DEFAULT_SECONDARY)
    col_bg        = brand.get("color_bg", DEFAULT_BG)
    logo_url      = brand.get("logo_url")
    tagline       = brand.get("tagline") or f"Benvenuti da {nome} — prenota il tuo tavolo online"

    # Foto hero: prima Google, poi og:image, poi placeholder
    if foto_urls:
        hero_foto = foto_urls[0]
    elif brand.get("og_image"):
        hero_foto = brand["og_image"]
    else:
        hero_foto = "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200"

    # Gallery
    gallery_html = ""
    for url in foto_urls[1:4]:
        gallery_html += f'<div class="gimg"><img src="{url}" alt="{nome}" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>'

    # Stelle rating
    stars_html = ""
    for i in range(1, 6):
        if i <= int(rating):
            stars_html += '<span class="s full">★</span>'
        elif rating % 1 >= 0.5 and i == int(rating) + 1:
            stars_html += '<span class="s half">★</span>'
        else:
            stars_html += '<span class="s empty">☆</span>'

    # Orari
    orari = place_data.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    orari_html = ""
    if orari:
        for o in orari:
            orari_html += f'<div class="orario-row"><span>{o.split(":")[0]}</span><span>{":" .join(o.split(":")[1:]).strip()}</span></div>'
    else:
        orari_html = '<p style="color:#999;font-style:italic;font-size:13px">Contatta il ristorante per gli orari</p>'

    # Logo HTML
    logo_html = ""
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="Logo {nome}" class="rist-logo" onerror="this.style.display=\'none\'">'

    # Colore testo su primario (bianco o nero in base alla luminosità)
    def testo_su_colore(hex_col):
        try:
            h = hex_col.lstrip('#')
            if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            lum = (0.299*r + 0.587*g + 0.114*b) / 255
            return "#ffffff" if lum < 0.5 else "#1a1a1a"
        except:
            return "#ffffff"

    testo_primary = testo_su_colore(col_primary)
    testo_secondary = testo_su_colore(col_secondary)

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} — Prenota su Full Booking</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --primary:   {col_primary};
  --secondary: {col_secondary};
  --bg:        {col_bg};
  --on-primary:   {testo_primary};
  --on-secondary: {testo_secondary};
}}
*{{ margin:0; padding:0; box-sizing:border-box; }}
body{{ font-family:'Inter',sans-serif; background:var(--bg); color:#2c2c2c; }}

/* TOPBAR FULL BOOKING */
.fb-bar{{
  background:#111; padding:6px 20px;
  display:flex; align-items:center; justify-content:space-between;
  font-size:11px; color:#aaa;
}}
.fb-brand{{ color:#fff; font-weight:700; letter-spacing:1px; font-size:13px; }}
.fb-brand span{{ color:var(--secondary); }}
.fb-preview-tag{{ display:none; }}

/* HEADER RISTORANTE — colori reali del cliente */
.header{{
  background:var(--primary); padding:14px 24px;
  display:flex; align-items:center; justify-content:space-between;
  position:sticky; top:0; z-index:100;
  box-shadow:0 2px 16px rgba(0,0,0,0.25);
}}
.header-left{{ display:flex; align-items:center; gap:14px; }}
.rist-logo{{ height:44px; width:auto; max-width:140px; object-fit:contain; }}
.rist-nome{{
  font-family:'Playfair Display',serif; font-size:20px;
  color:var(--on-primary); letter-spacing:0.5px;
}}
.btn-prenota-top{{
  background:var(--secondary); color:var(--on-secondary);
  border:none; padding:10px 22px; border-radius:6px;
  font-size:13px; font-weight:700; cursor:pointer; letter-spacing:0.5px;
}}

/* HERO */
.hero{{ position:relative; height:420px; overflow:hidden; }}
.hero img{{ width:100%; height:100%; object-fit:cover; }}
.hero-ov{{
  position:absolute; inset:0;
  background:linear-gradient(to top,rgba(0,0,0,0.80) 0%,rgba(0,0,0,0.05) 55%);
}}
.hero-info{{ position:absolute; bottom:30px; left:30px; right:30px; color:#fff; }}
.hero-info h1{{
  font-family:'Playfair Display',serif;
  font-size:clamp(24px,4vw,40px); margin-bottom:10px;
  text-shadow:0 2px 12px rgba(0,0,0,0.6);
}}
.hero-tagline{{
  font-size:14px; color:rgba(255,255,255,0.85);
  margin-bottom:12px; max-width:560px; line-height:1.6;
}}
.hero-meta{{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
.rating-pill{{
  display:flex; align-items:center; gap:5px;
  background:rgba(255,255,255,0.15); backdrop-filter:blur(6px);
  padding:6px 14px; border-radius:20px;
}}
.s{{ font-size:15px; }}
.s.full,.s.half{{ color:#f5c518; }}
.s.empty{{ color:rgba(255,255,255,0.35); }}
.r-num{{ color:#fff; font-weight:700; font-size:15px; }}
.r-cnt{{ color:rgba(255,255,255,0.75); font-size:12px; }}
.hero-citta{{ color:rgba(255,255,255,0.9); font-size:14px; }}

/* LAYOUT */
.wrap{{
  max-width:960px; margin:0 auto; padding:30px 18px;
  display:grid; grid-template-columns:1fr 370px; gap:26px;
}}
@media(max-width:720px){{.wrap{{grid-template-columns:1fr;}}}}

/* GALLERY */
.gallery{{ display:grid; grid-template-columns:1fr 1fr; gap:6px; border-radius:10px; overflow:hidden; margin-bottom:22px; }}
.gimg img{{ width:100%; height:145px; object-fit:cover; display:block; }}

/* INFO CARDS */
.card{{
  background:#fff; border-radius:12px; padding:22px;
  margin-bottom:18px; box-shadow:0 2px 14px rgba(0,0,0,0.06);
}}
.card h3{{
  font-family:'Playfair Display',serif; font-size:16px;
  color:var(--primary); margin-bottom:14px;
  padding-bottom:10px; border-bottom:2px solid var(--bg);
}}
.info-r{{ display:flex; gap:10px; margin-bottom:9px; font-size:14px; color:#555; }}
.info-r .ico{{ font-size:17px; flex-shrink:0; }}
.orario-row{{
  display:flex; justify-content:space-between;
  font-size:13px; color:#555; padding:4px 0;
  border-bottom:1px solid #f5f5f5;
}}

/* PERCHE FULL BOOKING */
.why-item{{ display:flex; align-items:flex-start; gap:10px; margin-bottom:10px; }}
.why-icon{{
  width:30px; height:30px; border-radius:50%;
  background:var(--primary); color:var(--on-primary);
  display:flex; align-items:center; justify-content:center;
  font-size:13px; flex-shrink:0;
}}
.why-text{{ font-size:13px; color:#555; line-height:1.5; }}
.why-text strong{{ color:#2c2c2c; font-size:13px; }}

/* BOOKING CARD */
.booking-card{{
  background:#fff; border-radius:14px; padding:26px;
  box-shadow:0 4px 28px rgba(0,0,0,0.11);
  border-top:4px solid var(--primary);
  position:sticky; top:68px; height:fit-content;
}}
.booking-card h2{{
  font-family:'Playfair Display',serif; font-size:20px;
  color:var(--primary); margin-bottom:4px;
}}
.bk-sub{{ font-size:13px; color:#999; margin-bottom:20px; }}
.fg{{ margin-bottom:14px; }}
.fg label{{
  display:block; font-size:11px; font-weight:700;
  color:#777; margin-bottom:5px;
  text-transform:uppercase; letter-spacing:0.5px;
}}
.fg input,.fg select{{
  width:100%; padding:11px 13px;
  border:1.5px solid #e8e0d5; border-radius:8px;
  font-size:14px; color:#2c2c2c; background:#fafaf8;
  font-family:'Inter',sans-serif; appearance:none;
}}
.fg input:focus,.fg select:focus{{
  outline:none; border-color:var(--primary); background:#fff;
}}
.fg-row{{ display:grid; grid-template-columns:1fr 1fr; gap:11px; }}
.btn-book{{
  width:100%; padding:15px; margin-top:6px;
  background:var(--primary); color:var(--on-primary);
  border:none; border-radius:10px; font-size:15px; font-weight:700;
  cursor:pointer; font-family:'Inter',sans-serif; letter-spacing:0.5px;
  transition:opacity 0.2s;
}}
.btn-book:hover{{opacity:0.88;}}
.bk-note{{ text-align:center; font-size:11px; color:#bbb; margin-top:12px; }}
.bk-note span{{ color:var(--secondary); font-weight:700; }}

/* FOOTER */
footer{{
  background:#111; color:rgba(255,255,255,0.5);
  text-align:center; padding:22px; font-size:12px; margin-top:36px;
}}
footer strong{{ color:var(--secondary); }}
</style>
</head>
<body>

<!-- TOPBAR FULL BOOKING -->
<div class="fb-bar">
  <span class="fb-brand">FULL<span>BOOKING</span>.it</span>
  <span style="font-size:11px;color:#666;">Sistema di prenotazione online</span>
</div>

<!-- HEADER con colori reali del ristorante -->
<header class="header">
  <div class="header-left">
    {logo_html}
    <span class="rist-nome">{nome}</span>
  </div>
  <button class="btn-prenota-top" onclick="document.querySelector('.booking-card').scrollIntoView({{behavior:'smooth'}})">
    📅 Prenota Ora
  </button>
</header>

<!-- HERO -->
<div class="hero">
  <img src="{hero_foto}" alt="{nome}"
       onerror="this.src='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200'">
  <div class="hero-ov"></div>
  <div class="hero-info">
    <h1>{nome}</h1>
    <p class="hero-tagline">{tagline}</p>
    <div class="hero-meta">
      <div class="rating-pill">
        {stars_html}
        <span class="r-num">{rating}</span>
        <span class="r-cnt">({recensioni:,} recensioni Google)</span>
      </div>
      <span class="hero-citta">📍 {citta}</span>
    </div>
  </div>
</div>

<!-- CONTENUTO -->
<div class="wrap">

  <!-- SINISTRA -->
  <div>

    {'<div class="gallery">' + gallery_html + '</div>' if gallery_html else ''}

    <div class="card">
      <h3>📍 Dove siamo</h3>
      <div class="info-r"><span class="ico">🏠</span><span>{indirizzo}</span></div>
      {'<div class="info-r"><span class="ico">📞</span><span>' + telefono + '</span></div>' if telefono else ''}
      <div class="info-r"><span class="ico">⭐</span><span><strong>{rating}/5</strong> su {recensioni:,} recensioni Google</span></div>
    </div>

    <div class="card">
      <h3>🕐 Orari di apertura</h3>
      {orari_html}
    </div>

    <div class="card">
      <h3>🏆 Perché prenotare online con Full Booking?</h3>

      <div class="why-item">
        <div class="why-icon">24</div>
        <div class="why-text"><strong>Prenota quando vuoi</strong><br>Il sistema accetta prenotazioni 24 ore su 24, anche a mezzanotte.</div>
      </div>
      <div class="why-item">
        <div class="why-icon">✓</div>
        <div class="why-text"><strong>Conferma immediata via WhatsApp</strong><br>Ricevi la conferma sul cellulare in pochi secondi.</div>
      </div>
      <div class="why-item">
        <div class="why-icon">0€</div>
        <div class="why-text"><strong>Nessuna commissione</strong><br>La prenotazione diretta è sempre gratuita per il cliente.</div>
      </div>

      <div class="why-item">
        <div class="why-icon">📧</div>
        <div class="why-text"><strong>Riepilogo via email</strong><br>Ricevi anche un'email con tutti i dettagli della prenotazione.</div>
      </div>
    </div>

  </div>

  <!-- DESTRA — FORM -->
  <div>
    <div class="booking-card">
      <h2>Prenota il tuo tavolo</h2>
      <p class="bk-sub">da {nome} · {citta}</p>

      <div class="fg">
        <label>Data</label>
        <input type="date" id="data-input">
      </div>
      <div class="fg-row">
        <div class="fg">
          <label>Orario</label>
          <select>
            <option>12:30</option><option>13:00</option><option>13:30</option>
            <option>20:00</option><option selected>20:30</option>
            <option>21:00</option><option>21:30</option><option>22:00</option>
          </select>
        </div>
        <div class="fg">
          <label>Persone</label>
          <select>
            <option>1</option><option selected>2</option>
            <option>3</option><option>4</option><option>5</option><option>6+</option>
          </select>
        </div>
      </div>
      <div class="fg">
        <label>Nome e Cognome</label>
        <input type="text" placeholder="Mario Rossi">
      </div>
      <div class="fg-row">
        <div class="fg">
          <label>Telefono</label>
          <input type="tel" placeholder="+39 333 000 0000">
        </div>
        <div class="fg">
          <label>Email</label>
          <input type="email" placeholder="mario@email.it">
        </div>
      </div>
      <div class="fg">
        <label>Note speciali (opzionale)</label>
        <input type="text" placeholder="Allergie, occasioni speciali...">
      </div>

      <button class="btn-book">🗓️ Verifica Disponibilità</button>

      <p class="bk-note">
        Powered by <span>Full Booking</span> · Prenotazione gratuita · Zero commissioni
      </p>
    </div>
  </div>

</div>

<footer>
  <strong>Full Booking</strong> · Sistema di prenotazione online per ristoranti<br>
  <span style="font-size:11px;opacity:0.6;">© 2025 fullbooking.it · Tutti i diritti riservati</span>
</footer>

<script>
  const d = new Date(); d.setDate(d.getDate()+1);
  document.getElementById('data-input').value = d.toISOString().split('T')[0];
  document.getElementById('data-input').min = d.toISOString().split('T')[0];
</script>
</body>
</html>"""


# ── UTILS ──────────────────────────────────────────────────────

def genera_slug(nome):
    import re
    s = nome.lower()
    for a,b in [("à","a"),("á","a"),("è","e"),("é","e"),("ì","i"),("ò","o"),("ù","u")]:
        s = s.replace(a,b)
    s = re.sub(r"[^a-z0-9\s-]","",s)
    s = re.sub(r"\s+","-",s.strip())
    return re.sub(r"-+","-",s)[:55]


# ── MAIN ───────────────────────────────────────────────────────

def main(limite=10):
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, citta, indirizzo, telefono, email,
               sito_web, rating, num_recensioni, google_place_id
        FROM leads
        WHERE note = 'LABAITA:target'
        AND google_place_id IS NOT NULL AND google_place_id != ''
        ORDER BY num_recensioni DESC, rating DESC
        LIMIT ?
    """, (limite,))
    leads = cur.fetchall()

    print("=" * 65)
    print(f"  LEONARDO · Full Booking Preview Generator v2")
    print(f"  {len(leads)} ristoranti con colori dal sito reale")
    print("=" * 65)

    ok = 0
    for i, lead in enumerate(leads, 1):
        nome_short = lead['nome'][:42]
        print(f"[{i:3d}/{len(leads)}] {nome_short:<42}", end=" ", flush=True)

        # 1. Foto reali da Google Places
        foto_urls, place_data = get_place_photos(lead["google_place_id"])

        # 2. Colori/logo/tagline dal sito del ristorante
        brand = estrai_dati_sito(lead["sito_web"] or "")

        # 3. Genera HTML personalizzato
        html = genera_html(dict(lead), foto_urls, place_data, brand)

        # 4. Salva
        slug = genera_slug(lead["nome"])
        filename = f"{slug}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        cur.execute("UPDATE leads SET note = ? WHERE id = ?",
                    (f"FB:preview:{filename}", lead["id"]))
        conn.commit()

        col = brand.get("color_primary", DEFAULT_PRIMARY)
        logo = "✓logo" if brand.get("logo_url") else "no-logo"
        tag  = "✓tag"  if brand.get("tagline")  else "no-tag"
        print(f"OK | {len(foto_urls)}foto | {col} | {logo} | {tag}")
        ok += 1
        time.sleep(0.4)

    conn.close()
    print(f"\n  FATTO! {ok} preview in: {OUTPUT_DIR}")

    # Apri la prima nel browser
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.html')]
    if files:
        import subprocess
        subprocess.Popen(["start", os.path.join(OUTPUT_DIR, files[0])], shell=True)


if __name__ == "__main__":
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(limite)
