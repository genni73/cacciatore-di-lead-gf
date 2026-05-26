"""
LA BAITA — Analisi siti ristoranti
Verifica quali ristoranti NON hanno sistema di prenotazione online
=> Questi sono i nostri target prioritari
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import requests
import time
from urllib.parse import urlparse

# Parole chiave che indicano GIA' un sistema di prenotazione
KEYWORDS_HA_PRENOTAZIONE = [
    "thefork", "the fork", "lafourchette",
    "opentable", "open table",
    "quandoo",
    "resy.com",
    "yelp.com/reservations",
    "prenota ora",
    "prenota il tuo tavolo",
    "prenotazione online",
    "reservations",
    "book a table",
    "book now",
    "bookatable",
    "fork.it",
    "tripadvisor.com/restaurantreservations",
    "sevenrooms",
    "prenotazioni.me",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
}


def ha_prenotazione(sito_web: str) -> tuple[bool, str]:
    """
    Ritorna (True, motivo) se il sito ha prenotazione, (False, "") altrimenti.
    """
    if not sito_web or sito_web.strip() == "":
        return None, "nessun sito"

    # Controlla già dall'URL
    url_lower = sito_web.lower()
    for kw in KEYWORDS_HA_PRENOTAZIONE:
        if kw in url_lower:
            return True, f"URL contiene '{kw}'"

    try:
        resp = requests.get(
            sito_web,
            headers=HEADERS,
            timeout=8,
            allow_redirects=True
        )
        html = resp.text.lower()

        for kw in KEYWORDS_HA_PRENOTAZIONE:
            if kw in html:
                return True, f"Sito contiene '{kw}'"

        return False, "nessun sistema trovato"

    except requests.exceptions.SSLError:
        # Riprova senza SSL
        try:
            sito_http = sito_web.replace("https://", "http://")
            resp = requests.get(sito_http, headers=HEADERS, timeout=8, allow_redirects=True)
            html = resp.text.lower()
            for kw in KEYWORDS_HA_PRENOTAZIONE:
                if kw in html:
                    return True, f"Sito contiene '{kw}'"
            return False, "nessun sistema trovato"
        except:
            return None, "errore SSL"
    except requests.exceptions.ConnectionError:
        return None, "sito non raggiungibile"
    except requests.exceptions.Timeout:
        return None, "timeout"
    except Exception as e:
        return None, f"errore: {str(e)[:40]}"


def main():
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Prendi tutti i ristoranti con sito web non ancora analizzati
    cur.execute("""
        SELECT id, nome, citta, sito_web FROM leads
        WHERE categoria = 'ristorante'
        AND sito_web IS NOT NULL AND sito_web != ''
        AND (note IS NULL OR note NOT LIKE 'LABAITA:%')
        ORDER BY rating DESC, num_recensioni DESC
    """)
    leads = cur.fetchall()
    totale = len(leads)

    print("=" * 65)
    print(f"  LA BAITA — Analisi {totale} siti ristoranti")
    print("=" * 65)

    con_prenotazione = 0
    senza_prenotazione = 0
    non_raggiungibili = 0

    for i, lead in enumerate(leads, 1):
        print(f"[{i:4d}/{totale}] {lead['nome'][:40]:<40} ({lead['citta']})...", end=" ", flush=True)

        ha, motivo = ha_prenotazione(lead['sito_web'])

        if ha is True:
            tag = f"LABAITA:ha_prenotazione:{motivo[:50]}"
            con_prenotazione += 1
            print(f"GIA' PRENOTA ({motivo[:35]})")
        elif ha is False:
            tag = "LABAITA:target"
            senza_prenotazione += 1
            print(f"*** TARGET LA BAITA ***")
        else:
            tag = f"LABAITA:errore:{motivo[:50]}"
            non_raggiungibili += 1
            print(f"[{motivo}]")

        cur.execute("UPDATE leads SET note = ? WHERE id = ?", (tag, lead['id']))
        conn.commit()

        time.sleep(0.3)

    conn.close()

    print("\n" + "=" * 65)
    print(f"  ANALISI COMPLETATA!")
    print(f"  Gia' con prenotazione:    {con_prenotazione:4d}  (esclusi)")
    print(f"  TARGET La Baita:          {senza_prenotazione:4d}  *** QUESTI CONTATTARE ***")
    print(f"  Siti non raggiungibili:   {non_raggiungibili:4d}")
    print("=" * 65)
    print(f"\n  Prossimo step: genera preview personalizzate per i {senza_prenotazione} target!")


if __name__ == "__main__":
    main()
