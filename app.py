import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, baby_required, sort_babies

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///babies.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show babies"""
    session["babies"] = db.execute("SELECT * FROM babies WHERE user_id = ? ORDER BY baby_name",
                        session["user_id"])

    if request.method == "POST":
        baby_name = request.form.get("baby_name")
        baby_dob = request.form.get("baby_dob")
        baby_gender = request.form.get("baby_gender")
        if len(baby_name) > 30:
            return apology("Sorry, that name is too long", 403)
        else:
            db.execute("INSERT INTO babies (baby_name, birthdate, gender, user_id) VALUES (?, ?, ?, ?)",
                       baby_name, baby_dob, baby_gender, session["user_id"])
            session["babies"] = db.execute(
                "SELECT * FROM babies WHERE user_id = ?",
                session["user_id"])
            flash(f"Baby {baby_name} has been successfully added.")
            return redirect("/")

    return render_template("index.html", babies=session["babies"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        # session["babies"] = db.execute(
        # "SELECT * FROM babies WHERE user_id = ? ORDER BY baby_name",
        # session["user_id"])

        # Redirect user to home page
        # flash("Successfully logged in!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Please enter a username", 400)
        elif not request.form.get("password"):
            return apology("Please enter a password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password confirmation does not match", 400)
        elif db.execute(
            "SELECT user_id FROM users WHERE username = ?", request.form.get("username")
            ):
            return apology("Username already taken", 400)
        else:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
            )
            session.clear()
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("invalid username and/or password", 400)
            session["user_id"] = rows[0]["user_id"]
            flash("Account registered!")
            return redirect("/")

    return render_template("register.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "GET":
        return render_template("account.html")

    user_data = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])
    form = request.form.get("submit")

    if form == "change_password":
        if not check_password_hash(
            user_data[0]["hash"], request.form.get("current_password")
        ):
            return apology("incorrect current password", 400)
        elif not request.form.get("new_password"):
            return apology("Please enter a password", 400)
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("Password confirmation does not match", 400)
        else:
            db.execute(
                "UPDATE users SET hash = ? WHERE user_id = ?",
                generate_password_hash(request.form.get("new_password")),
                session["user_id"],
            )
            flash("Password successfully changed.")
            return redirect("/")


@app.route("/sleep", methods=["GET", "POST"])
@login_required
@baby_required
def sleep():
    if request.method == "POST":

        baby_id = int(request.form.get("baby_id"))
        if not any(baby["baby_id"] == baby_id for baby in session["babies"]):
            return apology("That baby was not found", 403)
        start_time = datetime.fromisoformat(request.form.get("start_time"))
        end_time = datetime.fromisoformat(request.form.get("end_time"))
        duration = int((end_time - start_time).total_seconds()/60)
        db.execute("INSERT INTO sleeps (baby_id, start_time, end_time, duration_minutes) VALUES (?, ?, ?, ?)",
                   baby_id, start_time, end_time, duration)
        baby_name = [baby["baby_name"] for baby in session["babies"] if baby.get("baby_id") == baby_id][0]
        flash(f"Sleep for {baby_name} successfully logged!")
        return redirect("/")

    return render_template("sleep.html", babies=session["babies"])


@app.route("/feed", methods=["GET", "POST"])
@login_required
@baby_required
def feed():
    if request.method =="POST":

        baby_id = int(request.form.get("baby_id"))
        feed_time = datetime.fromisoformat(request.form.get("feed_time"))
        type = request.form.get("options-outlined")
        feed_length = request.form.get("feed_length")
        feed_volume = request.form.get("feed_volume")

        db.execute("INSERT INTO feeds (baby_id, timestamp, type, quantity_ml, duration_minutes) VALUES (?, ?, ?, ?, ?)",
                   baby_id, feed_time, type, feed_volume, feed_length)

        baby_name = [baby["baby_name"] for baby in session["babies"] if baby.get("baby_id") == baby_id][0]
        flash(f"Feed for {baby_name} successfully logged")
        return redirect("/")


    return render_template("feed.html", babies=session["babies"])


@app.route("/nappy", methods=["GET", "POST"])
@login_required
@baby_required
def nappy():
    if request.method =="POST":
        baby_id = int(request.form.get("baby_id"))
        nappy_time = datetime.fromisoformat(request.form.get("nappy_time"))
        nappy_contents = request.form.get("nappy_contents")
        nappy_size = request.form.get("nappy_size")

        if nappy_contents == "wet":
            wet = True
            dirty = False
        elif nappy_contents == "dirty":
            wet = False
            dirty = True
        elif nappy_contents == "both":
            wet = True
            dirty = True
        else:
            wet = False
            dirty = False

        db.execute("INSERT INTO nappy_changes (baby_id, timestamp, wet, dirty, nappy_size) VALUES (?, ?, ?, ?, ?)",
                   baby_id, nappy_time, wet, dirty, nappy_size)

        baby_name = [baby["baby_name"] for baby in session["babies"] if baby.get("baby_id") == baby_id][0]
        flash(f"Nappy for {baby_name} successfully logged")
        return redirect("/")

    return render_template("nappy.html", babies=session["babies"])


@app.route("/milestone", methods=["GET", "POST"])
@login_required
@baby_required
def milestone():

    if request.method =="POST":
        baby_id = int(request.form.get("baby_id"))
        milestone_time = datetime.fromisoformat(request.form.get("milestone_time"))
        description = request.form.get("description")

        db.execute("INSERT INTO milestones (baby_id, description, timestamp) VALUES (?, ?, ?)", baby_id, description, milestone_time)

        baby_name = [baby["baby_name"] for baby in session["babies"] if baby.get("baby_id") == baby_id][0]
        flash(f"Milestone for {baby_name} successfully recorded")
        return redirect(f"/milestone/history/{baby_id}")

    return render_template("milestone.html", babies=session["babies"])


@app.route("/sleep/history/<int:baby_id>", methods=["GET", "POST"])
@login_required
@baby_required
def sleep_history(baby_id):
    if not any(baby["baby_id"] == baby_id for baby in session["babies"]):
            return apology("That baby was not found", 403)
    
    if request.method == "POST":
        sleep_id = int(request.form.get("delete"))
        db.execute("DELETE FROM sleeps WHERE sleep_id = ?", sleep_id)
        flash("Milestone deleted")

    babies = sort_babies(session["babies"], baby_id)
    nappies = db.execute("SELECT * FROM nappies WHERE baby_id = ?", baby_id)
    return render_template("milestone_history.html", babies=babies, nappies=nappies)


@app.route("/milestone/history/<int:baby_id>", methods=["GET", "POST"])
@login_required
@baby_required
def milestone_history(baby_id):
    if not any(baby["baby_id"] == baby_id for baby in session["babies"]):
            return apology("That baby was not found", 403)

    if request.method == "POST":
        milestone_id = int(request.form.get("delete"))
        db.execute("DELETE FROM milestones WHERE milestone_id = ?", milestone_id)
        flash("Milestone deleted")

    babies = sort_babies(session["babies"], baby_id)
    milestones = db.execute("SELECT * FROM milestones WHERE baby_id = ?", baby_id)
    return render_template("milestone_history.html", babies=babies, milestones=milestones, baby_id=baby_id)
