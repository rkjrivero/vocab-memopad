### NOTE / DISCLAIMER: GENERAL APPLICATION FOUNDATION IS BUILT UPON THE APPLICATION.PY FILE OF CS50 PSET 9
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import datetime

#import sqlalchemy # provisional
# https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/

import re # UNUSED RN
from tempfile import mkdtemp #UNUSED RN
import secrets #UNUSED RN

# TODO - INSPECT IMPORT LIST AND REMOVE THOSE NOT RELEVANT EVENTUALLY !!!

# Configure application
app = Flask(__name__)

# Session setup
# stolen from https://stackoverflow.com/questions/34902378/where-do-i-get-a-secret-key-for-flask/34903502 because ... eh, cbf
#himitsu_key = secrets.token_hex(16)
#print("secret key is: ",himitsu_key)
#app.config['SECRET_KEY'] = himitsu_key
#app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf' # set as fixed
# https://stackoverflow.com/questions/44769152/difficulty-implementing-server-side-session-storage-using-redis-and-flask
# FOR HEROKU, YOU NEED TO SAVE SESSIONS SOMEWHERE BECAUSE SESSION IS NOT SHARED BETWEEN GUNICORN 'WORKERS'
# THIS MEANS SESSION DICTIONARY ENDS UP EMPTY
# https://stackoverflow.com/questions/30984622/flask-session-not-persistent-across-requests-in-flask-app-with-gunicorn-on-herok
# https://devcenter.heroku.com/articles/java-session-handling-on-heroku
# https://devcenter.heroku.com/articles/php-sessions
# https://devcenter.heroku.com/articles/flask-memcache
# https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true
# https://flask-session.readthedocs.io/en/latest/
# note - read up on jwt authentication

# NOTE TO SELF - DISABLED THE ENTIRE BLOCK ABOVE DUE TO WORKAROUND BY DISABLING MKDTEMP() ALONE GETS THE APP TO WORK 
# REFACTOR TO A BETTER SESSION-HANDLING METHOD ONCE PRIMARY FUNCTIONALITY IS ESTABLISHED


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# NOTE CS50PSET9 CODE FOR REMOVAL !!!
"""
# Custom filter
app.jinja_env.filters["usd"] = usd
"""

# Commented-out block to return to using signed cookies for heroku compatibility
# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# based on https://www.reddit.com/r/cs50/comments/lerroy/using_cookies_in_flask_and_deploying_to_heroku/

Session(app)

# Configure CS50 Library to use postgresql (heroku integration)
# NOTE TO SELF: TRANSITION TO SQLALCHEMY ONCE MAIN FUNCTIONALITY IS ESTABLISHED
db_uri = os.getenv("DATABASE_URL")
# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)
db = SQL(db_uri)

# NOTE CS50PSET9 CODE FOR REMOVAL !!!
"""
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
"""

@app.route("/register", methods=["GET", "POST"])
def register():
    # NOTE - REGISTER DEFINITION ORIGINALLY FROM CS50PSET9, WITHOUT MODIFICATION
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must repeat password", 400)

        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords must match", 400)

        # Ensure target language was selected
        if not request.form.get("targetlang"):
            return apology("must select target Language", 400)
        tgtlang = request.form.get("targetlang")
    
        # Ensure origin language was selected
        if not request.form.get("originlang"):
            return apology("must select origin Language", 400)
        orglang = request.form.get("originlang")

        # Assign boolean value based on auto-translate checkbox
        if request.form.get("autotrans") == "true":
            autotrans = True
        else:
            autotrans = False
    

        # Query database for username
        usertable = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))
        print(usertable)
        # Check if username exists

        if len(usertable) != 0:
            return apology("existing user detected", 400)

        else:
            newpass = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
            # print test
            print("TEST /register input: username:", request.form.get("username") ," hash:", newpass," tgtlang:", tgtlang," orglang:", 
                orglang, " autotrans (raw):", request.form.get("autotrans")," autotrans (if/else):", autotrans)
            # NOTE - try studying sqlalchemy if possible
            db.execute("INSERT INTO users (username, hash, tgtlang, orglang, autotrans, wordcount, pincount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                request.form.get("username"), newpass, tgtlang, orglang, autotrans, 0, 0)            
            flash("User registered", category="message")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # NOTE - LOGIN DEFINITION ORIGINALLY FROM CS50PSET9, WITH MODIFICATIONS
    """Log user in"""

    # Forget any userid
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
        usertable = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        print("test, query-usertable: ", usertable)
        print("test, query-username: ", request.form.get("username"))
        print("test, password-hash: ", generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))
        print("test, check_password_hash: ",check_password_hash(usertable[0]["hash"], request.form.get("password")) )

        # Ensure username exists and password is correct
        if len(usertable) != 1 or not check_password_hash(usertable[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Establish session[] array based on "user" table on database
        # NOTE: usertable = userid, username, hash, tgtlang, orglang, autotrans, pincount, wordcount
        # NOTE "user_id/user_name" instead of userid/username is both to distinctly identify a session[] variable as well as prior-html/py-code compatibility (less work)
        
        # user_id and user_name utilized for database recall, and are static (permanent)
        session["user_id"] = usertable[0]["userid"]
        session["user_name"] = usertable[0]["username"]
        # user_tgtlang/orglang/autotrans are used for layout display, and are dynamic (manually changed in profile options)
        session["user_tgtlang"] = usertable[0]["tgtlang"]
        session["user_orglang"] = usertable[0]["orglang"]
        session["user_autotrans"] = usertable[0]["autotrans"]
        # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
        session["user_wordcount"] = usertable[0]["wordcount"]
        session["user_pincount"] = usertable[0]["pincount"]

        # update current display time - display format: dd/mm/YY H:M:S
        session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # NOTE - LOGOUT DEFINITION ORIGINALLY FROM CS50PSET9, WITHOUT MODIFICATION
    """Log user out"""

    # Forget any userid
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile")
@login_required
def profile():
    # NOTE FROM CS50PSET9 SUBMISSION, REVISE AS NECESSARY LATER !!!
    """CUSTOM: Profile Page"""

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    return render_template("profile.html")

@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    # NOTE FROM CS50PSET9 SUBMISSION, REVISE AS NECESSARY LATER !!!
    """CUSTOM: Change Password Page"""

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("oldpw"):
            return apology("must provide old password", 403)

        # Ensure password was submitted
        elif not request.form.get("newpw"):
            return apology("must provide new password", 403)

        # Query database for username
        userdb = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        print("userdb[0][hash]:", userdb[0]["hash"])

        # Ensure old password is correct
        if check_password_hash(userdb[0]["hash"], request.form.get("oldpw")) == False:
            return apology("invalid old password", 403)

        else:
            changepass = generate_password_hash(request.form.get("newpw"), method='pbkdf2:sha256', salt_length=8)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", changepass, session["user_id"])
            flash("Password Changed", category="message")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepw.html")

@app.route("/")
@login_required
def index():
    # NOTE - INDEX DEFINITION ORIGINALLY FROM CS50PSET9, WITH MODIFICATIONS
    """Show INDEX.html"""

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # RETRIEVE FROM DATABASE

    # CS50 EXECUTE METHOD NOTE: If str is a SELECT, then execute returns a list of zero or more dict objects, 
    # inside of which are keys and values representing a table’s fields and cells, respectively.

    # NOTE: user table info (name/id + tgtlang/orglang/autotrans + wordcount/pincount) are saved in session[] array (initially in /login, updated as required)
    # NOTE: vocab table = wordid, userlink, strinput, strtrans, langinput, langtrans, time, rating, pin
    vocabtable = db.execute("SELECT * FROM vocab where userlink = ?", session["user_id"])        
    allvocabtable = ()
    pinvocabtable = ()
    # PRINT TEST
    print("test, vocabtable[{}]: ", vocabtable)
    print("test, allvocabtable (before): ", allvocabtable)
    # Filter out for allvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    for vocabtable_list in vocabtable:
        # PRINT TEST
        print("test, vocabtable_list{}: ", vocabtable_list)
        testvtlist = vocabtable_list.items()                
        for (vt_key, vt_value) in testvtlist:            
            # NOTE: go through all key/value pairs and search if they're for the current user
            #print("test, testvtlist: ", testvtlist)
            print("vt_key: ", vt_key)
            print("vt_value: ", vt_value)
            if vt_key == "userlink" and vt_value == session["user_id"]:
                # PRINT TEST
                print("userlink match")                
                #print("test, vocabtable_list {userlink:user_id} match: ", vocabtable_list)
                for (vt_key, vt_value) in testvtlist:
                # NOTE: go through all key/value pairs and search if they're pinned or not
                    if vt_key == "pin" and vt_value == False:
                    print("pin match")
                    allvocabtable[vt_key] = vt_value
                    # PRINT TEST
                    print("test, allvocabtable{}: ", allvocabtable)
    print("test, allvocabtable (after): ", allvocabtable)
    """
    # Filter out for pinvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    for vocabtable_list in vocabtable:
        # PRINT TEST
        print("test, vocabtable_list{}: ", vocabtable_list)                
        for (vt_key, vt_value) in vocabtable_list:            
            # NOTE: go through all key/value pairs and search if they're for the current user
            if vt_key == "userlink" and vt_value == session["user_id"]:
                # PRINT TEST
                print("test, vocabtable_list {userlink:user_id} match: ", vocabtable_list)
                # NOTE: go through all key/value pairs and search if they're pinned or not
                if vt_key == "pin" and vt_value == True:
                    pinvocabtable[vt_key] = vt_value
                    # PRINT TEST
                    print("test, allvocabtable{}: ", allvocabtable)
    """

    # NOTE/TODO NEED TO VERIFY IF ABOVE FUNCTIONS actually work (need to either get /insert route functional or insert dummy data)

    # NOTE CS50PSET9 CODE FOR REMOVAL !!!
    """    
    # RETRIEVE FROM DATABASE
    nowrecords = db.execute("SELECT * FROM nowrecords where userid = ?", session["user_id"])
    tmprecords = nowrecords
    userposition = 0
    usdstockprice = {}
    for tmprecords in tmprecords :
        userposition = userposition + (tmprecords["stock_price"] * tmprecords["stock_amount"] )
        #usdstockprice.append(usd(tmprecords["stock_price"]))
        usdstockprice[tmprecords["stock_price"]]=usd(tmprecords["stock_price"])
        usdstockprice[tmprecords["stock_price"] * tmprecords["stock_amount"]]=usd(tmprecords["stock_price"] * tmprecords["stock_amount"])
    print("userposition", userposition)
    print("usdstockprice", usdstockprice)
    usdposition = usd(userposition)
    usdtotalpos = usd(userposition + session["user_fund"])
    
    return render_template("index.html", nowrecords=nowrecords, usdstockprice=usdstockprice, usr=userposition, usd=usdposition, ust=usdtotalpos)
    """
    return render_template("index.html", vocabtable = vocabtable, allvocabtable = allvocabtable, pinvocabtable = pinvocabtable)

# NOTE - ADD NEW app.route DEFINITIONS FOLLOWING THIS LINE !!!
# TODO - CREATE DEFINITIONS FOR THE FOLLOWING FUNCTIONS:
# def input(): - to input word/phrase, etc
# def review(): - to review results of inputted word/phrase, etc
# def recall_summary(): - to view summary of all word/phrase entries, NOTE: check if overlapping with index()
# def recall_full(): - to view full list of saved word/phrase entries
# def recall_pinned(): - to view pinned list of saved word/phrase entries

# NOTE CS50PSET9 BASE CODE BELOW RETAINED
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# NOTE ENTIRE CODEBLOCK BELOW IS CS50PSET9 CODE FOR REMOVAL !!!
# NOTE COMMENTED-OUT BUT NOT REMOVED FOR TEMPORARY SYNTAX GUDIE ONLY !!!
"""
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)

        # Lookup quote for a symbol
        quote = lookup(request.form.get("symbol"))
        print("quote", quote)

        empty = ""
        if quote == None:
            return apology("no stock found", 400)
        if quote["name"] == None or quote["name"] == empty:
            quote["name"] = quote["symbol"]
        usdquoteprice = usd(quote["price"])

        # Redirect user to home page
        return render_template("quoted.html", **quote, usdquoteprice=usdquoteprice)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure stock symbol and amount was submitted
        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide stock amount", 400)
        if not request.form.get("shares").isdigit():
            return apology("must provide an integer amount", 400)
        elif int(request.form.get("shares")) <= 0:
            return apology("must provide a positive amount", 400)

        # Lookup quote for a symbol
        buy_quote = lookup(request.form.get("symbol"))
        print("buy_quote", buy_quote)

        empty = ""
        if buy_quote == None:
            return apology("no stock found", 400)
        if buy_quote["name"] == None or buy_quote["name"] == empty:
            buy_quote["name"] = buy_quote["symbol"]

        # Check how much funds the user has
        user_fund = db.execute("SELECT cash FROM users WHERE username = ?", session["user_name"])[0]["cash"]

        # note to self: "db.execute" returns a list, while lookup() returns a dictionary

        # Verify balances match
        print("user_fund:", user_fund)
        print("session[user_fund]:", session["user_fund"])

        if user_fund != session["user_fund"]:
            return apology("FUND BALANCE MISMATCH")

        # Compute costs
        buystockprice = float(buy_quote["price"])
        buystockamount = float(request.form.get("shares"))
        cost = buystockprice * buystockamount

        print("buystockprice", buystockprice)
        print("buystockamount:", buystockamount)
        print("cost:", cost)

        # Verify is user has enough cash
        if int(cost) > int(user_fund):
            return apology("INSUFFICIENT FUNDING")

        # Proceed with transaction
        user_fund = session["user_fund"] - cost
        print("user_fund:", user_fund)

        # Insert into table of all stock purchases
        db.execute(
            "INSERT INTO buyrecords (userid, stock_symbol, stock_name, stock_amount, stock_price, time) VALUES (?, ?, ?, ?, ?, ?)",
            session["user_id"], buy_quote["symbol"], buy_quote["name"], buystockamount, buystockprice, datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            )

        # Insert into table of all currently-owned stocks
        db.execute(
        	"INSERT INTO nowrecords (userid, stock_symbol, stock_name, stock_amount, stock_price, time) VALUES (?, ?, ?, ?, ?, ?)",
        	session["user_id"], buy_quote["symbol"], buy_quote["name"], buystockamount, buystockprice, datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        	)

        # Update balances
        session["user_fund"] = user_fund
        session["user_balance"] = usd(user_fund)

        db.execute(
        	"UPDATE users SET cash = ? WHERE username = ?",
        	session["user_fund"], session["user_name"]
        	)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Obtain list of user-held stocks
        userheld = db.execute("SELECT * FROM nowrecords where userid = ?", session["user_id"])
        print("userheld:", userheld)

        # Ensure stock symbol and amount was submitted
        if not request.form.get("symbol"):
            return apology("must provide stock symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide stock amount", 400)
        if not request.form.get("shares").isdigit():
            return apology("must provide an integer amount", 400)
        elif not int(request.form.get("shares")) >= 0:
            return apology("must provide a positive amount", 400)

        # split merged html input (symbols|now_id) into two items
        userheld_split = request.form.get("symbol").split("|")
        if len(userheld_split) == 2:
            print("userheld_split", userheld_split)
            userheld_stocksymbol = userheld_split[0]
            userheld_nowid = int(userheld_split[1])
            print("userheld_stocksymbol:", userheld_stocksymbol)
            print("userheld_nowid:", userheld_nowid)

        # check50 workaround where html input is just symbol itself
        elif len(userheld_split) == 1:
            print("userheld_split", userheld_split)
            userheld_stocksymbol = userheld_split[0]
            for checkid in userheld:
                if userheld_stocksymbol == checkid["stock_symbol"]:
                    userheld_nowid = checkid["now_id"]
                    break
            print("userheld_stocksymbol:", userheld_stocksymbol)
            print("userheld_nowid:", userheld_nowid)


        # Check how much funds the user has
        user_fund = db.execute("SELECT cash FROM users WHERE username = ?", session["user_name"])[0]["cash"]

        # Verify balances match
        print("user_fund:", user_fund)
        print("session[user_fund]:", session["user_fund"])

        if user_fund != session["user_fund"]:
            return apology("FUND BALANCE MISMATCH")

        # Lookup quote for a symbol
        sell_quote = lookup(userheld_stocksymbol)
        print("sell_quote:", sell_quote)

        # Compute costs
        sellstockprice = float(sell_quote["price"])
        sellstockamount = float(request.form.get("shares"))
        cashback = sellstockprice * sellstockamount

        print("sellstockprice:", sellstockprice)
        print("sellstockamount:", sellstockamount)
        print("cashback:", cashback)

        # Verify is user has enough stocks on hand

        for innerlist in userheld:
            if userheld_nowid == innerlist["now_id"]:
                print("stock amount:", innerlist["stock_amount"])
                if sellstockamount > innerlist["stock_amount"]:
                    return apology("NOT ENOUGH STOCK AT HAND")
                else:
                    # Identify if whether to delete or update nowrecord entry
                    if sellstockamount == innerlist["stock_amount"]:
                        deletenowrec = True
                    else:
                        deletenowrec = False
                        newstockamount = innerlist["stock_amount"] - sellstockamount
                        print("newstockamount:", newstockamount)
                        break

        print("deletenowrec", deletenowrec)

        # Proceed with transaction
        user_fund = session["user_fund"] + cashback
        print("userfund:", user_fund)

        # Insert into table of all stock sales
        db.execute(
            "INSERT INTO sellrecords (userid, stock_symbol, stock_name, stock_amount, stock_price, time) VALUES (?, ?, ?, ?, ?, ?)",
            session["user_id"], sell_quote["symbol"], sell_quote["name"], sellstockamount, sellstockprice, datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            )

        if deletenowrec == True:
            # Remove from table of all currently-owned stocks
            db.execute(
            	"DELETE FROM nowrecords WHERE now_id = ?",
            	userheld_nowid
            	)
        else:
            # Update nowrecord to the new amount
            db.execute(
                "UPDATE nowrecords SET stock_amount = ?, time = ? WHERE now_id = ?",
                newstockamount, datetime.now().strftime("%Y/%m/%d %H:%M:%S"), userheld_nowid
                )

        # Update balances
        session["user_fund"] = user_fund
        session["user_balance"] = usd(user_fund)

        db.execute(
        	"UPDATE users SET cash = ? WHERE username = ?",
        	session["user_fund"], session["user_name"]
        	)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Obtain list of user-held stocks
        user_held = db.execute("SELECT * FROM nowrecords where userid = ?", session["user_id"])
        print("user_held:", user_held)
        return render_template("sell.html", user_held=user_held)

@app.route("/history")
@login_required
def history():

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # RETRIEVE FROM DATABASE
    buyrecords = db.execute("SELECT * FROM buyrecords where userid = ?", session["user_id"])
    sellrecords = db.execute("SELECT * FROM sellrecords where userid = ?", session["user_id"])
    print("buyrecords:", buyrecords)
    print("sellrecords:", sellrecords)

    return render_template("history.html", buyrecords=buyrecords, sellrecords=sellrecords)

@app.route("/addfunds", methods=["GET", "POST"])
@login_required
def addfunds():

    # update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure amount was submitted
        if not request.form.get("newfunds"):
            return apology("must provide funding amount", 403)

        # Update database
        new_fund = session["user_fund"] + int(request.form.get("newfunds"))
        session["user_fund"] = new_fund
        session["user_balance"] = usd(new_fund)
        db.execute(
        	"UPDATE users SET cash = ? WHERE username = ?",
        	new_fund, session["user_name"]
        	)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Actually just fluff tbh
        fundsource = ["VISA", "MASTERCARD", "AMEX"]
        return render_template("addfunds.html", fundsource=fundsource)
"""