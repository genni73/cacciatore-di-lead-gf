"""
LEONARDO — Campagna WhatsApp Full Booking
Invia messaggio personalizzato con link preview a tutti i ristoranti target.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, requests, time, os
from config import WA_TOKEN, WA_INSTANCE_ID, WA_API_URL

# ── CONFIGURAZIONE ────────────────────────────────────────────
NGROK_URL = os.environ.get("NGROK_URL", "https://feel-scribing-wildly.ngrok-free.dev")
PAUSA_TRA_MESSAGGI = 8  # secondi tra un messaggio e l'altro (anti-spam)
DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")


def pulisci_numero(numero: str) -> str:
    """Converte numero in formato internazionale senza +."""
    numero = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
    if numero.startswith("039"):
        numero = "39" + numero[3:]
    elif numero.startswith("0"):
        numero = "39" + numero[1:]
    elif not numero.startswith("39"):
        numero = "39" + numero
    return numero


def componi_messaggio(nome_ristorante: str, preview_url: str) -> str:
    """Compone il messaggio WhatsApp personalizzato."""
    # Pulisce il nome (rimuove stuff tra parentesi e pipe)
    nome_pulito = nome_ristorante.split("|")[0].split("(")[0].strip()

    return (
        f"Ciao! Sono Leonardo di *Full Booking* 🍽️\n\n"
        f"Ho creato una *demo gratuita* per *{nome_pulito}*: "
        f"un sistema di prenotazione online completo con:\n\n"
        f"✅ Modulo prenotazioni sul tuo sito\n"
        f"✅ Conferma automatica via WhatsApp e Email\n"
        f"✅ Centralino virtuale con risposta h24\n"
        f"✅ Gestione tavoli in tempo reale\n\n"
        f"👉 Guarda la tua demo personalizzata:\n"
        f"{preview_url}\n\n"
        f"A partire da *€69/mese* — nessun vincolo, attivazione immediata.\n\n"
        f"Ti interessa? Possiamo parlarne 😊"
    )


def invia_whatsapp(numero: str, messaggio: str) -> bool:
    """Invia messaggio WhatsApp via UltraMsg."""
    numero_pulito = pulisci_numero(numero)
    payload = {
        "token": WA_TOKEN,
        "to": f"+{numero_pulito}",
        "body": messaggio,
        "priority": 10
    }
    try:
        resp = requests.post(WA_API_URL, data=payload, timeout=15)
        data = resp.json()
        return data.get("sent") == "true" or data.get("sent") is True
    except Exception as e:
        print(f"   Errore: {e}")
        return False


def lancia_campagna(limite: int = 50, solo_mobile: bool = True, test_numero: str = None):
    """
    Lancia la campagna WhatsApp Full Booking.
    Usa URL con token (/p/xK9mQ) — nessun nome visibile nel link.

    Args:
        limite: numero massimo di messaggi da inviare
        solo_mobile: se True, invia solo a numeri cellulare (3xx)
        test_numero: se impostato, invia TUTTI i messaggi a questo numero (modalità test)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Query: lead con preview E token generato, non ancora contattati per FB
    # Prima i numeri mobile (3xx), poi i fissi — massima copertura
    query = """
        SELECT id, nome, citta, telefono, note, fb_token
        FROM leads
        WHERE note LIKE 'FB:preview:%'
        AND (note NOT LIKE 'FB:inviato%')
        AND telefono IS NOT NULL AND telefono != ''
        AND fb_token IS NOT NULL AND fb_token != ''
        ORDER BY
          CASE WHEN telefono LIKE '3%' OR telefono LIKE '+39 3%' OR telefono LIKE '393%' THEN 0 ELSE 1 END,
          id
    """ + f" LIMIT {limite}"
    leads = conn.execute(query).fetchall()

    print(f"\n{'='*65}")
    print(f"  CAMPAGNA FULL BOOKING — {len(leads)} messaggi da inviare")
    if test_numero:
        print(f"  *** MODALITA' TEST — tutti i messaggi vanno a {test_numero} ***")
    print(f"  Base URL: {NGROK_URL}")
    print(f"{'='*65}\n")

    inviati = 0
    errori = 0

    for i, lead in enumerate(leads, 1):
        token = lead["fb_token"]
        # URL con token — nessun nome visibile
        preview_url = f"{NGROK_URL}/p/{token}"

        nome = lead["nome"]
        telefono = lead["telefono"]
        nota = lead["note"]
        filename = nota.replace("FB:preview:", "")
        destinatario = test_numero if test_numero else telefono

        messaggio = componi_messaggio(nome, preview_url)

        print(f"[{i:3d}/{len(leads)}] {nome[:40]:<40} {telefono}", end=" ... ", flush=True)

        ok = invia_whatsapp(destinatario, messaggio)

        if ok:
            print(f"OK ({NGROK_URL}/p/{token})")
            inviati += 1
            # Aggiorna DB: marcalo come inviato
            if not test_numero:
                conn.execute(
                    "UPDATE leads SET note = ?, stato = ? WHERE id = ?",
                    (f"FB:inviato:{filename}", "contattato", lead["id"])
                )
                conn.commit()
        else:
            print("ERRORE")
            errori += 1

        time.sleep(PAUSA_TRA_MESSAGGI)

    conn.close()

    print(f"\n{'='*65}")
    print(f"  RISULTATO: {inviati} inviati | {errori} errori")
    print(f"{'='*65}\n")
    return inviati


def stato_campagna():
    """Mostra lo stato attuale della campagna."""
    conn = sqlite3.connect(DB_PATH)
    totale_preview = conn.execute("SELECT COUNT(*) FROM leads WHERE note LIKE 'FB:preview:%'").fetchone()[0]
    gia_inviati = conn.execute("SELECT COUNT(*) FROM leads WHERE note LIKE 'FB:inviato:%'").fetchone()[0]
    da_inviare_mobile = conn.execute("""
        SELECT COUNT(*) FROM leads
        WHERE note LIKE 'FB:preview:%'
        AND (telefono LIKE '3%' OR telefono LIKE '+39 3%' OR telefono LIKE '393%')
    """).fetchone()[0]
    in_generazione = conn.execute("SELECT COUNT(*) FROM leads WHERE note='LABAITA:target'").fetchone()[0]
    conn.close()

    print(f"\n{'='*50}")
    print(f"  STATO CAMPAGNA FULL BOOKING")
    print(f"{'='*50}")
    print(f"  Preview generate:      {totale_preview}")
    print(f"  Messaggi gia inviati:  {gia_inviati}")
    print(f"  Da inviare (mobile):   {da_inviare_mobile}")
    print(f"  Ancora in generazione: {in_generazione}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        stato_campagna()
        print("Uso:")
        print("  python campagna_fullbooking.py stato")
        print("  python campagna_fullbooking.py test +39XXXXXXXXXX")
        print("  python campagna_fullbooking.py invia [limite]")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "stato":
        stato_campagna()

    elif cmd == "test":
        numero = sys.argv[2] if len(sys.argv) > 2 else "+393888842343"
        print(f"\nTest su: {numero}")
        # Prende il primo lead con preview
        conn = sqlite3.connect(DB_PATH)
        lead = conn.execute("""
            SELECT id, nome, citta, telefono, note FROM leads
            WHERE note LIKE 'FB:preview:%' LIMIT 1
        """).fetchone()
        conn.close()
        if lead:
            nota = lead[4]
            filename = nota.replace("FB:preview:", "")
            slug = filename.replace(".html", "")
            preview_url = f"{NGROK_URL}/preview/{slug}"
            msg = componi_messaggio(lead[1], preview_url)
            print("\n=== ANTEPRIMA MESSAGGIO ===")
            print(msg)
            print(f"\nLink: {preview_url}")
            print("===========================\n")
            ok = invia_whatsapp(numero, msg)
            print(f"Invio: {'OK' if ok else 'ERRORE'}")

    elif cmd == "invia":
        limite = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        forza = "--si" in sys.argv
        if not forza:
            conferma = input(f"\nConfermi invio a {limite} ristoranti? (si/no): ")
            forza = conferma.lower() == "si"
        if forza:
            lancia_campagna(limite=limite, solo_mobile=False)
        else:
            print("Annullato.")

    else:
        print(f"Comando sconosciuto: {cmd}")
