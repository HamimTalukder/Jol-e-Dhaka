# Some of the structure of this file (login/register pattern, session setup)
# was written with help from Claude (Anthropic), as allowed by CS50's final
# project policy on using AI tools as helpers.

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# A secret key is needed so Flask can sign session cookies
app.secret_key = "change-this-to-something-random"

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use our SQLite database
db = SQL("sqlite:///waterlog.db")


@app.after_request
def after_request(response):
    """Make sure responses are not cached by the browser"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show the map with all active waterlogging reports"""
    return render_template("index.html")


@app.route("/api/reports")
def api_reports():
    """Return active (not expired, not cleared) reports as JSON, for the map to load"""
    reports = db.execute(
        """
        SELECT id, area_name, latitude, longitude, severity, description, created_at
        FROM reports
        WHERE status = 'active' AND expires_at > datetime('now')
        ORDER BY created_at DESC
        """
    )
    return jsonify(reports)


@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Let a logged-in user submit a new waterlogging report"""
    if request.method == "POST":
        area_name = request.form.get("area_name")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        severity = request.form.get("severity")
        description = request.form.get("description")

        # Basic validation
        if not latitude or not longitude:
            flash("Please click on the map to select a location.")
            return redirect("/report")

        if severity not in ("light", "moderate", "severe"):
            flash("Please choose a severity level.")
            return redirect("/report")

        # New reports start out active and expire in 24 hours unless someone
        # confirms the water is still there
        db.execute(
            """
            INSERT INTO reports
                (user_id, area_name, latitude, longitude, severity, description,
                 created_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now', '+24 hours'), 'active')
            """,
            session["user_id"], area_name, latitude, longitude, severity, description
        )

        flash("Thanks! Your report has been added to the map.")
        return redirect("/")

    return render_template("report.html")


@app.route("/confirm/<int:report_id>", methods=["POST"])
@login_required
def confirm(report_id):
    """Someone is confirming the water is still there, so push back the expiry time"""
    db.execute(
        "UPDATE reports SET expires_at = datetime('now', '+12 hours') WHERE id = ? AND status = 'active'",
        report_id
    )
    flash("Thanks for the update!")
    return redirect("/")


@app.route("/clear/<int:report_id>", methods=["POST"])
@login_required
def clear(report_id):
    """Someone is saying the water has gone down, so mark the report cleared"""
    db.execute("UPDATE reports SET status = 'cleared' WHERE id = ?", report_id)
    flash("Marked as cleared. Thanks!")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Please provide a username.")
            return redirect("/login")
        if not request.form.get("password"):
            flash("Please provide a password.")
            return redirect("/login")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password.")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Please provide a username.")
            return redirect("/register")
        if not password:
            flash("Please provide a password.")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords must match.")
            return redirect("/register")

        existing = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(existing) > 0:
            flash("That username is already taken.")
            return redirect("/register")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        flash("Registered! Please log in.")
        return redirect("/login")

    return render_template("register.html")


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
