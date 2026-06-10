# ============================================================
#  GF LEAD HUNTER — Invio WhatsApp + Email
# ============================================================
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import (MAKE_WEBHOOK_URL, GMAIL_USER, GMAIL_APP_PASSWORD,
                    NOME_AZIENDA, NOME_VENDITORE, TELEFONO, CATEGORIE,
                    WA_TOKEN, WA_API_URL, WA_INSTANCE_ID, FULLBOOKING_BASE_URL)
from database import get_leads, aggiorna_stato, salva_messaggio


# ─── WhatsApp via UltraMsg ────────────────────────────────────────────────────

# Immagini prodotti per categoria
IMG_460  = "https://cashmatic.it/wp-content/uploads/2026/01/460-1.png"
IMG_860  = "https://cashmatic.it/wp-content/uploads/2026/02/image-16.png"
IMG_1060 = "https://cashmatic.it/wp-content/uploads/2026/02/image-17.png"

IMMAGINI_CATEGORIA = {
    "farmacia":        IMG_460,
    "tabaccheria":     IMG_1060,
    "bar":             IMG_460,
    "ristorante":      IMG_860,
    "supermercato":    IMG_1060,
    "gelateria":       IMG_460,
    "hotel":           IMG_460,
    "parrucchiere":    IMG_460,
    "palestra":        IMG_460,
    "estetica":        IMG_460,
    "veterinario":     IMG_460,
    "caseificio":      IMG_860,
}

SITO_WEB = "https://casseautomaticheperildenaro.it"


def pulisci_numero(numero: str) -> str:
    """Converte il numero in formato internazionale."""
    numero = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
    if numero.startswith("039"):
        numero = "39" + numero[3:]
    elif numero.startswith("0"):
        numero = "39" + numero[1:]
    elif not numero.startswith("39"):
        numero = "39" + numero
    return numero


def invia_whatsapp(numero: str, messaggio: str, immagine_url: str = None) -> bool:
    """Invia messaggio WhatsApp via UltraMsg."""
    if not numero:
        return False

    numero = pulisci_numero(numero)

    try:
        # Invia il testo
        payload_testo = {
            "token": WA_TOKEN,
            "to": f"+{numero}",
            "body": messaggio,
            "priority": 10
        }
        resp = requests.post(WA_API_URL, data=payload_testo, timeout=10)
        data = resp.json()

        if data.get("sent") != "true" and data.get("sent") is not True:
            print(f"   Errore WA: {data}")
            return False

        # Poi invia l'immagine se presente
        if immagine_url:
            payload_img = {
                "token": WA_TOKEN,
                "to": f"+{numero}",
                "image": immagine_url,
                "caption": "Scopri il Cashmatic su casseautomaticheperildenaro.it",
                "priority": 10
            }
            img_url = f"https://api.ultramsg.com/{WA_INSTANCE_ID}/messages/image"
            requests.post(img_url, data=payload_img, timeout=10)

        return True

    except Exception as e:
        print(f"   Errore WhatsApp: {e}")
        return False


def invia_whatsapp_lead(lead: dict) -> bool:
    """Compone e invia WhatsApp a un lead specifico."""
    cat = lead.get("categoria")
    config_cat = CATEGORIE.get(cat, {})
    template = config_cat.get("template_whatsapp", "")

    messaggio = template.format(
        nome_attivita=lead.get("nome", ""),
        citta=lead.get("citta", ""),
        telefono=TELEFONO
    )

    # Aggiunge link sito in fondo
    messaggio += f"\n\nScopri di piu': {SITO_WEB}"

    immagine = IMMAGINI_CATEGORIA.get(cat, "")

    ok = invia_whatsapp(lead["telefono"], messaggio, immagine)
    if ok:
        salva_messaggio(lead["id"], "whatsapp", messaggio, "inviato")
        aggiorna_stato(lead["id"], "contattato", "WhatsApp inviato")
    return ok


def invia_test(numero_test: str, categoria: str = "farmacia") -> bool:
    """Manda un messaggio di test al numero indicato per vedere come appare."""
    config_cat = CATEGORIE.get(categoria, {})
    template = config_cat.get("template_whatsapp", "")

    messaggio = template.format(
        nome_attivita="[NOME ATTIVITA']",
        citta="Napoli",
        telefono=TELEFONO
    )
    messaggio += f"\n\nScopri di piu': {SITO_WEB}"
    immagine = IMMAGINI_CATEGORIA.get(categoria, "")

    print("\n" + "=" * 50)
    print("ANTEPRIMA MESSAGGIO WhatsApp:")
    print("=" * 50)
    print(messaggio)
    print(f"\nImmagine allegata: {immagine}")
    print("=" * 50)

    ok = invia_whatsapp(numero_test, messaggio, immagine)
    if ok:
        print(f"TEST INVIATO a {numero_test}!")
    else:
        print(f"Errore invio test a {numero_test}")
    return ok


# ─── Email via Gmail SMTP ────────────────────────────────────────────────────

import os as _os
BROCHURE_PDF = _os.path.join(_os.path.dirname(__file__), "brochure.pdf")


def invia_email(destinatario: str, oggetto: str, corpo: str) -> bool:
    """Invia una email via Gmail SMTP con brochure allegata."""
    if not destinatario:
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"] = oggetto
    msg["From"] = f"{NOME_AZIENDA} <{GMAIL_USER}>"
    msg["To"] = destinatario

    # Parte testo + HTML
    parte_alternativa = MIMEMultipart("alternative")

    # Versione testo
    parte_alternativa.attach(MIMEText(corpo, "plain", "utf-8"))

    # Versione HTML
    corpo_html = corpo.replace("\n", "<br>")
    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; max-width: 600px;">
        <div style="border-left: 4px solid #1a8fff; padding-left: 16px; margin-bottom: 20px;">
            <h2 style="color: #1a8fff; margin: 0;">GF Technological System</h2>
            <p style="margin: 4px 0; color: #666;">Partner Esclusivo Cashmatic | Napoli e Campania</p>
        </div>
        <div style="line-height: 1.8;">{corpo_html}</div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="font-size: 12px; color: #999;">
            GF Technological System | {TELEFONO} | {GMAIL_USER}<br>
            <a href="https://casseautomaticheperildenaro.it" style="color: #1a8fff;">casseautomaticheperildenaro.it</a>
        </p>
    </body></html>
    """
    parte_alternativa.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(parte_alternativa)

    # Allegato PDF brochure
    if os.path.exists(BROCHURE_PDF):
        with open(BROCHURE_PDF, "rb") as f:
            allegato = MIMEBase("application", "pdf")
            allegato.set_payload(f.read())
            encoders.encode_base64(allegato)
            allegato.add_header(
                "Content-Disposition",
                "attachment",
                filename="Cashmatic_GF_Technological_System.pdf"
            )
            msg.attach(allegato)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        return True
    except Exception as e:
        print(f"   ⚠️  Errore email: {e}")
        return False


def invia_email_lead(lead: dict) -> bool:
    """Compone e invia email a un lead specifico."""
    cat = lead.get("categoria")
    config_cat = CATEGORIE.get(cat, {})

    oggetto = config_cat.get("template_email_oggetto", f"Casse Automatiche - {NOME_AZIENDA}")
    corpo = config_cat.get("template_email_corpo", "").format(
        nome_attivita=lead.get("nome", ""),
        citta=lead.get("citta", ""),
        telefono=TELEFONO
    )

    ok = invia_email(lead["email"], oggetto, corpo)
    if ok:
        salva_messaggio(lead["id"], "email", corpo, "inviato")
        aggiorna_stato(lead["id"], "contattato", "Email inviata")
    return ok


# ─── Campagne di massa ───────────────────────────────────────────────────────

def campagna_whatsapp(categoria: str = None, citta: str = None, limite: int = 50):
    """Invia WhatsApp a tutti i lead nuovi con telefono."""
    leads = get_leads(stato="nuovo", categoria=categoria, citta=citta, con_telefono=True)
    leads = leads[:limite]

    print(f"\n📱 CAMPAGNA WHATSAPP — {len(leads)} messaggi da inviare")
    inviati = 0
    errori = 0

    for i, lead in enumerate(leads, 1):
        emoji = CATEGORIE.get(lead["categoria"], {}).get("emoji", "📍")
        print(f"[{i}/{len(leads)}] {emoji} {lead['nome']} ({lead['citta']})...", end=" ")
        ok = invia_whatsapp_lead(lead)
        if ok:
            print("✅ Inviato")
            inviati += 1
        else:
            print("❌ Errore")
            errori += 1

        # Pausa anti-spam
        import time
        time.sleep(3)

    print(f"\n📊 Risultato: {inviati} inviati, {errori} errori")
    return inviati


def campagna_fullbooking_wa(limite: int = 50):
    """
    Invia WhatsApp ai ristoranti che hanno una preview Full Booking generata.
    Il messaggio include il link personalizzato Netlify (sempre online).
    """
    from database import get_conn as _get_conn
    conn = _get_conn()
    rows = conn.execute("""
        SELECT * FROM leads
        WHERE (note LIKE 'FB:preview:%' OR note LIKE 'FB:inviato:%')
        AND telefono IS NOT NULL AND telefono != ''
        AND stato != 'FB:inviato'
        ORDER BY num_recensioni DESC, rating DESC
        LIMIT ?
    """, (limite,)).fetchall()
    conn.close()

    leads_fb = [dict(r) for r in rows]
    print(f"\nCAMPAGNA FULL BOOKING -- {len(leads_fb)} ristoranti da contattare")

    if not leads_fb:
        print("   Nessun lead con preview generata. Esegui prima: python genera_preview_fullbooking.py")
        return 0

    inviati = 0
    errori = 0

    for i, lead in enumerate(leads_fb, 1):
        nome    = lead["nome"]
        citta   = lead["citta"]
        nota    = lead.get("note", "")

        # Estrai il nome del file dalla nota (es: "FB:preview:pizzeria-da-franco.html")
        filename = nota.replace("FB:preview:", "").replace("FB:inviato:", "").strip()
        slug = filename.replace(".html", "")
        link_sito    = f"{FULLBOOKING_BASE_URL}/{slug}"
        link_prenota = f"{FULLBOOKING_BASE_URL}/{slug}-prenota"

        messaggio = (
            f"Buongiorno {nome}!\n\n"
            f"Le facciamo un regalo \U0001f381\n\n"
            f"Abbiamo creato il *sito del suo ristorante* con sistema di prenotazione online -- *completamente gratis*.\n\n"
            f"\U0001f310 Il suo sito:\n"
            f"{link_sito}\n\n"
            f"\U0001f4c5 Prenotazione diretta:\n"
            f"{link_prenota}\n\n"
            f"L'*assistente virtuale Full Booking* risponde ai clienti *al posto suo* -- anche di domenica, anche a mezzanotte.\n"
            f"Nessuna telefonata persa. Nessuna prenotazione mancata.\n\n"
            f"I clienti prenotano in 30 secondi e ricevono conferma immediata su WhatsApp.\n"
            f"*Zero commissioni* -- sempre.\n\n"
            f"Vuole attivarlo per {nome} a {citta}?\n"
            f"La chiamo io personalmente: {TELEFONO}\n\n"
            f"Gennaro Fusco | Full Booking | https://fullbooking.cloud"
        )

        print(f"[{i:3d}/{len(leads_fb)}] {nome[:40]:<40}", end=" ", flush=True)
        ok = invia_whatsapp(lead["telefono"], messaggio)

        if ok:
            print("OK Inviato")
            salva_messaggio(lead["id"], "whatsapp_fb", messaggio, "inviato")
            # Aggiorna nota a FB:inviato per non reinviare
            from database import get_conn as _gc
            c2 = _gc()
            c2.execute("UPDATE leads SET stato='FB:inviato', note=? WHERE id=?",
                       (f"FB:inviato:{filename}", lead["id"]))
            c2.commit()
            c2.close()
            inviati += 1
        else:
            print("ERRORE")
            errori += 1

        import time
        time.sleep(3)

    print(f"\nRisultato Full Booking: {inviati} inviati, {errori} errori")
    return inviati


def campagna_email(categoria: str = None, citta: str = None, limite: int = 100):
    """Invia email a tutti i lead nuovi con email."""
    leads = get_leads(stato="nuovo", categoria=categoria, citta=citta, con_email=True)
    leads = leads[:limite]

    print(f"\n📧 CAMPAGNA EMAIL — {len(leads)} email da inviare")
    inviate = 0
    errori = 0

    for i, lead in enumerate(leads, 1):
        emoji = CATEGORIE.get(lead["categoria"], {}).get("emoji", "📍")
        print(f"[{i}/{len(leads)}] {emoji} {lead['nome']}...", end=" ")
        ok = invia_email_lead(lead)
        if ok:
            print("✅ Inviata")
            inviate += 1
        else:
            print("❌ Errore")
            errori += 1

        import time
        time.sleep(1)

    print(f"\n📊 Risultato: {inviate} inviate, {errori} errori")
    return inviate
