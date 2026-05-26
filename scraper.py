# ============================================================
#  GF LEAD HUNTER — Scraper Google Places API (New)
# ============================================================
import requests
import time
from config import GOOGLE_MAPS_API_KEY, ZONE_CAMPANIA, CATEGORIE
from database import salva_lead

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
    "places.location"
])


def check_api_key():
    if GOOGLE_MAPS_API_KEY == "INSERISCI_QUI_LA_TUA_API_KEY":
        print("❌ ERRORE: Inserisci la tua API Key Google Maps in config.py")
        return False
    return True


def cerca_attivita(categoria: str, citta: str, max_pages: int = 3) -> list:
    """Cerca attività usando Places API (New) Text Search."""
    config_cat = CATEGORIE.get(categoria)
    if not config_cat:
        print(f"❌ Categoria '{categoria}' non trovata")
        return []

    query = f"{config_cat['query_google']} {citta} Campania Italia"
    print(f"\n🔍 Cerco: {query}")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK
    }

    all_places = []
    next_page_token = None

    for page in range(max_pages):
        body = {
            "textQuery": query,
            "languageCode": "it",
            "regionCode": "IT",
            "maxResultCount": 20
        }
        if next_page_token:
            body["pageToken"] = next_page_token
            time.sleep(2)

        try:
            resp = requests.post(PLACES_URL, json=body, headers=headers, timeout=15)
            data = resp.json()

            if "error" in data:
                print(f"   ⚠️  Errore API: {data['error'].get('message', data['error'])}")
                break

            places = data.get("places", [])
            all_places.extend(places)
            print(f"   📍 Pagina {page+1}: {len(places)} risultati (totale: {len(all_places)})")

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        except Exception as e:
            print(f"   ⚠️  Errore richiesta: {e}")
            break

    return all_places


def parse_place(place: dict, categoria: str, citta: str) -> dict:
    """Converte il formato Places API (New) nel formato del nostro DB."""
    return {
        "nome": place.get("displayName", {}).get("text", ""),
        "categoria": categoria,
        "citta": citta,
        "indirizzo": place.get("formattedAddress", ""),
        "telefono": place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber", ""),
        "email": "",
        "sito_web": place.get("websiteUri", ""),
        "rating": place.get("rating"),
        "num_recensioni": place.get("userRatingCount"),
        "place_id": place.get("id", "")
    }


def scrape_categoria_citta(categoria: str, citta: str) -> int:
    """Cerca e salva nel DB tutti i lead per una categoria e città."""
    places = cerca_attivita(categoria, citta)
    salvati = 0
    duplicati = 0

    for place in places:
        lead = parse_place(place, categoria, citta)
        if not lead["nome"]:
            continue

        result = salva_lead(lead)
        if result:
            salvati += 1
            emoji = CATEGORIE[categoria]["emoji"]
            tel = lead['telefono'] or 'no tel'
            print(f"   {emoji} {lead['nome']} — {tel}")
        else:
            duplicati += 1

    print(f"\n✅ {categoria} {citta}: {salvati} nuovi lead, {duplicati} duplicati")
    return salvati


def scrape_tutto(categorie: list = None, zone: list = None):
    """Lancia la ricerca completa per tutte le combinazioni categoria × città."""
    if not check_api_key():
        return 0

    if not categorie:
        categorie = list(CATEGORIE.keys())
    if not zone:
        zone = ZONE_CAMPANIA

    totale = 0
    print(f"\n🚀 GF LEAD HUNTER — Avvio ricerca completa")
    print(f"   Categorie: {', '.join(categorie)}")
    print(f"   Città: {len(zone)}")
    print("=" * 50)

    for cat in categorie:
        for citta in zone:
            trovati = scrape_categoria_citta(cat, citta)
            totale += trovati
            time.sleep(1)

    print(f"\n🎉 RICERCA COMPLETATA! Totale lead trovati: {totale}")
    return totale
