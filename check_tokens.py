import sqlite3, os

conn = sqlite3.connect('leads.db')
rows = conn.execute(
    "SELECT nome, fb_token, note FROM leads WHERE fb_token IS NOT NULL AND fb_token != '' LIMIT 5"
).fetchall()
for r in rows:
    print(f"Nome: {r[0][:35]} | Token: {r[1]} | Note: {str(r[2])[:55]}")

total = conn.execute(
    "SELECT COUNT(*) FROM leads WHERE fb_token IS NOT NULL AND fb_token != ''"
).fetchone()[0]
preview_ready = conn.execute(
    "SELECT COUNT(*) FROM leads WHERE fb_token IS NOT NULL AND fb_token != '' AND note LIKE 'FB:%'"
).fetchone()[0]
print(f"\nTotale con token: {total}")
print(f"Con preview pronta: {preview_ready}")
conn.close()
