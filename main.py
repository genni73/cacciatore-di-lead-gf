#!/usr/bin/env python3
# ============================================================
#  GF LEAD HUNTER v1.0
#  GF Technological System | Gennaro Fusco | Napoli
#  Partner Esclusivo Cashmatic per Campania
# ============================================================
import sys
import webbrowser
import threading
import time

from database import init_db, get_stats
from config import GOOGLE_MAPS_API_KEY


def banner():
    print("=" * 55)
    print("  GF LEAD HUNTER v1.0")
    print("  GF Technological System | Napoli")
    print("  Partner Esclusivo Cashmatic Campania")
    print("=" * 55)


def check_config():
    if GOOGLE_MAPS_API_KEY == "INSERISCI_QUI_LA_TUA_API_KEY":
        print("⚠️  ATTENZIONE: API Key Google Maps non configurata!")
        print("   Apri config.py e inserisci la tua API Key")
        print("   (La ricerca automatica non funzionerà)\n")
        return False
    return True


def stampa_stats():
    stats = get_stats()
    print(f"""
📊 STATISTICHE ATTUALI:
   Lead totali:    {stats['totale']}
   Nuovi:          {stats['nuovi']}
   Contattati:     {stats['contattati']}
   Interessati:    {stats['interessati']}
   Clienti 💰:     {stats['clienti']}
   Con telefono:   {stats['con_telefono']}
   Con email:      {stats['con_email']}
   Messaggi inv.:  {stats['messaggi_inviati']}
""")


def main():
    banner()
    init_db()

    if len(sys.argv) < 2:
        print("📋 COMANDI DISPONIBILI:")
        print()
        print("  python main.py dashboard          → Apre dashboard web (raccomandato)")
        print("  python main.py search             → Cerca lead (tutta Campania)")
        print("  python main.py search farmacia    → Cerca farmacie in Campania")
        print("  python main.py search bar Napoli  → Cerca bar a Napoli")
        print("  python main.py enrich             → Cerca email dai siti web")
        print("  python main.py whatsapp           → Invia WhatsApp ai nuovi lead")
        print("  python main.py email              → Invia email ai nuovi lead")
        print("  python main.py stats              → Mostra statistiche")
        print()
        stampa_stats()
        return

    cmd = sys.argv[1].lower()

    # ── DASHBOARD ─────────────────────────────────────────
    if cmd == "dashboard":
        from dashboard import avvia_dashboard
        check_config()
        stampa_stats()
        def apri_browser():
            time.sleep(1.5)
            webbrowser.open("http://localhost:5000")
        threading.Thread(target=apri_browser, daemon=True).start()
        avvia_dashboard()

    # ── RICERCA LEAD ──────────────────────────────────────
    elif cmd == "search":
        if not check_config():
            return
        from scraper import scrape_categoria_citta, scrape_tutto
        from config import CATEGORIE, ZONE_CAMPANIA

        categoria = sys.argv[2] if len(sys.argv) > 2 else None
        citta = sys.argv[3] if len(sys.argv) > 3 else None

        if categoria and citta:
            if categoria not in CATEGORIE:
                print(f"❌ Categoria non valida. Disponibili: {', '.join(CATEGORIE.keys())}")
                return
            trovati = scrape_categoria_citta(categoria, citta)
            print(f"\n✅ Trovati {trovati} nuovi lead")

        elif categoria:
            if categoria not in CATEGORIE:
                print(f"❌ Categoria non valida. Disponibili: {', '.join(CATEGORIE.keys())}")
                return
            print(f"🔍 Cerco '{categoria}' in tutta la Campania...")
            totale = 0
            for c in ZONE_CAMPANIA:
                totale += scrape_categoria_citta(categoria, c)
            print(f"\n✅ Totale: {totale} nuovi lead per '{categoria}'")

        else:
            print("🚀 Avvio ricerca completa (tutte le categorie, tutta la Campania)...")
            print("⚠️  Operazione lunga — ci vorrà qualche ora. Premi Ctrl+C per fermare.\n")
            scrape_tutto()

        stampa_stats()

    # ── ARRICCHIMENTO EMAIL ───────────────────────────────
    elif cmd == "enrich":
        from enricher import arricchisci_tutti
        arricchisci_tutti()
        stampa_stats()

    # ── CAMPAGNA WHATSAPP ─────────────────────────────────
    elif cmd == "whatsapp":
        from outreach import campagna_whatsapp
        categoria = sys.argv[2] if len(sys.argv) > 2 else None
        citta = sys.argv[3] if len(sys.argv) > 3 else None
        limite = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        campagna_whatsapp(categoria=categoria, citta=citta, limite=limite)
        stampa_stats()

    # ── CAMPAGNA EMAIL ─────────────────────────────────────
    elif cmd == "email":
        from outreach import campagna_email
        categoria = sys.argv[2] if len(sys.argv) > 2 else None
        citta = sys.argv[3] if len(sys.argv) > 3 else None
        limite = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        campagna_email(categoria=categoria, citta=citta, limite=limite)
        stampa_stats()

    # ── STATS ─────────────────────────────────────────────
    elif cmd == "stats":
        stampa_stats()
        stats = get_stats()
        if stats['per_categoria']:
            print("📊 Lead per categoria:")
            for row in stats['per_categoria']:
                print(f"   {row[0]:<20} {row[1]} lead")
        if stats['per_citta']:
            print("\n📍 Top città:")
            for row in stats['per_citta']:
                print(f"   {row[0]:<25} {row[1]} lead")

    else:
        print(f"❌ Comando '{cmd}' non riconosciuto. Usa: dashboard | search | enrich | whatsapp | email | stats")


if __name__ == "__main__":
    main()
