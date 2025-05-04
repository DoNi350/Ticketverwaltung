from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import send_file
import io
import ast

import os
import sqlite3
import ast
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geheim'
app.jinja_env.globals.update(data_eval=lambda d: ast.literal_eval(d))

DB_PATH = "tickets.db"
PHOTO_FOLDER = "tickets_photos"
os.makedirs(PHOTO_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import send_file
import io

@app.route('/export_pdf')
def export_pdf():
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Alle Tickets")
    y -= 30

    pdf.setFont("Helvetica", 10)
    for ticket in tickets:
        data = ast.literal_eval(ticket['data'])
        line = (
            f"{ticket['ticket_number']} | "
            f"{ticket['ticket_type']} | "
            f"{data.get('company', '-')} | "
            f"{data.get('contact', '-')} | "
            f"{data.get('brand', '-')} | "
            f"{data.get('model', '-')} | "
            f"{ticket['status']} | "
            f"{ticket['created_at']}"
        )
        pdf.drawString(50, y, line)
        y -= 15
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="tickets_export.pdf", mimetype='application/pdf')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_ticket/<ticket_type>', methods=['GET', 'POST'])
def create_ticket(ticket_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT,
            ticket_type TEXT,
            data TEXT,
            photo_path TEXT,
            status TEXT,
            closed_at TEXT,
            created_at TEXT
        )
    """)

    # Letzte ID je Tickettyp holen
    cursor.execute("SELECT MAX(id) FROM tickets WHERE ticket_type = ?", (ticket_type,))
    last_id = cursor.fetchone()[0]
    next_id = (last_id if last_id else 0) + 1

    # Ticketnummer mit Typpräfix
    prefix = "#R" if ticket_type.lower() == "reparatur" else "#S"
    ticket_number = f"{prefix}{next_id:05d}"

    if request.method == 'POST':
        form = request.form
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        photo_path = ""
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                filename = f"{form['company']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                photo_path = os.path.join(PHOTO_FOLDER, filename)
                photo.save(photo_path)

        cursor.execute("""
            INSERT INTO tickets (
                ticket_number, ticket_type, data, photo_path, status, closed_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_number,
            ticket_type,
            str(dict(form)),
            photo_path,
            form.get("status", "Offen"),
            form.get("closed_at", ""),
            created_at
        ))
        conn.commit()
        conn.close()
        flash(f"Ticket {ticket_number} gespeichert.", "success")
        return redirect(url_for('index'))

    conn.close()
    return render_template('create_ticket.html', ticket_type=ticket_type, ticket_number=ticket_number)

@app.route('/all_tickets')
def all_tickets():
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return render_template('all_tickets.html', tickets=tickets)

@app.route('/edit_ticket/<ticket_number>', methods=['GET', 'POST'])
def edit_ticket(ticket_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,))
    ticket = cursor.fetchone()

    if not ticket:
        flash("Ticket nicht gefunden.", "error")
        return redirect(url_for('all_tickets'))

    if request.method == 'POST':
        status = request.form.get("status", "Offen")
        closed_at = request.form.get("closed_at", "")
        data_dict = dict(request.form)
        data_dict.pop("status", None)
        data_dict.pop("closed_at", None)
        cursor.execute("UPDATE tickets SET data = ?, status = ?, closed_at = ? WHERE ticket_number = ?",
                       (str(data_dict), status, closed_at, ticket_number))
        conn.commit()
        conn.close()
        flash("Ticket aktualisiert.", "success")
        return redirect(url_for('all_tickets'))

    data = ast.literal_eval(ticket['data'])
    conn.close()
    return render_template('edit_ticket.html', ticket=ticket, data=data)

@app.route('/delete_ticket/<ticket_number>')
def delete_ticket(ticket_number):
@app.route('/export_pdf')
def export_pdf():
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Alle Tickets")
    y -= 30

    pdf.setFont("Helvetica", 10)
    for ticket in tickets:
        data = ast.literal_eval(ticket['data'])
        line = (
            f"{ticket['ticket_number']} | "
            f"{ticket['ticket_type']} | "
            f"{data.get('company', '-')} | "
            f"{data.get('contact', '-')} | "
            f"{data.get('brand', '-')} | "
            f"{data.get('model', '-')} | "
            f"{ticket['status']} | "
            f"{ticket['created_at']}"
        )
        pdf.drawString(50, y, line)
        y -= 15
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name="tickets_export.pdf",
                     mimetype='application/pdf')
    conn = get_db_connection()
    conn.execute("DELETE FROM tickets WHERE ticket_number = ?", (ticket_number,))
    conn.commit()
    conn.close()
    flash(f"Ticket {ticket_number} wurde gelöscht.", "success")
    return redirect(url_for('all_tickets'))

if __name__ == '__main__':
    app.run(debug=True)
