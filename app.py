import datetime
import random
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from name_check import check_name
from email_send import send_email

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

def apology(message):
    return render_template("apology.html", message=message)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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
    return render_template("layout.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted(rows)
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = (?)", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    '''Log user out'''
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/profile")
def profile():
    '''Show users profile'''
    user_id = session["user_id"]
    user_db = db.execute("SELECT username, code, email, cash FROM users WHERE id = (?)", user_id)
    return render_template("profile.html", database=user_db)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "GET":
        user_id = session["user_id"]
        user_db = db.execute("SELECT username, email FROM users WHERE id = (?)", user_id)
        return render_template("settings.html", database=user_db)
    else:
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = (?)", user_id)
        #Change username
        if request.form.get("username-input"):
            username_db = db.execute("SELECT username FROM users WHERE id = (?)", user_id)
            old_username = username_db[0]["username"]
            username = request.form.get("username-input")
            password = request.form.get("password-username")
            confirmation = request.form.get("password-username-2")

            #Checking passwords
            if password != confirmation:
                return apology("Password and confirmation does not match")
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("Password is incorrect")
            if old_username == username:
                return apology("Username must be different from alredy existing one")

            db.execute("UPDATE users SET username = (?) WHERE id = (?)", username, user_id)
            return redirect("/")

        #Change email
        elif request.form.get("email-input"):
            email_db = db.execute("SELECT email FROM users WHERE id = (?)", user_id)
            old_email = email_db[0]["email"]
            email = request.form.get("email-input")
            password = request.form.get("password-email")
            confirmation = request.form.get("password-email-2")

            #Checking passwords
            if password != confirmation:
                return apology("Password and confirmation does not match")
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("Password is incorrect")
            if email == old_email:
                return apology("Email must be different from alredy existing one")

            #Send email
            body = "Congratulations on changing email"
            send_email(app, email, body)
            db.execute("UPDATE users SET email = (?) WHERE id = (?)", email, user_id)
            return redirect("/")

        #Change pasword
        if request.form.get("old-password-input"):
            old_password = request.form.get("old-password-input")
            password = request.form.get("password-password")
            confirmation = request.form.get("password-password-2")

            #Checking passwords
            if password != confirmation:
                return apology("Password and confirmation does not match")
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_password):
                return apology("Password is incorrect")
            if old_password == password:
                return apology("Password must be different from the one existing")

            #Create new hash for password
            hash = generate_password_hash(password)
            #Checing if passwords are different from one another
            code_db = db.execute("SELECT code FROM users")
            code = random.randint(10000,99999)
            while code in code_db:
                code = random.randint(10000,99999)
            db.execute("UPDATE users SET hash = (?) WHERE id = (?)", hash, user_id)
            return redirect("/")
        return apology("Please enter all data")


@app.route("/history", methods=["GET", "POST"])
def history():
    user_id = session["user_id"]
    if request.method == "GET":
        #Working with filtering criteria
        transactions_db = db.execute("SELECT reason, money, date, receiver_id AS receiver_id_imp, user_id AS user_id_imp, IIF(receiver_id == (?), user_id, receiver_id) important_id, IIF(receiver_id == (?), (SELECT username FROM users WHERE id = IIF(receiver_id == (?), user_id, receiver_id)), username) important_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE user_id = (?) OR receiver_id = (?) ORDER BY date DESC", user_id, user_id, user_id, user_id, user_id)
        return render_template("history.html", database=transactions_db, current_user_id=user_id)
    else:
        transactions_db = "SELECT reason, money, date, receiver_id AS receiver_id_imp, user_id AS user_id_imp, IIF(receiver_id == (" + str(user_id) + "), user_id, receiver_id) important_id, IIF(receiver_id == (" + str(user_id) + "), (SELECT username FROM users WHERE id = IIF(receiver_id == (" + str(user_id) + "), user_id, receiver_id)), username) important_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE (user_id = (" + str(user_id) + ") OR receiver_id = (" + str(user_id) + "))"
        #Filtering
        if request.form.get("by-date-start"):
            start_date = request.form.get("by-date-start").replace("-", "")
            end_date = request.form.get("by-date-end").replace("-", "")
            if(int(start_date) > int(end_date)):
                return apology("enter different start or end date")
            transactions_db = db.execute(transactions_db + " AND (CAST(strftime('%Y%m%d', date) AS INTEGER) >= ("+ str(int(start_date)) + ")) AND (CAST(strftime('%Y%m%d', date) AS INTEGER) <= (" + str(int(end_date)) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-cash-start"):
            start_cash = "%.2f" % float(request.form.get("by-cash-start"))
            end_cash = "%.2f" % float(request.form.get("by-cash-end"))
            if float(start_cash) > float(end_cash) :
                return apology("Please enter a smaller end number")
            if float(start_cash) < 0.01 or float(end_cash) < 0.01:
                return apology("Please enter a positive number")
            transactions_db = db.execute(transactions_db + " AND (money >= ("+ str(start_cash) + ")) AND (money <= (" + str(end_cash) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("reason"):
            reason = request.form.get("reason")
            transactions_db = db.execute(transactions_db + " AND (reason = ('" + str(reason) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-username-input"):
            username = request.form.get("by-username-input")
            transactions_db = db.execute(transactions_db + " AND (important_username = ('" + str(username) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        return apology("Please enter all requested data")


@app.route("/history/by-me", methods=["GET", "POST"])
def historyByMe():
    user_id = session["user_id"]
    if request.method == "GET":
        #Working with filtering criteria
        transactions_db = db.execute("SELECT user_id, receiver_id, reason, money, date, username AS r_username, (SELECT username FROM users WHERE id = IIF(user_id == (?), user_id, receiver_id)) u_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE user_id = (?) ORDER BY date DESC", user_id, user_id)
        return render_template("history.html", database=transactions_db, current_user_id=user_id)
    else:
        transactions_db = "SELECT user_id, receiver_id, reason, money, date, username AS r_username, (SELECT username FROM users WHERE id = IIF(user_id == (" + str(user_id) + "), user_id, receiver_id)) u_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE user_id = (" + str(user_id) + ")"
        #Filtering
        if request.form.get("by-date-start"):
            start_date = request.form.get("by-date-start").replace("-", "")
            end_date = request.form.get("by-date-end").replace("-", "")
            if(int(start_date) > int(end_date)):
                return apology("enter different start or end date")
            transactions_db = db.execute(transactions_db + " AND (CAST(strftime('%Y%m%d', date) AS INTEGER) >= ("+ str(int(start_date)) + ")) AND (CAST(strftime('%Y%m%d', date) AS INTEGER) <= (" + str(int(end_date)) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-cash-start"):
            start_cash = "%.2f" % float(request.form.get("by-cash-start"))
            end_cash = "%.2f" % float(request.form.get("by-cash-end"))
            if float(start_cash) > float(end_cash) :
                return apology("Please enter a smaller end number")
            if float(start_cash) < 0.01 or float(end_cash) < 0.01:
                return apology("Please enter a positive number")
            transactions_db = db.execute(transactions_db + " AND (money >= ("+ str(start_cash) + ")) AND (money <= (" + str(end_cash) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("reason"):
            reason = request.form.get("reason")
            transactions_db = db.execute(transactions_db + " AND (reason = ('" + str(reason) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-username-input"):
            username = request.form.get("by-username-input")
            transactions_db = db.execute(transactions_db + " AND (username = ('" + str(username) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        return apology("Please enter all requested data")


@app.route("/history/to-me", methods=["GET", "POST"])
def historyToMe():
    user_id = session["user_id"]
    if request.method == "GET":
        #Working with filtering criteria
        transactions_db = db.execute("SELECT user_id, receiver_id, reason, money, date, username AS r_username, (SELECT username FROM users WHERE id = IIF(receiver_id == (?), user_id, receiver_id)) u_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE receiver_id = (?) ORDER BY date DESC", user_id, user_id)
        return render_template("history.html", database=transactions_db, current_user_id=user_id)
    else:
        transactions_db = "SELECT user_id, receiver_id, reason, money, date, username AS r_username, (SELECT username FROM users WHERE id = IIF(receiver_id == (" + str(user_id) + "), user_id, receiver_id)) u_username FROM transactions INNER JOIN users ON users.id = transactions.receiver_id WHERE receiver_id = (" + str(user_id) + ")"
        #Filtering
        if request.form.get("by-date-start"):
            start_date = request.form.get("by-date-start").replace("-", "")
            end_date = request.form.get("by-date-end").replace("-", "")
            if(int(start_date) > int(end_date)):
                return apology("enter different start or end date")
            transactions_db = db.execute(transactions_db + " AND (CAST(strftime('%Y%m%d', date) AS INTEGER) >= ("+ str(int(start_date)) + ")) AND (CAST(strftime('%Y%m%d', date) AS INTEGER) <= (" + str(int(end_date)) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-cash-start"):
            start_cash = "%.2f" % float(request.form.get("by-cash-start"))
            end_cash = "%.2f" % float(request.form.get("by-cash-end"))
            if float(start_cash) > float(end_cash) :
                return apology("Please enter a smaller end number")
            if float(start_cash) < 0.01 or float(end_cash) < 0.01:
                return apology("Please enter a positive number")
            transactions_db = db.execute(transactions_db + " AND (money >= ("+ str(start_cash) + ")) AND (money <= (" + str(end_cash) + ")) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("reason"):
            reason = request.form.get("reason")
            transactions_db = db.execute(transactions_db + " AND (reason = ('" + str(reason) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        elif request.form.get("by-username-input"):
            username = request.form.get("by-username-input")
            transactions_db = db.execute(transactions_db + " AND (username = ('" + str(username) + "')) ORDER BY date DESC")
            return render_template("history.html", database=transactions_db, current_user_id=user_id)
        return apology("Please enter all requested data")


@app.route("/send_money", methods=["GET", "POST"])
def send_money():
    if request.method == "GET":
        return render_template("send_money.html")
    else:
        #Getting inputs
        name = request.form.get("receivername")
        rcode = request.form.get("receivercode")
        money = request.form.get("money")
        reason = request.form.get("reason")

        #Checking if inputs are not NULL
        if not name:
            return apology("Please enter name of user to whom you want to send money")
        if not rcode:
            return apology("Please enter a code of user")
        if not money:
            return apology("Please enter a sum of money that you want to send")
        if not reason:
            return apology("Please enter reason why you want to send money")

        #Checking if number ipnuts are consisting only out of numbers
        for row in range(0, len(str(rcode))):
            if ord(rcode[row]) > 57 or ord(rcode[row]) < 48:
                return apology("Please enter an code consisting only out of numbers")
        if float(money) % 1 != 0:
            money_new = str(int(float(money)*100))
            for row in range(0, len(money_new)):
                if ord(money_new[row]) > 57 or ord(money_new[row]) < 48:
                    return apology("Please enter a real number")
        else:
            for row in range(0, len(str(money))):
                if ord(money[row]) > 57 or ord(money[row]) < 48:
                    return apology("Please enter a real number")

        #Creating important user and receiver variables
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users where id = (?)", user_id)
        user_cash = "%.2f" % (user_cash_db[0]["cash"])
        receiver_code_count_db = db.execute("SELECT COUNT(code) as code FROM users")
        receiver_code_count = receiver_code_count_db[0]["code"]
        code_db = db.execute("SELECT code FROM users")

        #Checking if code is in database
        data = 0
        for row in range(receiver_code_count):
            if str(rcode) != str(code_db[row]["code"]):
                data = data + 1
        if data == receiver_code_count:
            return apology("Check if you wrote code correctly")

        #Creating more important eceiver variables
        receiver_id_db = db.execute("SELECT id FROM users where code = (?)", rcode)
        receiver_id = receiver_id_db[0]["id"]
        receiver_cash_db = db.execute("SELECT cash FROM users where id = (?)", receiver_id)
        receiver_cash = "%.2f" % (receiver_cash_db[0]["cash"])
        receiver_name_db = db.execute("SELECT username FROM users where id = (?)", receiver_id)
        receiver_name = receiver_name_db[0]["username"]

        #Checking if username is not trying to send money to himnself
        if user_id == receiver_id:
            return apology("You can't sent money to yourslef")
        #Checking if username is correct and if not - letting it slide if it is simmilar enough
        if check_name(name, receiver_name) < 50:
            return apology("Check if you wrote username correctly")

        #Checking if written sum of money is not higher that users personal cash
        if float(money) > float(user_cash):
            return apology("Please enter a lower amount of money, you can not give that many.")
        else:
            money = "%.2f" % float(money)
            new_user_cash = "%.2f" % (float(user_cash) - float(money))
            db.execute("UPDATE users SET cash = (?) WHERE id = (?)", new_user_cash, user_id)

            new_receiver_cash = "%.2f" % (float(receiver_cash) + float(money))
            db.execute("UPDATE users SET cash = (?) WHERE id = (?)", new_receiver_cash, receiver_id)

            date = datetime.datetime.now()
            db.execute("INSERT INTO transactions (user_id, receiver_id, reason, money, date) VALUES(?, ?, ?, ?, ?)", user_id, receiver_id, reason, money, date)

            flash(f"Congratulations, you just sent {money}€ to {name}!")

        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        #Getting inputs
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #Checking if inputs are not NULL
        if not username:
            return apology("please enter username")
        elif not email:
            return apology("please enter email")
        elif not password:
            return apology("please enter password")
        elif not confirmation:
            return apology("please enter confirmation")
        if password != confirmation:
            return apology("Password does not match confirmation")

        hash = generate_password_hash(password)
        #Checing if passwords are different from one another
        code_db = db.execute("SELECT code FROM users")
        code = random.randint(10000,99999)
        while code in code_db:
             code = random.randint(10000,99999)

        try:
            db.execute("INSERT INTO users (username, code, email, hash) VALUES(?, ?, ?, ?)", username, code, email, hash)
        except:
            return apology("This username alredy exists")

        body = "You are registered"

        #Sending email
        send_email(app, email, body)
        return redirect("/")