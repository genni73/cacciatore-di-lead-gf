# ============================================================
#  GF LEAD HUNTER — Configurazione (ESEMPIO)
#  Copia questo file in config.py e inserisci i tuoi dati
# ============================================================

# Google Maps / Places API
GOOGLE_MAPS_API_KEY = "LA_TUA_API_KEY_GOOGLE"

# Make.com webhook (per Facebook posts)
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/IL_TUO_WEBHOOK"

# WhatsApp via UltraMsg
WA_TOKEN = "IL_TUO_TOKEN_ULTRAMSG"
WA_INSTANCE_ID = "instanceXXXXXX"
WA_API_URL = f"https://api.ultramsg.com/{WA_INSTANCE_ID}/messages/chat"

# Gmail per invio email
GMAIL_USER = "la.tua@email.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"

# Dati azienda
NOME_AZIENDA = "GF Technological System"
NOME_VENDITORE = "Leonardo"
TELEFONO = "+39 388 884 2343"

# Categorie con template messaggi
CATEGORIE = {
    "ristorante": {
        "emoji": "🍽️",
        "template_whatsapp": "...",
        "template_email_oggetto": "...",
        "template_email_corpo": "...",
    },
    # Aggiungi altre categorie...
}

ZONE_CAMPANIA = [
    "Napoli", "Salerno", "Caserta", "Avellino", "Benevento",
    # Aggiungi altre città...
]
