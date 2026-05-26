# ============================================================
#  GF LEAD HUNTER — Estrattore Email dai Siti Web
# ============================================================
import re
import requests
from bs4 import BeautifulSoup
from database import get_leads, aggiorna_email

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

EMAIL_BLACKLIST = [
    "example.com", "test.com", "gmail.com", "yahoo.com", "hotmail.com",
    "wix.com", "wordpress.com", "sentry.io", "google.com", "facebook.com",
    "instagram.com", "support@", "noreply@", "no-reply@"
]


def estrai_email_da_sito(url: str) -> str | None:
    """Visita un sito web ed estrae la prima email di contatto trovata."""
    if not url:
        return None
    if not url.startswith("http"):
        url = "https://" + url

    # Pagine da visitare in ordine
    pagine_contatto = ["", "/contatti", "/contattaci", "/contact", "/chi-siamo", "/about"]

    for path in pagine_contatto:
        try:
            full_url = url.rstrip("/") + path
            resp = requests.get(full_url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Cerca nei mailto
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("mailto:"):
                    email = href.replace("mailto:", "").split("?")[0].strip()
                    if email and not any(b in email for b in EMAIL_BLACKLIST):
                        return email

            # Cerca nel testo
            testo = soup.get_text()
            emails = EMAIL_REGEX.findall(testo)
            for email in emails:
                if not any(b in email for b in EMAIL_BLACKLIST):
                    return email

        except Exception:
            continue

    return None


def arricchisci_tutti():
    """Cerca le email per tutti i lead con sito web ma senza email."""
    leads = get_leads()
    da_arricchire = [l for l in leads if l.get("sito_web") and not l.get("email")]

    print(f"\n🔍 Arricchimento email — {len(da_arricchire)} lead da processare")
    trovate = 0

    for i, lead in enumerate(da_arricchire, 1):
        print(f"[{i}/{len(da_arricchire)}] {lead['nome']}...", end=" ")
        email = estrai_email_da_sito(lead["sito_web"])
        if email:
            aggiorna_email(lead["id"], email)
            print(f"✅ {email}")
            trovate += 1
        else:
            print("❌ non trovata")

    print(f"\n📧 Email trovate: {trovate}/{len(da_arricchire)}")
    return trovate
