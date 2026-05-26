# ============================================================
#  GF LEAD HUNTER — Web Dashboard (Flask)
# ============================================================
import csv
import io
import json
import os
import threading
from flask import Flask, render_template, jsonify, request, Response, send_file, abort

from database import get_leads, get_stats, aggiorna_stato, get_conn
from scraper import scrape_categoria_citta, scrape_tutto
from enricher import arricchisci_tutti
from outreach import invia_whatsapp_lead, invia_email_lead, campagna_whatsapp, campagna_email

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/citta")
def api_citta():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT citta FROM leads WHERE citta IS NOT NULL ORDER BY citta").fetchall()
    conn.close()
    return jsonify([r[0] for r in rows])


@app.route("/api/leads")
def api_leads():
    stato = request.args.get("stato")
    categoria = request.args.get("categoria")
    citta = request.args.get("citta")
    cerca = request.args.get("cerca", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    leads = get_leads(stato=stato, categoria=categoria, citta=citta)

    if cerca:
        leads = [l for l in leads if cerca.lower() in l.get("nome", "").lower()]

    totale = len(leads)
    start = (page - 1) * per_page
    leads_pag = leads[start:start + per_page]

    return jsonify({
        "leads": leads_pag,
        "totale": totale,
        "pagina": page,
        "per_page": per_page
    })


@app.route("/api/stato/<int:lead_id>", methods=["POST"])
def api_stato(lead_id):
    data = request.get_json()
    stato = data.get("stato")
    note = data.get("note")
    aggiorna_stato(lead_id, stato, note)
    return jsonify({"ok": True})


@app.route("/api/send-wa/<int:lead_id>", methods=["POST"])
def api_send_wa(lead_id):
    leads = get_leads()
    lead = next((l for l in leads if l["id"] == lead_id), None)
    if not lead:
        return jsonify({"ok": False, "error": "Lead non trovato"})
    ok = invia_whatsapp_lead(lead)
    return jsonify({"ok": ok})


@app.route("/api/send-email/<int:lead_id>", methods=["POST"])
def api_send_email(lead_id):
    leads = get_leads()
    lead = next((l for l in leads if l["id"] == lead_id), None)
    if not lead:
        return jsonify({"ok": False, "error": "Lead non trovato"})
    ok = invia_email_lead(lead)
    return jsonify({"ok": ok})


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json()
    categoria = data.get("categoria")
    citta = data.get("citta")

    trovati = 0

    def esegui():
        nonlocal trovati
        if categoria and citta:
            trovati = scrape_categoria_citta(categoria, citta)
        elif categoria:
            from config import ZONE_CAMPANIA
            for c in ZONE_CAMPANIA:
                trovati += scrape_categoria_citta(categoria, c)
        elif citta:
            from config import CATEGORIE
            for cat in CATEGORIE:
                trovati += scrape_categoria_citta(cat, citta)
        else:
            trovati = scrape_tutto()

    t = threading.Thread(target=esegui)
    t.start()
    t.join(timeout=300)

    return jsonify({"trovati": trovati})


@app.route("/api/campagna-wa", methods=["POST"])
def api_campagna_wa():
    data = request.get_json()
    limite = data.get("limite", 20)
    inviati = campagna_whatsapp(limite=limite)
    return jsonify({"inviati": inviati})


@app.route("/api/campagna-email", methods=["POST"])
def api_campagna_email():
    data = request.get_json()
    limite = data.get("limite", 50)
    inviate = campagna_email(limite=limite)
    return jsonify({"inviate": inviate})


@app.route("/api/enrich", methods=["POST"])
def api_enrich():
    trovate = arricchisci_tutti()
    return jsonify({"trovate": trovate})


@app.route("/api/analytics")
def api_analytics():
    conn = get_conn()
    # Per categoria
    per_cat = conn.execute("""
        SELECT categoria, COUNT(*) as tot,
               SUM(CASE WHEN telefono IS NOT NULL AND telefono != '' THEN 1 ELSE 0 END) as con_tel,
               SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as con_email,
               SUM(CASE WHEN stato = 'cliente' THEN 1 ELSE 0 END) as clienti
        FROM leads GROUP BY categoria ORDER BY tot DESC
    """).fetchall()
    # Per città top 10
    per_citta = conn.execute("""
        SELECT citta, COUNT(*) as tot FROM leads
        WHERE citta IS NOT NULL GROUP BY citta ORDER BY tot DESC LIMIT 10
    """).fetchall()
    # Per stato
    per_stato = conn.execute("""
        SELECT stato, COUNT(*) as tot FROM leads GROUP BY stato
    """).fetchall()
    # Ultimi 7 giorni
    per_giorno = conn.execute("""
        SELECT DATE(data_creazione) as giorno, COUNT(*) as tot
        FROM leads WHERE data_creazione >= DATE('now', '-7 days')
        GROUP BY giorno ORDER BY giorno
    """).fetchall()
    conn.close()
    return jsonify({
        "per_categoria": [{"categoria": r[0], "tot": r[1], "con_tel": r[2], "con_email": r[3], "clienti": r[4]} for r in per_cat],
        "per_citta": [{"citta": r[0], "tot": r[1]} for r in per_citta],
        "per_stato": [{"stato": r[0], "tot": r[1]} for r in per_stato],
        "per_giorno": [{"giorno": r[0], "tot": r[1]} for r in per_giorno],
    })


@app.route("/api/export-csv")
def api_export_csv():
    leads = get_leads()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "nome", "categoria", "citta", "indirizzo",
        "telefono", "email", "sito_web", "rating", "stato", "data_creazione"
    ])
    writer.writeheader()
    for l in leads:
        writer.writerow({k: l.get(k, "") for k in writer.fieldnames})

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=gf-leads.csv"}
    )


@app.route("/preview/<path:filename>")
def serve_preview(filename):
    """Serve le pagine HTML preview Full Booking (URL leggibile — solo interno)."""
    if not filename.endswith(".html"):
        filename = filename + ".html"
    preview_dir = os.path.join(os.path.dirname(__file__), "preview_fullbooking")
    filepath = os.path.join(preview_dir, filename)
    if not os.path.exists(filepath):
        abort(404)
    return send_file(filepath, mimetype="text/html")


@app.route("/p/<token>")
def serve_preview_token(token):
    """Serve la preview tramite token — URL breve e anonimo (usato nelle campagne)."""
    conn = get_conn()
    row = conn.execute(
        "SELECT note FROM leads WHERE fb_token = ?", (token,)
    ).fetchone()
    conn.close()
    if not row:
        abort(404)
    nota = row[0]
    if not nota or not nota.startswith("FB:preview:") and not nota.startswith("FB:inviato:"):
        abort(404)
    filename = nota.replace("FB:preview:", "").replace("FB:inviato:", "")
    preview_dir = os.path.join(os.path.dirname(__file__), "preview_fullbooking")
    filepath = os.path.join(preview_dir, filename)
    if not os.path.exists(filepath):
        abort(404)
    return send_file(filepath, mimetype="text/html")


def avvia_dashboard(port=5000):
    print(f"\n🌐 Dashboard aperta su: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
