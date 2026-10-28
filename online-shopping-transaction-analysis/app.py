import os
import threading
import webbrowser

from flask import Flask, jsonify, redirect, render_template, request, url_for

from analysis import build_report
from database import get_db, import_csv, init_db

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/report")
def api_report():
    return jsonify(build_report(request.args.get("start"), request.args.get("end")))


@app.route("/transactions")
def transactions():
    q = request.args.get("q", "").strip()
    sql, params = "SELECT * FROM transactions", []
    if q:
        sql += " WHERE order_id LIKE ? OR customer_id LIKE ? OR product LIKE ? OR category LIKE ?"
        params = [f"%{q}%"] * 4
    rows = get_db().execute(sql + " ORDER BY order_date DESC LIMIT 200", params).fetchall()
    return render_template("transactions.html", rows=rows, q=q)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    message, ok = None, True
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".csv"):
            message, ok = "Please choose a .csv file.", False
        else:
            try:
                done, skipped = import_csv(f.read().decode("utf-8-sig"))
                message = f"Imported {done} transactions ({skipped} invalid rows skipped)."
            except (ValueError, UnicodeDecodeError) as e:
                message, ok = str(e), False
    return render_template("upload.html", message=message, ok=ok)


@app.route("/clear", methods=["POST"])
def clear():
    with get_db() as db:
        db.execute("DELETE FROM transactions")
    return redirect(url_for("upload"))


if __name__ == "__main__":
    init_db()
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True)
