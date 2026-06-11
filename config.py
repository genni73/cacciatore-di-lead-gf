import os

# API Keys (lette dalle variabili d'ambiente di Render)
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
WA_TOKEN = os.environ.get("WA_TOKEN", "")
WA_INSTANCE_ID = os.environ.get("WA_INSTANCE_ID", "")
WA_API_URL = os.environ.get("WA_API_URL", f"https://api.ultramsg.com/{os.environ.get('WA_INSTANCE_ID', '')}/messages/chat")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
FULLBOOKING_BASE_URL = os.environ.get("FULLBOOKING_BASE_URL", "https://fullbooking.cloud")

# Dati aziendali
NOME_AZIENDA = os.environ.get("NOME_AZIENDA", "GF Technological System")
NOME_VENDITORE = os.environ.get("NOME_VENDITORE", "Gennaro Fusco")
TELEFONO = os.environ.get("TELEFONO", "+39 388 884 2343")
SITO_WEB = os.environ.get("SITO_WEB", "casseautomaticheperildenaro.it")

# Zone Campania
ZONE_CAMPANIA = [
    "Napoli", "Salerno", "Caserta", "Benevento", "Avellino",
    "Pozzuoli", "Torre del Greco", "Giugliano in Campania",
    "Castellammare di Stabia", "Afragola", "Ercolano",
    "Portici", "Scafati", "Battipaglia", "Cava de' Tirreni",
    "Marano di Napoli", "Acerra", "Nola", "Nocera Inferiore",
    "Aversa", "Marcianise", "Casal di Principe", "Pompei",
    "Torre Annunziata", "Sorrento", "Pagani", "Sarno"
]

# Categorie con template messaggi personalizzati
CATEGORIE = {
    "farmacia": {
        "query_google": "farmacia",
        "emoji": "💊",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Sa cosa sta perdendo ogni giorno senza una cassa automatica?\n"
            "Tempo, soldi e clienti — mentre i suoi concorrenti gia si aggiornano.\n\n"
            "La buona notizia: con il Piano Transizione 5.0 del Governo, "
            "la sua farmacia recupera fino al 45% del costo come CREDITO FISCALE IMMEDIATO.\n\n"
            "Esempio reale:\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "Incluso nel pacchetto:\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Addio ammanchi e errori di cassa\n"
            "Velocita doppia ai pagamenti\n"
            "Assistenza diretta a Napoli — non un call center\n\n"
            "Offerta valida per pochi posti in Campania.\n"
            "Posso mostrarle tutto dal vivo GRATIS questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Farmacie - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La nostra cassa automatica Cashmatic e' la soluzione ideale per le farmacie:\n"
            "Elimina gli errori di cassa\n"
            "Velocizza i pagamenti del 40%\n"
            "Riduce i rischi di gestione del contante\n"
            "Piano Transizione 5.0 — recupera fino al 45% come credito fiscale\n"
            "Esempio: Cashmatic 460 da 6.000 euro, costo finale SOLO 3.300 euro\n\n"
            "Posso fissare un appuntamento per una demo gratuita direttamente in farmacia?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "tabaccheria": {
        "query_google": "tabaccheria",
        "emoji": "🚬",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Sa cosa sta perdendo ogni giorno senza una cassa automatica?\n"
            "Tempo, soldi e clienti — mentre i suoi concorrenti gia si aggiornano.\n\n"
            "La buona notizia: con il Piano Transizione 5.0 del Governo, "
            "la sua tabaccheria recupera fino al 45% del costo come CREDITO FISCALE IMMEDIATO.\n\n"
            "Esempio reale:\n"
            "Cassa Cashmatic: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "Incluso nel pacchetto:\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Addio ammanchi e errori di cassa\n"
            "Gestione automatica tabacchi e gratta e vinci\n"
            "Assistenza diretta a Napoli — non un call center\n\n"
            "Offerta valida per pochi posti in Campania.\n"
            "Posso mostrarle tutto dal vivo GRATIS questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Tabaccherie - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Il Cashmatic e' la cassa automatica ideale per le tabaccherie:\n"
            "Gestione automatica del contante e resto\n"
            "Zero errori di cassa\n"
            "Code piu veloci = piu clienti serviti\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n"
            "Esempio: Cashmatic da 6.000 euro, costo finale SOLO 3.300 euro\n\n"
            "Possiamo fissare una demo gratuita?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "bar": {
        "query_google": "bar caffetteria",
        "emoji": "☕",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Sa cosa sta perdendo ogni giorno senza una cassa automatica?\n"
            "Tempo, soldi e clienti — mentre i suoi concorrenti gia si aggiornano.\n\n"
            "La buona notizia: con il Piano Transizione 5.0 del Governo, "
            "il suo bar recupera fino al 45% del costo come CREDITO FISCALE IMMEDIATO.\n\n"
            "Esempio reale:\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "Incluso nel pacchetto:\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Il cliente paga da solo — zero errori\n"
            "Piu velocita nelle ore di punta\n"
            "Assistenza diretta a Napoli — non un call center\n\n"
            "Offerta valida per pochi posti in Campania.\n"
            "Posso mostrarle tutto dal vivo GRATIS questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Bar - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Nei bar il contante e' ancora il re — il Cashmatic lo gestisce in automatico:\n"
            "Il cliente inserisce i soldi, il sistema da' il resto automaticamente\n"
            "Niente piu errori o ammanchi\n"
            "Il personale puo concentrarsi sul servizio\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n"
            "Esempio: Cashmatic 460 da 6.000 euro, costo finale SOLO 3.300 euro\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "ristorante": {
        "query_google": "ristorante pizzeria",
        "emoji": "🍕",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Sa cosa sta perdendo ogni giorno senza una cassa automatica?\n"
            "Tempo, soldi e clienti — mentre i suoi concorrenti gia si aggiornano.\n\n"
            "La buona notizia: con il Piano Transizione 5.0 del Governo, "
            "il suo ristorante recupera fino al 45% del costo come CREDITO FISCALE IMMEDIATO.\n\n"
            "Esempio reale:\n"
            "Cassa Cashmatic 860: 7.000 euro\n"
            "Credito Transizione 5.0: - 3.150 euro\n"
            "Costo finale: SOLO 3.850 euro\n\n"
            "Incluso nel pacchetto:\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Addio ammanchi e errori di cassa\n"
            "Zero attese — piu tavoli serviti\n"
            "Assistenza diretta a Napoli — non un call center\n\n"
            "Offerta valida per pochi posti in Campania.\n"
            "Posso mostrarle tutto dal vivo GRATIS questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Ristoranti - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Il Cashmatic e' la soluzione ideale per ristoranti e pizzerie:\n"
            "Pagamenti al tavolo o alla cassa automatizzati\n"
            "Elimina code e attese\n"
            "Rendicontazione automatica fine giornata\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n"
            "Esempio: Cashmatic 860 da 7.000 euro, costo finale SOLO 3.850 euro\n\n"
            "Fissiamo una demo gratuita?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "supermercato": {
        "query_google": "supermercato alimentari",
        "emoji": "🛒",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Sa cosa sta perdendo ogni giorno senza una cassa automatica?\n"
            "Tempo, soldi e clienti — mentre i suoi concorrenti gia si aggiornano.\n\n"
            "La buona notizia: con il Piano Transizione 5.0 del Governo, "
            "il suo negozio recupera fino al 45% del costo come CREDITO FISCALE IMMEDIATO.\n\n"
            "Esempio reale:\n"
            "Cassa Cashmatic 1060: 8.000 euro\n"
            "Credito Transizione 5.0: - 3.600 euro\n"
            "Costo finale: SOLO 4.400 euro\n\n"
            "Incluso nel pacchetto:\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Self-checkout automatico — code eliminate\n"
            "Addio ammanchi e errori di cassa\n"
            "Assistenza diretta a Napoli — non un call center\n\n"
            "Offerta valida per pochi posti in Campania.\n"
            "Posso mostrarle tutto dal vivo GRATIS questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Self-Service per Supermercati - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La nostra cassa automatica SelfPay e' pensata per supermercati e negozi:\n"
            "Self-checkout completo con gestione contante\n"
            "Riduzione del personale alla cassa\n"
            "Code eliminate\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n"
            "Esempio: Cashmatic 1060 da 8.000 euro, costo finale SOLO 4.400 euro\n\n"
            "Possiamo organizzare una demo gratuita?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "gelateria": {
        "query_google": "gelateria pasticceria",
        "emoji": "🍦",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Due soluzioni su misura per la sua gelateria:\n\n"
            "ACQUISTO con incentivo:\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "NOLEGGIO TOTEM (zero anticipo):\n"
            "Totem self-order + cassa automatica\n"
            "Canone mensile fisso — nessuna spesa iniziale\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Assistenza diretta a Napoli\n\n"
            "Posti limitati in Campania.\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica e Totem per Gelaterie - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Due soluzioni per la sua gelateria:\n"
            "ACQUISTO: Cashmatic 460 con credito fiscale fino al 45%, costo finale da 3.300 euro\n"
            "NOLEGGIO TOTEM: zero anticipo, canone mensile fisso, software incluso GRATIS\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "hotel": {
        "query_google": "hotel albergo bed breakfast",
        "emoji": "🏨",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo, il suo hotel recupera fino al 45%:\n\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Check-in e pagamenti automatizzati\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Hotel - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Il Cashmatic e' perfetto per hotel e strutture ricettive:\n"
            "Check-in/check-out automatizzato\n"
            "Gestione caparre e pagamenti sicura\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n"
            "Esempio: Cashmatic 460 da 6.000 euro, costo finale SOLO 3.300 euro\n\n"
            "Possiamo fissare una demo?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "parrucchiere": {
        "query_google": "parrucchiere barbiere salone",
        "emoji": "💇",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo, il suo salone recupera fino al 45%:\n\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Addio ammanchi e errori di cassa\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Saloni - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "Per saloni e barberie il Cashmatic semplifica tutto:\n"
            "Gestione automatica del contante\n"
            "Niente piu errori di resto\n"
            "Rendiconto giornaliero automatico\n"
            "Piano Transizione 5.0 — credito fiscale fino al 45%\n\n"
            "Demo gratuita?\n\n"
            "Cordialmente,\n"
            "Gennaro Fusco\n"
            "GF Technological System\n"
            "Tel: +39 388 884 2343\n"
            "casseautomaticheperildenaro.it"
        )
    },
    "palestra": {
        "query_google": "palestra fitness centro sportivo",
        "emoji": "💪",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo recupera fino al 45% del costo:\n\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Incassi automatici — zero ammanchi\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Palestre - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La Cashmatic 460 e' la soluzione ideale per palestre e centri fitness:\n"
            "Gestione automatica abbonamenti e ingressi\n"
            "Zero errori e ammanchi\n"
            "Software gestionale incluso GRATIS\n"
            "Credito d'imposta Transizione 5.0 fino al 45%\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Gennaro Fusco | GF Technological System\n"
            "Tel: +39 388 884 2343 | casseautomaticheperildenaro.it"
        )
    },
    "estetica": {
        "query_google": "centro estetico estetista beauty",
        "emoji": "💅",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo recupera fino al 45% del costo:\n\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Pagamenti automatici — lei pensa ai clienti\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Centri Estetici - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La Cashmatic 460 per centri estetici:\n"
            "Gestione automatica pagamenti\n"
            "Zero errori di cassa\n"
            "Software gestionale incluso GRATIS\n"
            "Credito d'imposta Transizione 5.0 fino al 45%\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Gennaro Fusco | GF Technological System\n"
            "Tel: +39 388 884 2343 | casseautomaticheperildenaro.it"
        )
    },
    "veterinario": {
        "query_google": "veterinario clinica veterinaria",
        "emoji": "🐾",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo recupera fino al 45% del costo:\n\n"
            "Cassa Cashmatic 460: 6.000 euro\n"
            "Credito Transizione 5.0: - 2.700 euro\n"
            "Costo finale: SOLO 3.300 euro\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Incassi automatici e sicuri\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Veterinari - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La Cashmatic 460 per studi veterinari:\n"
            "Gestione automatica incassi e pagamenti\n"
            "Zero errori e ammanchi\n"
            "Software gestionale incluso GRATIS\n"
            "Credito d'imposta Transizione 5.0 fino al 45%\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Gennaro Fusco | GF Technological System\n"
            "Tel: +39 388 884 2343 | casseautomaticheperildenaro.it"
        )
    },
    "caseificio": {
        "query_google": "caseificio latteria prodotti caseari",
        "emoji": "🧀",
        "template_whatsapp": (
            "Buongiorno! Sono Gennaro Fusco, partner esclusivo Cashmatic per Napoli e Campania.\n\n"
            "Con il Piano Transizione 5.0 del Governo recupera fino al 45% del costo:\n\n"
            "Cassa Cashmatic 860/1060: da 7.000 euro\n"
            "Credito Transizione 5.0: - fino a 3.150 euro\n"
            "Costo finale: MENO DELLA META'\n\n"
            "SOFTWARE GESTIONALE GRATIS (valore 1.500 euro)\n"
            "Gestione automatica vendita diretta e ingrosso\n"
            "Assistenza diretta a Napoli\n\n"
            "Demo GRATUITA questa settimana?\n\n"
            "Gennaro Fusco | GF Technological System | {telefono}"
        ),
        "template_email_oggetto": "Cassa Automatica per Caseifici - GF Technological System Napoli",
        "template_email_corpo": (
            "Gentile {nome_attivita},\n\n"
            "sono Gennaro Fusco di GF Technological System, partner esclusivo Cashmatic "
            "per Napoli e Campania.\n\n"
            "La Cashmatic 860/1060 per caseifici e latterie:\n"
            "Gestione automatica vendita diretta e ingrosso\n"
            "Zero errori su cifre elevate\n"
            "Software gestionale incluso GRATIS\n"
            "Credito d'imposta Transizione 5.0 fino al 45%\n\n"
            "Demo gratuita senza impegno?\n\n"
            "Gennaro Fusco | GF Technological System\n"
            "Tel: +39 388 884 2343 | casseautomaticheperildenaro.it"
        )
    }
}
