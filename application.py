import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = db.execute("SELECT symbol, price, SUM(shares) as total FROM account_activities WHERE id = :id GROUP BY symbol HAVING total > 0",
            id=session["user_id"])
    UTcash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

    quotes = {}
    for s in stocks:
        quotes[s["symbol"]] = lookup(s["symbol"])

    return render_template("index.html", stocks=stocks, UTcash=UTcash[0]["cash"], quotes=quotes)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Missing symbol", 656)
        if not request.form.get("shares"):
            return apology("Missing shares")
        shares = int(request.form.get("shares"))
        buy = lookup(request.form.get("symbol").upper())
        if buy == None:
            return apology("Invalid Symbol")
        price = buy["price"]
        rows = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        total_price = price * shares
        user_cash = rows[0]["cash"] # [{'cash': 555}]
        if user_cash < total_price:
           return apology("insufficient balance", 700)

        db.execute("UPDATE users SET cash = cash - :price WHERE id = :id", price=total_price, id=session["user_id"])
        db.execute("INSERT INTO account_activities(id,symbol,price,shares) VALUES (:id,:symbol,:price,:shares)", id=session["user_id"], symbol=request.form.get("symbol"), price=price, shares= request.form.get("shares"))
        #FLASH BOUGHT
        flash("Bought :)")

        return redirect("/")


    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    rows = db.execute("SELECT *FROM users WHERE username = :username", username = username)
    if len(rows) >= 1 or len(username) < 1:
        return jsonify("False")
    else:
        return jsonify("True")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    histories = db.execute("SELECT *FROM account_activities WHERE id = :id", id=session["user_id"])
    return render_template("history.html", histories=histories)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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


@app.route("/quote", methods=["GET", "POST"])
@login_required             #That decorator(@login_required) ensures that, if a user tries to visit any of those routes, he or she will first be redirected to login so as to log in.
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Missing symbol")
        quote = lookup(request.form.get("symbol").upper())

        if quote == None:
            return apology("Invalid Symbol", 400)

        return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=quote["price"])
    else:
        return render_template("quote.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username or len(username) < 2 :
            return apology("must provide valid username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords do not match", 400)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username DOSE NOT exist
        if len(rows) == 1:
            return apology("You must use different username", 400)
        rows = db.execute("INSERT INTO users(username, hash) VALUES(:username, :pass_hash)", username=request.form.get("username"),pass_hash=generate_password_hash(request.form.get("password")))

        # Forget any user_id
        session.clear()

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        shares = int(request.form.get("shares"))
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol")
        if not shares:
            return apology("Missing shares")

        stocks = db.execute("SELECT SUM(shares) as total FROM account_activities WHERE id = :id AND symbol = :symbol GROUP BY symbol",id=session["user_id"], symbol=symbol)[0]["total"]

        if shares > stocks :
            return apology("TOO MANY SHARES")

        price = lookup(symbol)["price"]
        db.execute("UPDATE users SET cash = cash + :price WHERE id = :id", id=session["user_id"], price=(price * shares))
        db.execute("INSERT INTO account_activities (id,symbol,price,shares) VALUES (:id,:symbol,:price,:shares)",
        id=session["user_id"],
        symbol=symbol,
        price=price,
        shares=-shares)

        flash("Sold! :) :( :|")

        return redirect("/")


    else:
        stocks = db.execute("SELECT symbol, SUM(shares) as total FROM account_activities WHERE id = :id GROUP BY symbol HAVING total > 0", id=session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
