import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required,usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    incomplete=db.execute("SELECT taskid,task FROM tasks where person_id=:user_id and completed=:comp",user_id=session["user_id"],comp=0)
    complete=db.execute("SELECT taskid,task FROM tasks where person_id=:user_id and completed=:comp",user_id=session["user_id"],comp=1)
    return render_template("index.html",incomplete=incomplete, complete=complete)


@app.route("/add", methods=["GET", "POST"])
@login_required
def buy():
    if request.method=="POST":
        task=request.form.get("task")
        db.execute("INSERT INTO tasks (person_id, task, completed) VALUES (:userid, :task, :completed)",userid=session["user_id"], task=task, completed=0)
        return redirect("/")
    else:
        return render_template("add.html")


@app.route("/remove" ,methods=["GET", "POST"])
@login_required
def history():
    if request.method=="POST":
        taskid=request.form.get("taskid")
        db.execute("UPDATE tasks SET completed=1 where taskid=:taskid and person_id=:userid ",userid=session["user_id"], taskid=taskid)
        return redirect("/")
    else:
        return render_template("remove.html")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)
        elif request.form.get("confirmation")!=request.form.get("password"):
            return apology("please check your password", 400)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) > 0:
            return apology("account with entered username already exists", 400)
        else:
            name=request.form.get("username")
            hash=generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users(username,hash) VALUES(?,?)",name,hash)
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            amount = db.execute("SELECT cash FROM users WHERE username = ?", request.form.get("username"))
            session["user_id"] = rows[0]["id"]
            return redirect("/")
    else:
        return render_template("register.html")
