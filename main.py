from flask import Flask, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "requests.db"

# Database init
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    message TEXT,
                    status TEXT DEFAULT 'pending'
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO requests (name, message) VALUES (?, ?)", (name, message))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return """
    <html>
    <head><title>Submit Request</title></head>
    <body style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h1>Submit Your Request</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Your Name" required><br><br>
            <textarea name="message" placeholder="Your Request" required></textarea><br><br>
            <button type="submit">Submit</button>
        </form>
        <br>
        <a href="/admin">Go to Admin Panel</a>
    </body>
    </html>
    """

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM requests")
    data = c.fetchall()
    conn.close()

    table_rows = ""
    for req in data:
        table_rows += f"""
        <tr>
            <td>{req[0]}</td>
            <td>{req[1]}</td>
            <td>{req[2]}</td>
            <td>{req[3]}</td>
            <td>
                <a href="/update/{req[0]}/approved">✅ Approve</a> |
                <a href="/update/{req[0]}/rejected">❌ Reject</a>
            </td>
        </tr>
        """

    return f"""
    <html>
    <head><title>Admin Panel</title></head>
    <body style="font-family: Arial; margin: 30px;">
        <h1>Approval Dashboard</h1>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Request</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
            {table_rows}
        </table>
        <br>
        <a href="/">⬅ Go Back</a>
    </body>
    </html>
    """

@app.route("/update/<int:req_id>/<string:status>")
def update_status(req_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE requests SET status=? WHERE id=?", (status, req_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
