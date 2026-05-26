"""
Scraping massiccio ristoranti per La Baita
Cerca: ristorante, pizzeria, trattoria, osteria in tutta la Campania
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import time
import sqlite3
from config import GOOGLE_MAPS_API_KEY, ZONE_CAMPANIA

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.internationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.regularOpeningHours",
    "places.priceLevel",
    "places.types",
    "places.photos",
])

# Query multiple per catturare piu risultati
QUERIES_RISTORANTE = [
    "ristorante",
    "pizzeria",
    "trattoria",
    "osteria",
    "rosticceria",
    "braceria",
]


def cerca_ristoranti(query_tipo: str, citta: str) -> list:
    query = f"{query_tipo} {citta} Campania Italia"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK
    }
    body = {
        "textQuery": query,
        "languageCode": "it",
        "regionCode": "IT",
        "maxResultCount": 20
    }
    try:
        resp = requests.post(PLACES_URL, json=body, headers=headers, timeout=15)
        data = resp.json()
        if "error" in data:
            print(f"   Errore API: {data['error'].get('message', '')[:80]}")
            return []
        return data.get("places", [])
    except Exception as e:
        print(f"   Errore: {e}")
        return []


def get_db():
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    return conn


def place_exists(conn, place_id: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT id FROM leads WHERE google_place_id = ?", (place_id,))
    return cur.fetchone() is not None


def salva_ristorante(conn, place: dict, citta: str) -> bool:
    place_id = place.get("id", "")
    if not place_id or place_exists(conn, place_id):
        return False

    nome = place.get("displayName", {}).get("text", "")
    if not nome:
        return False

    # Foto: salva i nomi delle foto per recuperarle dopo
    photos = place.get("photos", [])
    photo_names = "|".join([p.get("name", "") for p in photos[:5]])

    # Orari apertura
    orari = ""
    opening = place.get("regularOpeningHours", {})
    if opening:
        desc = opening.get("weekdayDescriptions", [])
        orari = " | ".join(desc[:3])  # primi 3 giorni come esempio

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leads
        (nome, categoria, citta, indirizzo, telefono, email, sito_web,
         rating, num_recensioni, google_place_id, stato, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        "ristorante",
        citta,
        place.get("formattedAddress", ""),
        place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber", ""),
        "",
        place.get("websiteUri", ""),
        place.get("rating"),
        place.get("userRatingCount"),
        place_id,
        "nuovo",
        photo_names  # salviamo i nomi foto nel campo note temporaneamente
    ))
    conn.commit()
    return True


def main():
    print("=" * 60)
    print("  LA BAITA — Scraping Ristoranti Campania")
    print("=" * 60)

    conn = get_db()
    totale_nuovi = 0
    totale_duplicati = 0

    for citta in ZONE_CAMPANIA:
        print(f"\n CITTA': {citta}")
        citta_nuovi = 0

        for tipo in QUERIES_RISTORANTE:
            places = cerca_ristoranti(tipo, citta)
            nuovi = 0
            for p in places:
                if salva_ristorante(conn, p, citta):
                    nuovi += 1
                    totale_nuovi += 1
                else:
                    totale_duplicati += 1

            print(f"   {tipo}: {len(places)} trovati, {nuovi} nuovi")
            citta_nuovi += nuovi
            time.sleep(0.5)  # rispetta rate limit API

        print(f"   => Totale nuovi per {citta}: {citta_nuovi}")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  COMPLETATO!")
    print(f"  Nuovi ristoranti salvati: {totale_nuovi}")
    print(f"  Duplicati saltati:        {totale_duplicati}")
    print("=" * 60)

    # Riepilogo finale
    conn2 = sqlite3.connect("leads.db")
    cur = conn2.cursor()
    cur.execute("SELECT COUNT(*) FROM leads WHERE categoria = 'ristorante'")
    tot = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE categoria = 'ristorante' AND sito_web != ''")
    con_sito = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE categoria = 'ristorante' AND email != ''")
    con_email = cur.fetchone()[0]
    conn2.close()

    print(f"\n  TOTALE RISTORANTI NEL DB: {tot}")
    print(f"  Con sito web:             {con_sito}")
    print(f"  Con email:                {con_email}")


if __name__ == "__main__":
    main()
