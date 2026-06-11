import os

# API Keys (lette dalle variabili d'ambiente di Render)
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
WA_TOKEN = os.environ.get("WA_TOKEN", "")
WA_INSTANCE_ID = os.environ.get("WA_INSTANCE_ID", "")
WA_API_URL = os.environ.get("WA_API_URL", "https://api.ultramsg.com")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# Dati aziendali
NOME_AZIENDA = os.environ.get("NOME_AZIENDA", "GF Technological System")
NOME_VENDITORE = os.environ.get("NOME_VENDITORE", "Gennaro Fusco")
TELEFONO = os.environ.get("TELEFONO", "+39 388 884 2343")
FULLBOOKING_BASE_URL = os.environ.get("FULLBOOKING_BASE_URL", "https://www.fullbooking.it")

# Categorie lead
CATEGORIE = {
    "ristorante": {
        "emoji": "🍽️",
        "label": "Ristorante",
        "wa_template": "Buongiorno! Sono {venditore} di {azienda}. Ho visto il vostro ristorante e volevo presentarvi la nostra soluzione...",
        "email_oggetto": "Proposta per {nome}",
        "email_corpo": "Gentile titolare,\n\nSono {venditore} di {azienda}..."
    },
    "pizzeria": {
        "emoji": "🍕",
        "label": "Pizzeria",
        "wa_template": "Buongiorno! Sono {venditore} di {azienda}. Ho visto la vostra pizzeria e volevo presentarvi la nostra soluzione...",
        "email_oggetto": "Proposta per {nome}",
        "email_corpo": "Gentile titolare,\n\nSono {venditore} di {azienda}..."
    },
    "bar": {
        "emoji": "☕",
        "label": "Bar",
        "wa_template": "Buongiorno! Sono {venditore} di {azienda}. Ho visto il vostro bar e volevo presentarvi la nostra soluzione...",
        "email_oggetto": "Proposta per {nome}",
        "email_corpo": "Gentile titolare,\n\nSono {venditore} di {azienda}..."
    },
    "hotel": {
        "emoji": "🏨",
        "label": "Hotel",
        "wa_template": "Buongiorno! Sono {venditore} di {azienda}. Ho visto il vostro hotel e volevo presentarvi la nostra soluzione...",
        "email_oggetto": "Proposta per {nome}",
        "email_corpo": "Gentile titolare,\n\nSono {venditore} di {azienda}..."
    },
}

# Zone Campania
ZONE_CAMPANIA = [
    "Napoli", "Salerno", "Caserta", "Benevento", "Avellino",
    "Pozzuoli", "Torre del Greco", "Castellammare di Stabia",
    "Sorrento", "Amalfi", "Positano", "Pompei", "Ercolano",
    "Portici", "San Giorgio a Cremano", "Giugliano in Campania",
    "Afragola", "Acerra", "Nola", "Nocera Inferiore",
    "Battipaglia", "Eboli", "Paestum", "Agropoli"
]
