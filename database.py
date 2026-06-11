# ============================================================
#  GF LEAD HUNTER — Database SQLite
# ============================================================
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            citta TEXT,
            indirizzo TEXT,
            telefono TEXT,
            email TEXT,
            sito_web TEXT,
            rating REAL,
            num_recensioni INTEGER,
            google_place_id TEXT UNIQUE,
            stato TEXT DEFAULT 'nuovo',
            note TEXT,
            data_creazione TEXT DEFAULT CURRENT_TIMESTAMP,
            data_contatto TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messaggi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            tipo TEXT,
            contenuto TEXT,
            esito TEXT DEFAULT 'inviato',
            data_invio TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessioni_ricerca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            citta TEXT,
            lead_trovati INTEGER,
            data TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database inizializzato correttamente")


def salva_lead(lead: dict) -> int | None:
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO leads (nome, categoria, citta, indirizzo, telefono, email,
                               sito_web, rating, num_recensioni, google_place_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead.get("nome"),
            lead.get("categoria"),
            lead.get("citta"),
            lead.get("indirizzo"),
            lead.get("telefono"),
            lead.get("email"),
            lead.get("sito_web"),
            lead.get("rating"),
            lead.get("num_recensioni"),
            lead.get("place_id")
        ))
        conn.commit()
        lead_id = c.lastrowid
        return lead_id
    except sqlite3.IntegrityError:
        return None  # duplicato
    finally:
        conn.close()


def aggiorna_email(lead_id: int, email: str):
    conn = get_conn()
    conn.execute("UPDATE leads SET email=? WHERE id=?", (email, lead_id))
    conn.commit()
    conn.close()


def aggiorna_stato(lead_id: int, stato: str, note: str = None):
    conn = get_conn()
    if note:
        conn.execute("UPDATE leads SET stato=?, note=?, data_contatto=? WHERE id=?",
                     (stato, note, datetime.now().isoformat(), lead_id))
    else:
        conn.execute("UPDATE leads SET stato=?, data_contatto=? WHERE id=?",
                     (stato, datetime.now().isoformat(), lead_id))
    conn.commit()
    conn.close()


def salva_messaggio(lead_id: int, tipo: str, contenuto: str, esito: str = "inviato"):
    conn = get_conn()
    conn.execute("""
        INSERT INTO messaggi (lead_id, tipo, contenuto, esito)
        VALUES (?, ?, ?, ?)
    """, (lead_id, tipo, contenuto, esito))
    conn.commit()
    conn.close()


def get_leads(stato=None, categoria=None, citta=None, con_telefono=False, con_email=False):
    conn = get_conn()
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if stato:
        query += " AND stato=?"
        params.append(stato)
    if categoria:
        query += " AND categoria=?"
        params.append(categoria)
    if citta:
        query += " AND citta=?"
        params.append(citta)
    if con_telefono:
        query += " AND telefono IS NOT NULL AND telefono != ''"
    if con_email:
        query += " AND email IS NOT NULL AND email != ''"
    query += " ORDER BY data_creazione DESC"
    leads = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(l) for l in leads]


def get_stats():
    conn = get_conn()
    stats = {}
    stats["totale"] = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    stats["nuovi"] = conn.execute("SELECT COUNT(*) FROM leads WHERE stato='nuovo'").fetchone()[0]
    stats["contattati"] = conn.execute("SELECT COUNT(*) FROM leads WHERE stato='contattato'").fetchone()[0]
    stats["interessati"] = conn.execute("SELECT COUNT(*) FROM leads WHERE stato='interessato'").fetchone()[0]
    stats["clienti"] = conn.execute("SELECT COUNT(*) FROM leads WHERE stato='cliente'").fetchone()[0]
    stats["con_telefono"] = conn.execute("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''").fetchone()[0]
    stats["con_email"] = conn.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''").fetchone()[0]
    stats["messaggi_inviati"] = conn.execute("SELECT COUNT(*) FROM messaggi").fetchone()[0]
    stats["per_categoria"] = [
        {"categoria": r[0], "n": r[1]}
        for r in conn.execute(
            "SELECT categoria, COUNT(*) as n FROM leads GROUP BY categoria ORDER BY n DESC"
        ).fetchall()
    ]
    stats["per_citta"] = [
        {"citta": r[0], "n": r[1]}
        for r in conn.execute(
            "SELECT citta, COUNT(*) as n FROM leads GROUP BY citta ORDER BY n DESC LIMIT 10"
        ).fetchall()
    ]
    conn.close()
    return stats
