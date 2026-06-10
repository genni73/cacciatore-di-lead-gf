"""
LEONARDO — Full Booking Generator v3
Stile La Baita: nero profondo + oro elegante.
Genera DUE pagine per ogni ristorante:
  [slug].html          → landing page (il "sito regalato")
  [slug]-prenota.html  → pagina prenotazione
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, requests, os, time, re
from urllib.parse import urljoin
from config import GOOGLE_MAPS_API_KEY, FULLBOOKING_BASE_URL, TELEFONO

PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places/{place_id}"
PHOTO_URL = "https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=1200&key=" + GOOGLE_MAPS_API_KEY
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "preview_fullbooking")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS_WEB = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
}

# ── STILE LA BAITA ────────────────────────────────────────────
CSS_VARS = """
  --nero:     #0a0a0a;
  --nero2:    #141414;
  --nero3:    #1e1e1e;
  --oro:      #c9a84c;
  --oro2:     #e8c96b;
  --crema:    #f0ead6;
  --grigio:   #8a8a8a;
  --bianco:   #ffffff;
"""

CSS_BASE = """
*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', sans-serif;
  background: var(--nero);
  color: var(--crema);
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
img { display: block; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--nero2); }
::-webkit-scrollbar-thumb { background: var(--oro); border-radius: 3px; }

/* Topbar Full Booking */
.fb-topbar {
  background: var(--nero);
  border-bottom: 1px solid rgba(201,168,76,0.2);
  padding: 10px 32px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 200;
  backdrop-filter: blur(12px);
}
.fb-logo {
  font-family: 'Playfair Display', serif;
  font-size: 18px; letter-spacing: 3px; font-weight: 700;
  color: var(--bianco);
}
.fb-logo span { color: var(--oro); }
.fb-topbar-cta {
  font-size: 11px; color: var(--grigio);
  letter-spacing: 1px; text-transform: uppercase;
}

/* Bottone oro */
.btn-oro {
  display: inline-block;
  background: linear-gradient(135deg, var(--oro), var(--oro2));
  color: var(--nero);
  padding: 14px 36px;
  font-size: 12px; font-weight: 700;
  letter-spacing: 2px; text-transform: uppercase;
  border: none; cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: opacity .2s, transform .2s;
}
.btn-oro:hover { opacity: .88; transform: translateY(-1px); }

/* Linea oro decorativa */
.gold-line {
  width: 48px; height: 2px;
  background: linear-gradient(90deg, var(--oro), var(--oro2));
  margin: 0 auto 20px;
}
.gold-line.left { margin: 0 0 20px; }
"""


# ── GOOGLE PLACES ─────────────────────────────────────────────

def get_place_data(place_id: str):
    url = PLACES_DETAIL_URL.format(place_id=place_id)
    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "photos,rating,userRatingCount,formattedAddress,regularOpeningHours,websiteUri,editorialSummary"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        foto_urls = []
        for p in data.get("photos", [])[:6]:
            nome = p.get("name", "")
            if nome:
                foto_urls.append(PHOTO_URL.format(photo_name=nome))
        return foto_urls, data
    except Exception:
        return [], {}


# ── ESTRAZIONE DAL SITO ───────────────────────────────────────

def estrai_dati_sito(sito_url: str) -> dict:
    dati = {"logo_url": None, "tagline": None, "og_image": None}
    if not sito_url or not sito_url.strip():
        return dati
    try:
        resp = requests.get(sito_url, headers=HEADERS_WEB, timeout=8, allow_redirects=True)
        html = resp.text
        base_url = resp.url

        # Logo
        for pat in [
            r'<img[^>]+(?:class|id|alt)=["\'][^"\']*logo[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]+(?:class|id|alt)=["\'][^"\']*logo[^"\']*["\']',
            r'<a[^>]+class=["\'][^"\']*(?:logo|brand|navbar-brand)[^"\']*["\'][^>]*>[\s\S]{0,200}?<img[^>]+src=["\']([^"\']+)["\']',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m and not m.group(1).startswith('data:'):
                dati["logo_url"] = urljoin(base_url, m.group(1))
                break

        # Tagline
        for pat in [
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{10,200})["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']{10,200})["\']',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                dati["tagline"] = m.group(1).strip()[:160]
                break

        # OG image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if m:
            dati["og_image"] = m.group(1)

    except Exception:
        pass
    return dati


# ── UTILS ─────────────────────────────────────────────────────

def genera_slug(nome):
    s = nome.lower()
    for a, b in [("à","a"),("á","a"),("è","e"),("é","e"),("ì","i"),("ò","o"),("ù","u")]:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return re.sub(r"-+", "-", s)[:55]

def stelle_html(rating):
    html = ""
    for i in range(1, 6):
        if i <= int(rating):
            html += '<span class="star full">★</span>'
        elif rating % 1 >= 0.5 and i == int(rating) + 1:
            html += '<span class="star half">★</span>'
        else:
            html += '<span class="star empty">☆</span>'
    return html


# ── PAGINA 1: LANDING ─────────────────────────────────────────

def genera_html_landing(lead: dict, foto_urls: list, place_data: dict, brand: dict, slug: str) -> str:
    nome       = lead["nome"]
    citta      = lead["citta"]
    indirizzo  = lead.get("indirizzo") or citta
    telefono   = lead.get("telefono") or ""
    rating     = float(lead.get("rating") or 4.5)
    recensioni = int(lead.get("num_recensioni") or 0)
    sito_web   = lead.get("sito_web") or ""

    tagline    = brand.get("tagline") or f"Cucina autentica nel cuore di {citta}"
    logo_url   = brand.get("logo_url")

    hero_foto = foto_urls[0] if foto_urls else (brand.get("og_image") or "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1600")

    orari = place_data.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    orari_html = ""
    if orari:
        for o in orari:
            parti = o.split(":", 1)
            giorno = parti[0].strip()
            ore = parti[1].strip() if len(parti) > 1 else "—"
            orari_html += f'<div class="orario-row"><span class="orario-giorno">{giorno}</span><span class="orario-ore">{ore}</span></div>'
    else:
        orari_html = '<p class="no-info">Contatta il ristorante per gli orari aggiornati</p>'

    gallery_items = ""
    for url in foto_urls[1:5]:
        gallery_items += f'<div class="gallery-item"><img src="{url}" alt="{nome}" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>'

    logo_html = ""
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="Logo {nome}" class="nav-logo" onerror="this.style.display=\'none\'">'

    editorial = place_data.get("editorialSummary", {}).get("text", "") or tagline

    prenota_url = f"{slug}-prenota.html"

    # Pre-calcola gallery HTML fuori dall'f-string principale
    if len(foto_urls) >= 2:
        gallery_items_html = "".join(
            f'<div class="gallery-item"><img src="{u}" alt="{nome}" loading="lazy" onerror="this.parentElement.style.display:none"></div>'
            for u in foto_urls[:5]
        )
        gallery_section_html = f"""<section id="galleria" class="gallery-section">
  <div style="max-width:1200px;margin:0 auto 40px">
    <div class="section-label">Galleria</div>
    <h2 class="section-titolo">Le nostre immagini</h2>
    <div class="gold-line left"></div>
  </div>
  <div class="gallery-grid">{gallery_items_html}</div>
</section>"""
    else:
        gallery_section_html = ""

    # Foto sezione chi-siamo
    foto_chisiamo = foto_urls[1] if len(foto_urls) > 1 else hero_foto

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} — {citta} | Full Booking</title>
<meta name="description" content="{tagline}">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ {CSS_VARS} }}
{CSS_BASE}

/* NAVBAR */
.navbar {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 300;
  background: rgba(10,10,10,0.92);
  border-bottom: 1px solid rgba(201,168,76,0.15);
  padding: 0 40px;
  display: flex; align-items: center; justify-content: space-between;
  height: 68px;
  backdrop-filter: blur(16px);
  transition: background .3s;
}}
.navbar-brand {{
  display: flex; align-items: center; gap: 14px;
}}
.nav-logo {{ height: 40px; width: auto; max-width: 130px; object-fit: contain; }}
.navbar-nome {{
  font-family: 'Playfair Display', serif;
  font-size: 17px; color: var(--crema); letter-spacing: .5px;
}}
.navbar-links {{
  display: flex; align-items: center; gap: 32px;
}}
.navbar-links a {{
  font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
  color: var(--grigio); transition: color .2s;
}}
.navbar-links a:hover {{ color: var(--oro); }}
.navbar-prenota {{
  background: linear-gradient(135deg, var(--oro), var(--oro2));
  color: var(--nero) !important;
  padding: 10px 22px;
  font-size: 11px !important; font-weight: 700 !important;
  letter-spacing: 2px;
}}
.navbar-prenota:hover {{ opacity: .88; }}
@media(max-width: 768px) {{
  .navbar {{ padding: 0 20px; }}
  .navbar-links {{ display: none; }}
}}

/* HERO */
.hero {{
  height: 100vh; min-height: 600px;
  position: relative; overflow: hidden;
}}
.hero-img {{
  width: 100%; height: 100%; object-fit: cover;
  transform: scale(1.04);
  transition: transform 8s ease;
}}
.hero:hover .hero-img {{ transform: scale(1); }}
.hero-overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(10,10,10,0.3) 0%,
    rgba(10,10,10,0.1) 40%,
    rgba(10,10,10,0.85) 100%
  );
}}
.hero-content {{
  position: absolute; bottom: 80px; left: 0; right: 0;
  padding: 0 60px;
  max-width: 900px;
}}
.hero-badge {{
  display: inline-block;
  border: 1px solid var(--oro);
  color: var(--oro);
  font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
  padding: 6px 16px; margin-bottom: 20px;
}}
.hero-titolo {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(36px, 6vw, 72px);
  font-weight: 700; line-height: 1.1;
  color: var(--bianco);
  text-shadow: 0 2px 40px rgba(0,0,0,0.5);
  margin-bottom: 16px;
}}
.hero-tagline {{
  font-size: 15px; color: rgba(240,234,214,0.8);
  line-height: 1.7; max-width: 540px; margin-bottom: 24px;
  font-weight: 300;
}}
.hero-meta {{
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
}}
.rating-pill {{
  display: flex; align-items: center; gap: 8px;
  background: rgba(201,168,76,0.12);
  border: 1px solid rgba(201,168,76,0.3);
  padding: 8px 18px;
}}
.star {{ font-size: 14px; }}
.star.full, .star.half {{ color: var(--oro); }}
.star.empty {{ color: rgba(201,168,76,0.25); }}
.rating-num {{ color: var(--oro); font-weight: 700; font-size: 15px; }}
.rating-cnt {{ color: rgba(240,234,214,0.6); font-size: 12px; }}
.hero-citta {{ color: rgba(240,234,214,0.75); font-size: 13px; letter-spacing: 1px; }}
@media(max-width: 768px) {{
  .hero-content {{ padding: 0 24px; bottom: 60px; }}
}}

/* SCROLL INDICATOR */
.scroll-ind {{
  position: absolute; bottom: 28px; left: 50%;
  transform: translateX(-50%);
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: rgba(201,168,76,0.5); font-size: 10px; letter-spacing: 2px;
  text-transform: uppercase;
  animation: bounce 2s infinite;
}}
.scroll-ind::after {{
  content: ''; width: 1px; height: 40px;
  background: linear-gradient(to bottom, var(--oro), transparent);
}}
@keyframes bounce {{
  0%,100% {{ opacity: .5; transform: translateX(-50%) translateY(0); }}
  50% {{ opacity: 1; transform: translateX(-50%) translateY(6px); }}
}}

/* BOTTONE PRENOTA FLOTTANTE */
.btn-prenota-float {{
  position: fixed;
  bottom: 36px; right: 36px;
  z-index: 500;
  width: 96px; height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--oro), var(--oro2));
  color: var(--nero);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 11px; font-weight: 800;
  letter-spacing: 2px; text-transform: uppercase;
  text-decoration: none;
  box-shadow: 0 8px 32px rgba(201,168,76,0.35), 0 2px 8px rgba(0,0,0,0.4);
  transition: transform .25s, box-shadow .25s, opacity .25s;
  opacity: 0;
  transform: scale(0.7) translateY(20px);
  pointer-events: none;
}}
.btn-prenota-float.visible {{
  opacity: 1;
  transform: scale(1) translateY(0);
  pointer-events: auto;
}}
.btn-prenota-float:hover {{
  transform: scale(1.07) translateY(-3px);
  box-shadow: 0 14px 40px rgba(201,168,76,0.5), 0 4px 12px rgba(0,0,0,0.4);
}}
.btn-prenota-float .float-arrow {{
  font-size: 18px; line-height: 1;
  transition: transform .2s;
}}
.btn-prenota-float:hover .float-arrow {{
  transform: translateY(3px);
}}
@media(max-width: 768px) {{
  .btn-prenota-float {{
    width: 80px; height: 80px;
    bottom: 24px; right: 20px;
    font-size: 10px;
    opacity: 1; transform: scale(1) translateY(0);
    pointer-events: auto;
  }}
}}

/* SEZIONI */
section {{ padding: 100px 60px; }}
@media(max-width: 768px) {{ section {{ padding: 60px 24px; }} }}

.section-label {{
  font-size: 10px; letter-spacing: 4px; text-transform: uppercase;
  color: var(--oro); margin-bottom: 14px;
}}
.section-titolo {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(28px, 4vw, 42px); font-weight: 600;
  color: var(--crema); line-height: 1.2; margin-bottom: 20px;
}}

/* CHI SIAMO */
.chi-siamo {{
  max-width: 1100px; margin: 0 auto;
  display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center;
}}
@media(max-width: 768px) {{ .chi-siamo {{ grid-template-columns: 1fr; gap: 40px; }} }}
.chi-siamo-testo p {{
  font-size: 16px; line-height: 1.9; color: rgba(240,234,214,0.75);
  font-weight: 300; margin-bottom: 16px;
}}
.chi-siamo-foto {{
  position: relative; height: 480px;
}}
.chi-siamo-foto img {{
  width: 100%; height: 100%; object-fit: cover;
}}
.chi-siamo-foto::before {{
  content: '';
  position: absolute; inset: -12px -12px 12px 12px;
  border: 1px solid rgba(201,168,76,0.25);
  z-index: -1;
}}

/* GALLERY */
.gallery-section {{ background: var(--nero2); }}
.gallery-grid {{
  max-width: 1200px; margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: 280px 280px;
  gap: 4px;
}}
.gallery-item {{ overflow: hidden; position: relative; }}
.gallery-item:first-child {{
  grid-column: span 2; grid-row: span 2;
}}
.gallery-item img {{
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .6s ease;
}}
.gallery-item:hover img {{ transform: scale(1.05); }}
@media(max-width: 768px) {{
  .gallery-grid {{ grid-template-columns: 1fr 1fr; grid-template-rows: auto; }}
  .gallery-item:first-child {{ grid-column: span 2; height: 220px; }}
  .gallery-item {{ height: 160px; }}
}}

/* INFO + ORARI */
.info-section {{
  max-width: 1100px; margin: 0 auto;
  display: grid; grid-template-columns: 1fr 1fr; gap: 80px;
}}
@media(max-width: 768px) {{ .info-section {{ grid-template-columns: 1fr; gap: 48px; }} }}
.info-card {{
  border-top: 1px solid rgba(201,168,76,0.2);
  padding-top: 32px;
}}
.info-row {{
  display: flex; align-items: flex-start; gap: 16px;
  margin-bottom: 20px; padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.info-row:last-child {{ border-bottom: none; }}
.info-ico {{
  width: 36px; height: 36px; flex-shrink: 0;
  background: rgba(201,168,76,0.1);
  border: 1px solid rgba(201,168,76,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
}}
.info-txt {{ font-size: 14px; color: rgba(240,234,214,0.75); line-height: 1.6; }}
.info-txt strong {{ color: var(--crema); font-size: 12px; letter-spacing: 1px; text-transform: uppercase; display: block; margin-bottom: 4px; }}
.orario-row {{
  display: flex; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 13px;
}}
.orario-giorno {{ color: var(--crema); }}
.orario-ore {{ color: var(--grigio); text-align: right; }}
.no-info {{ font-size: 13px; color: var(--grigio); font-style: italic; }}

/* CTA PRENOTA */
.cta-section {{
  background: var(--nero2);
  border-top: 1px solid rgba(201,168,76,0.15);
  border-bottom: 1px solid rgba(201,168,76,0.15);
  text-align: center;
  padding: 120px 60px;
}}
.cta-section .section-titolo {{ margin-bottom: 14px; }}
.cta-section p {{
  font-size: 15px; color: rgba(240,234,214,0.6);
  max-width: 500px; margin: 0 auto 40px;
  line-height: 1.7; font-weight: 300;
}}
.cta-duo {{
  display: flex; align-items: center; justify-content: center;
  gap: 20px; flex-wrap: wrap;
}}
.btn-outline {{
  display: inline-block;
  border: 1px solid var(--oro);
  color: var(--oro);
  padding: 14px 36px;
  font-size: 12px; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  transition: all .2s;
}}
.btn-outline:hover {{ background: var(--oro); color: var(--nero); }}

/* FOOTER */
footer {{
  background: var(--nero);
  border-top: 1px solid rgba(201,168,76,0.1);
  padding: 48px 60px 32px;
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: 24px;
}}
.footer-brand {{
  font-family: 'Playfair Display', serif;
  font-size: 20px; letter-spacing: 3px; color: var(--crema);
}}
.footer-brand span {{ color: var(--oro); }}
.footer-copy {{
  font-size: 11px; color: rgba(138,138,138,0.5);
  letter-spacing: 1px;
}}
@media(max-width: 768px) {{
  footer {{ padding: 40px 24px 28px; flex-direction: column; align-items: flex-start; }}
}}
</style>
</head>
<body>

<!-- BOTTONE PRENOTA FLOTTANTE -->
<a href="{prenota_url}" class="btn-prenota-float" id="floatBtn">
  <span>PRENOTA</span>
  <span class="float-arrow">↓</span>
</a>

<!-- NAVBAR -->
<nav class="navbar">
  <div class="navbar-brand">
    {logo_html}
    <span class="navbar-nome">{nome}</span>
  </div>
  <div class="navbar-links">
    <a href="#ristorante">Il Ristorante</a>
    <a href="#galleria">Galleria</a>
    <a href="#orari">Orari</a>
    <a href="{prenota_url}" class="navbar-prenota">Prenota</a>
  </div>
</nav>

<!-- HERO -->
<section class="hero">
  <img class="hero-img" src="{hero_foto}" alt="{nome}"
       onerror="this.src='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1600'">
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-badge">Full Booking · {citta}</div>
    <h1 class="hero-titolo">{nome}</h1>
    <p class="hero-tagline">{tagline}</p>
    <div class="hero-meta">
      <div class="rating-pill">
        {stelle_html(rating)}
        <span class="rating-num">{rating}</span>
        <span class="rating-cnt">({recensioni:,} recensioni)</span>
      </div>
      <span class="hero-citta">📍 {citta}</span>
    </div>
  </div>
  <div class="scroll-ind">Scopri</div>
</section>

<!-- CHI SIAMO -->
<section id="ristorante">
  <div class="chi-siamo">
    <div class="chi-siamo-testo">
      <div class="section-label">Il Ristorante</div>
      <h2 class="section-titolo">{nome}</h2>
      <div class="gold-line left"></div>
      <p>{editorial}</p>
      <p>Prenota il tuo tavolo online in pochi secondi — conferma immediata su WhatsApp, zero commissioni.</p>
      <br>
      <a href="{prenota_url}" class="btn-oro">Prenota Ora</a>
    </div>
    <div class="chi-siamo-foto">
      <img src="{foto_chisiamo}" alt="{nome}"
           onerror="this.src='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800'">
    </div>
  </div>
</section>

<!-- GALLERY -->
{gallery_section_html}

<!-- ORARI E INFO -->
<section id="orari">
  <div class="info-section">
    <div class="info-card">
      <div class="section-label">Informazioni</div>
      <h2 class="section-titolo" style="font-size:26px">Dove siamo</h2>
      <div class="gold-line left"></div>
      <div class="info-row">
        <div class="info-ico">📍</div>
        <div class="info-txt"><strong>Indirizzo</strong>{indirizzo}</div>
      </div>
      {'<div class="info-row"><div class="info-ico">📞</div><div class="info-txt"><strong>Telefono</strong>' + telefono + '</div></div>' if telefono else ''}
      <div class="info-row">
        <div class="info-ico">⭐</div>
        <div class="info-txt"><strong>Valutazione Google</strong>{rating}/5 su {recensioni:,} recensioni</div>
      </div>
      {'<div class="info-row"><div class="info-ico">🌐</div><div class="info-txt"><strong>Sito web</strong><a href="' + sito_web + '" style="color:var(--oro)">' + sito_web[:45] + '</a></div></div>' if sito_web else ''}
    </div>
    <div class="info-card">
      <div class="section-label">Orari</div>
      <h2 class="section-titolo" style="font-size:26px">Quando apriremo</h2>
      <div class="gold-line left"></div>
      {orari_html}
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <div class="section-label">Prenotazione Online</div>
  <h2 class="section-titolo">Riserva il tuo tavolo</h2>
  <div class="gold-line"></div>
  <p>Prenota in 30 secondi. Conferma immediata su WhatsApp.<br>Zero commissioni — sempre gratuito per i clienti.</p>
  <div class="cta-duo">
    <a href="{prenota_url}" class="btn-oro">📅 Prenota Ora</a>
    {'<a href="tel:' + telefono + '" class="btn-outline">📞 Chiama</a>' if telefono else ''}
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div>
    <div class="footer-brand">FULL<span>BOOKING</span></div>
    <div style="font-size:12px;color:var(--grigio);margin-top:6px;letter-spacing:1px">
      Sistema di prenotazione online · {nome} · {citta}
    </div>
  </div>
  <div class="footer-copy">
    © 2025 fullbooking.cloud · Powered by GF Technological System
  </div>
</footer>

<script>
  // Bottone prenota flottante — appare dopo 80% dell'altezza hero
  const floatBtn = document.getElementById('floatBtn');
  const heroH = document.querySelector('.hero').offsetHeight;
  window.addEventListener('scroll', () => {{
    if (window.scrollY > heroH * 0.8) {{
      floatBtn.classList.add('visible');
    }} else {{
      floatBtn.classList.remove('visible');
    }}
  }}, {{ passive: true }});
</script>
</body>
</html>"""


# ── PAGINA 2: PRENOTAZIONE ─────────────────────────────────────

def genera_html_prenota(lead: dict, foto_urls: list, place_data: dict, brand: dict, slug: str) -> str:
    nome       = lead["nome"]
    citta      = lead["citta"]
    telefono   = lead.get("telefono") or ""
    rating     = float(lead.get("rating") or 4.5)
    recensioni = int(lead.get("num_recensioni") or 0)
    logo_url   = brand.get("logo_url")

    hero_foto = foto_urls[0] if foto_urls else (brand.get("og_image") or "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200")

    logo_html = ""
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="Logo {nome}" class="form-logo" onerror="this.style.display=\'none\'">'

    landing_url = f"{slug}.html"

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prenota — {nome} | Full Booking</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ {CSS_VARS} }}
{CSS_BASE}

body {{
  min-height: 100vh;
  background: var(--nero);
  display: grid;
  grid-template-rows: auto 1fr auto;
}}

/* HEADER */
.prenota-header {{
  background: var(--nero);
  border-bottom: 1px solid rgba(201,168,76,0.15);
  padding: 20px 40px;
  display: flex; align-items: center; justify-content: space-between;
}}
.header-brand {{
  display: flex; align-items: center; gap: 14px;
}}
.form-logo {{ height: 38px; width: auto; max-width: 120px; object-fit: contain; }}
.header-nome {{
  font-family: 'Playfair Display', serif;
  font-size: 18px; color: var(--crema);
}}
.header-fb {{
  font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
  color: var(--grigio);
}}
.header-back {{
  font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
  color: var(--grigio); transition: color .2s;
}}
.header-back:hover {{ color: var(--oro); }}

/* HERO STRIP */
.prenota-hero {{
  height: 220px; position: relative; overflow: hidden;
}}
.prenota-hero img {{
  width: 100%; height: 100%; object-fit: cover;
  filter: brightness(.45);
}}
.prenota-hero-content {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
}}
.prenota-hero-content h1 {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(22px, 4vw, 38px); color: var(--crema);
  margin-bottom: 8px;
}}
.prenota-hero-content .rating-strip {{
  display: flex; align-items: center; gap: 8px;
}}
.star.full, .star.half {{ color: var(--oro); font-size: 14px; }}
.star.empty {{ color: rgba(201,168,76,0.25); font-size: 14px; }}
.prenota-hero-content .r-num {{ color: var(--oro); font-weight: 700; }}
.prenota-hero-content .r-cnt {{ color: rgba(240,234,214,0.55); font-size: 12px; }}

/* MAIN */
.prenota-main {{
  max-width: 560px; margin: 0 auto;
  padding: 56px 24px;
  width: 100%;
}}

.form-intro {{
  text-align: center; margin-bottom: 44px;
}}
.form-intro .section-label {{ display: block; margin-bottom: 10px; }}
.form-intro h2 {{
  font-family: 'Playfair Display', serif;
  font-size: 28px; color: var(--crema); margin-bottom: 8px;
}}
.form-intro p {{
  font-size: 14px; color: var(--grigio); line-height: 1.7; font-weight: 300;
}}

/* FORM */
.form-group {{ margin-bottom: 20px; }}
.form-group label {{
  display: block;
  font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
  color: var(--grigio); margin-bottom: 8px;
}}
.form-group input,
.form-group select,
.form-group textarea {{
  width: 100%; padding: 14px 16px;
  background: var(--nero2);
  border: 1px solid rgba(201,168,76,0.15);
  color: var(--crema);
  font-size: 14px; font-family: 'Inter', sans-serif;
  transition: border-color .2s;
  appearance: none;
}}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {{
  outline: none;
  border-color: rgba(201,168,76,0.5);
  background: rgba(201,168,76,0.04);
}}
.form-group input::placeholder,
.form-group textarea::placeholder {{ color: rgba(138,138,138,0.5); }}
.form-group select option {{ background: var(--nero2); }}
.form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}

.divider {{
  display: flex; align-items: center; gap: 16px;
  margin: 28px 0;
}}
.divider::before, .divider::after {{
  content: ''; flex: 1; height: 1px;
  background: rgba(201,168,76,0.15);
}}
.divider span {{
  font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
  color: rgba(138,138,138,0.5);
}}

.btn-prenota-full {{
  width: 100%;
  background: linear-gradient(135deg, var(--oro), var(--oro2));
  color: var(--nero);
  border: none; padding: 18px;
  font-size: 12px; font-weight: 700;
  letter-spacing: 3px; text-transform: uppercase;
  cursor: pointer; font-family: 'Inter', sans-serif;
  transition: opacity .2s, transform .15s;
  margin-top: 8px;
}}
.btn-prenota-full:hover {{ opacity: .88; transform: translateY(-1px); }}

.form-note {{
  text-align: center; margin-top: 20px;
  font-size: 11px; color: rgba(138,138,138,0.5);
  line-height: 1.7; letter-spacing: .5px;
}}
.form-note span {{ color: var(--oro); }}

/* GARANZIE */
.garanzie {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1px; background: rgba(201,168,76,0.1);
  margin-top: 48px;
}}
.garanzia {{
  background: var(--nero2);
  padding: 24px 16px; text-align: center;
}}
.garanzia-ico {{
  font-size: 22px; margin-bottom: 10px;
}}
.garanzia-titolo {{
  font-size: 11px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: var(--crema);
  margin-bottom: 6px;
}}
.garanzia-testo {{
  font-size: 11px; color: var(--grigio); line-height: 1.5;
}}

/* FOOTER PRENOTA */
.prenota-footer {{
  background: var(--nero);
  border-top: 1px solid rgba(201,168,76,0.1);
  padding: 24px 40px;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 12px;
}}
.prenota-footer .fb-logo {{
  font-family: 'Playfair Display', serif;
  font-size: 15px; letter-spacing: 3px; color: var(--crema);
}}
.prenota-footer .fb-logo span {{ color: var(--oro); }}
.prenota-footer-copy {{
  font-size: 11px; color: rgba(138,138,138,0.4);
}}

@media(max-width: 480px) {{
  .form-row {{ grid-template-columns: 1fr; }}
  .garanzie {{ grid-template-columns: 1fr; }}
  .prenota-header {{ padding: 16px 20px; }}
}}
</style>
</head>
<body>

<!-- HEADER -->
<header class="prenota-header">
  <div class="header-brand">
    {logo_html}
    <div>
      <div class="header-nome">{nome}</div>
      <div class="header-fb">Full Booking · {citta}</div>
    </div>
  </div>
  <a href="{landing_url}" class="header-back">← Torna al sito</a>
</header>

<!-- HERO STRIP -->
<div class="prenota-hero">
  <img src="{hero_foto}" alt="{nome}"
       onerror="this.src='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200'">
  <div class="prenota-hero-content">
    <h1>Prenota da {nome}</h1>
    <div class="rating-strip">
      {stelle_html(rating)}
      <span class="r-num">{rating}</span>
      <span class="r-cnt">({recensioni:,} recensioni)</span>
    </div>
  </div>
</div>

<!-- FORM -->
<main class="prenota-main">

  <div class="form-intro">
    <span class="section-label">Prenotazione Tavolo</span>
    <h2>Quando ci vieni a trovare?</h2>
    <p>Prenota in 30 secondi — ricevi conferma immediata su WhatsApp</p>
  </div>

  <form onsubmit="inviaPrenotazione(event)">

    <div class="form-row">
      <div class="form-group">
        <label>Data</label>
        <input type="date" id="data-input" required>
      </div>
      <div class="form-group">
        <label>Orario</label>
        <select id="orario" required>
          <option value="">— Scegli —</option>
          <option>12:00</option><option>12:30</option><option>13:00</option><option>13:30</option>
          <option>19:30</option><option>20:00</option><option selected>20:30</option>
          <option>21:00</option><option>21:30</option><option>22:00</option>
        </select>
      </div>
    </div>

    <div class="form-group">
      <label>Numero di persone</label>
      <select id="persone" required>
        <option value="">— Quanti siete? —</option>
        <option>1 persona</option><option selected>2 persone</option>
        <option>3 persone</option><option>4 persone</option>
        <option>5 persone</option><option>6 persone</option>
        <option>7–10 persone</option><option>Più di 10</option>
      </select>
    </div>

    <div class="divider"><span>I tuoi dati</span></div>

    <div class="form-group">
      <label>Nome e Cognome</label>
      <input id="nome-cliente" type="text" placeholder="Mario Rossi" required>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>Telefono (WhatsApp)</label>
        <input id="tel-cliente" type="tel" placeholder="+39 333 000 0000" required>
      </div>
      <div class="form-group">
        <label>Email</label>
        <input id="email-cliente" type="email" placeholder="mario@email.it">
      </div>
    </div>

    <div class="form-group">
      <label>Note speciali (opzionale)</label>
      <input id="note-cliente" type="text" placeholder="Allergie, compleanno, tavolo esterno...">
    </div>

    <button type="submit" class="btn-prenota-full">Prenota su WhatsApp</button>

    <p class="form-note">
      Conferma immediata su WhatsApp · <span>Zero commissioni</span> · Cancellazione gratuita
    </p>

  </form>

  <!-- GARANZIE -->
  <div class="garanzie">
    <div class="garanzia">
      <div class="garanzia-ico">⚡</div>
      <div class="garanzia-titolo">Conferma Istantanea</div>
      <div class="garanzia-testo">Ricevi conferma su WhatsApp in pochi secondi</div>
    </div>
    <div class="garanzia">
      <div class="garanzia-ico">🎯</div>
      <div class="garanzia-titolo">Zero Commissioni</div>
      <div class="garanzia-testo">La prenotazione diretta è sempre gratuita</div>
    </div>
    <div class="garanzia">
      <div class="garanzia-ico">🕐</div>
      <div class="garanzia-titolo">24h su 24</div>
      <div class="garanzia-testo">Prenota quando vuoi, anche a mezzanotte</div>
    </div>
  </div>

</main>

<!-- FOOTER -->
<footer class="prenota-footer">
  <div class="fb-logo">FULL<span>BOOKING</span></div>
  <div class="prenota-footer-copy">
    © 2025 fullbooking.cloud · Powered by GF Technological System
  </div>
</footer>

<script>
  // Imposta data minima = domani
  const d = new Date(); d.setDate(d.getDate() + 1);
  const iso = d.toISOString().split('T')[0];
  const inp = document.getElementById('data-input');
  inp.value = iso; inp.min = iso;

  function inviaPrenotazione(e) {{
    e.preventDefault();

    const nome_cl  = document.getElementById('nome-cliente').value.trim();
    const tel_cl   = document.getElementById('tel-cliente').value.trim();
    const data_r   = document.getElementById('data-input').value;
    const orario_r = document.getElementById('orario').value;
    const persone  = document.getElementById('persone').value;

    if (!nome_cl || !tel_cl || !data_r || !orario_r || !persone) {{
      alert('Compila tutti i campi obbligatori.');
      return;
    }}

    const btn = e.target.querySelector('.btn-prenota-full');
    const noteEl = document.querySelector('.form-note');

    // Simulazione invio (demo promozionale)
    btn.textContent = 'Invio in corso...';
    btn.disabled = true;

    setTimeout(function() {{
      btn.textContent = 'Prenotazione confermata!';
      btn.style.background = 'linear-gradient(135deg, #1a6a2a, #2a8a3a)';
      noteEl.innerHTML = '<strong style="color:var(--oro)">Riceverai la conferma su WhatsApp entro pochi minuti. Grazie!</strong>';

      // Mostra riepilogo prenotazione
      const riepilogo = document.createElement('div');
      riepilogo.style.cssText = 'margin-top:1.5rem;padding:1.2rem;background:rgba(201,168,76,0.1);border:1px solid var(--oro);border-radius:8px;font-size:0.9rem;line-height:1.8;';
      const [y,m,gg2] = data_r.split('-');
      riepilogo.innerHTML =
        '<div style="color:var(--oro);font-weight:600;margin-bottom:0.5rem;">Riepilogo prenotazione</div>' +
        '<div>Ristorante: <strong>{nome}</strong></div>' +
        '<div>Data: <strong>' + gg2+'/'+m+'/'+y + '</strong></div>' +
        '<div>Orario: <strong>' + orario_r + '</strong></div>' +
        '<div>Persone: <strong>' + persone + '</strong></div>' +
        '<div>Nome: <strong>' + nome_cl + '</strong></div>';
      e.target.appendChild(riepilogo);
    }}, 1200);
  }}
</script>
</body>
</html>"""


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

    print("=" * 70)
    print(f"  LEONARDO · Full Booking Generator v3 — Stile Nero/Oro Elegante")
    print(f"  {len(leads)} ristoranti → 2 pagine ciascuno (landing + prenotazione)")
    print("=" * 70)

    ok = 0
    for i, lead in enumerate(leads, 1):
        nome_short = lead['nome'][:40]
        print(f"[{i:3d}/{len(leads)}] {nome_short:<40}", end=" ", flush=True)

        foto_urls, place_data = get_place_data(lead["google_place_id"])
        brand = estrai_dati_sito(lead["sito_web"] or "")

        slug = genera_slug(lead["nome"])
        landing_file  = f"{slug}.html"
        prenota_file  = f"{slug}-prenota.html"

        html_landing = genera_html_landing(dict(lead), foto_urls, place_data, brand, slug)
        html_prenota = genera_html_prenota(dict(lead), foto_urls, place_data, brand, slug)

        for filename, html in [(landing_file, html_landing), (prenota_file, html_prenota)]:
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

        cur.execute("UPDATE leads SET note = ? WHERE id = ?",
                    (f"FB:preview:{landing_file}", lead["id"]))
        conn.commit()

        logo = "✓logo" if brand.get("logo_url") else "—"
        print(f"OK | {len(foto_urls)}foto | {logo} | landing+prenota")
        ok += 1
        time.sleep(0.4)

    conn.close()
    print(f"\n  FATTO! {ok} ristoranti → {ok*2} pagine in: {OUTPUT_DIR}")
    print(f"\n  Prossimi passi:")
    print(f"  1. Esegui DEPLOY_FULLBOOKING.bat  → carica tutto su Netlify")
    print(f"  2. python main.py fullbooking-wa  → invia i WhatsApp")
    print(f"\n  URL esempio:")
    if ok > 0:
        print(f"  {FULLBOOKING_BASE_URL}/{genera_slug(leads[0]['nome'])}")
        print(f"  {FULLBOOKING_BASE_URL}/{genera_slug(leads[0]['nome'])}-prenota")


if __name__ == "__main__":
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(limite)
