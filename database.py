# ============================================================
#  GF LEAD HUNTER — Database (SQLite locale / PostgreSQL cloud)
# ============================================================
import os
import sqlite3
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USE_PG = bool(DATABASE_URL)

if USE_PG:
    import psycopg2
    import psycopg2.extras
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads.db")


def get_conn():
    if USE_PG:
        return psycopg2.connect(DATABASE_URL)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _exec(conn, sql, params=()):
    if USE_PG:
        sql = sql.replace("?", "%s")
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute(sql, params)
    return cur


def init_db():
    conn = get_conn()
    if USE_PG:
        id_def = "id SERIAL PRIMARY KEY"
    else:
        id_def = "id INTEGER PRIMARY KEY AUTOINCREMENT"

    _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS leads (
            {id_def},
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

    _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS messaggi (
            {id_def},
            lead_id INTEGER,
            tipo TEXT,
            contenuto TEXT,
            esito TEXT DEFAULT 'inviato',
            data_invio TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)

    _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS sessioni_ricerca (
            {id_def},
            categoria TEXT,
            citta TEXT,
            lead_trovati INTEGER,
            data TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database inizializzato correttamente")


def salva_lead(lead: dict):
    conn = get_conn()
    try:
        if USE_PG:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                INSERT INTO leads (nome, categoria, citta, indirizzo, telefono, email,
                                   sito_web, rating, num_recensioni, google_place_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                lead.get("nome"), lead.get("categoria"), lead.get("citta"),
                lead.get("indirizzo"), lead.get("telefono"), lead.get("email"),
                lead.get("sito_web"), lead.get("rating"), lead.get("num_recensioni"),
                lead.get("place_id")
            ))
            row = cur.fetchone()
            conn.commit()
            return row["id"] if row else None
        else:
            c = conn.cursor()
            c.execute("""
                INSERT INTO leads (nome, categoria, citta, indirizzo, telefono, email,
                                   sito_web, rating, num_recensioni, google_place_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.get("nome"), lead.get("categoria"), lead.get("citta"),
                lead.get("indirizzo"), lead.get("telefono"), lead.get("email"),
                lead.get("sito_web"), lead.get("rating"), lead.get("num_recensioni"),
                lead.get("place_id")
            ))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return None
        raise
    finally:
        conn.close()


def aggiorna_email(lead_id: int, email: str):
    conn = get_conn()
    _exec(conn, "UPDATE leads SET email=? WHERE id=?", (email, lead_id))
    conn.commit()
    conn.close()


def aggiorna_stato(lead_id: int, stato: str, note: str = None):
    conn = get_conn()
    if note:
        _exec(conn, "UPDATE leads SET stato=?, note=?, data_contatto=? WHERE id=?",
              (stato, note, datetime.now().isoformat(), lead_id))
    else:
        _exec(conn, "UPDATE leads SET stato=?, data_contatto=? WHERE id=?",
              (stato, datetime.now().isoformat(), lead_id))
    conn.commit()
    conn.close()


def salva_messaggio(lead_id: int, tipo: str, contenuto: str, esito: str = "inviato"):
    conn = get_conn()
    _exec(conn, """
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
    rows = _exec(conn, query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_conn()
    stats = {}

    def scalar(sql):
        return _exec(conn, sql).fetchone()

    stats["totale"] = list(scalar("SELECT COUNT(*) FROM leads").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads")[0]
    stats["nuovi"] = list(scalar("SELECT COUNT(*) FROM leads WHERE stato='nuovo'").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE stato='nuovo'")[0]
    stats["contattati"] = list(scalar("SELECT COUNT(*) FROM leads WHERE stato='contattato'").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE stato='contattato'")[0]
    stats["interessati"] = list(scalar("SELECT COUNT(*) FROM leads WHERE stato='interessato'").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE stato='interessato'")[0]
    stats["clienti"] = list(scalar("SELECT COUNT(*) FROM leads WHERE stato='cliente'").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE stato='cliente'")[0]
    stats["con_telefono"] = list(scalar("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''")[0]
    stats["con_email"] = list(scalar("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''")[0]
    stats["messaggi_inviati"] = list(scalar("SELECT COUNT(*) FROM messaggi").values())[0] if USE_PG else scalar("SELECT COUNT(*) FROM messaggi")[0]

    rows = _exec(conn, "SELECT categoria, COUNT(*) as n FROM leads GROUP BY categoria ORDER BY n DESC").fetchall()
    stats["per_categoria"] = [{"categoria": r["categoria"] if USE_PG else r[0], "n": r["n"] if USE_PG else r[1]} for r in rows]

    rows = _exec(conn, "SELECT citta, COUNT(*) as n FROM leads GROUP BY citta ORDER BY n DESC LIMIT 10").fetchall()
    stats["per_citta"] = [{"citta": r["citta"] if USE_PG else r[0], "n": r["n"] if USE_PG else r[1]} for r in rows]

    conn.close()
    return stats
