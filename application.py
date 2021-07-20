### NOTE / DISCLAIMER: GENERAL APPLICATION FOUNDATION IS BUILT UPON THE APPLICATION.PY FILE OF CS50 PSET 9
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import datetime
# Import googletrans (https://pypi.org/project/googletrans/ , https://py-googletrans.readthedocs.io/en/latest/)
from googletrans import Translator
# Import SQLAlchemy NOTE: currently vestigial due to CS50 reliance
from sqlalchemy.sql.expression import false

# TODO - INSPECT IMPORT LIST BELOW AND REMOVE THOSE NOT RELEVANT EVENTUALLY !!!
"""
import sqlalchemy # provisional
# https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/
import re # UNUSED RN
from tempfile import mkdtemp #UNUSED RN
import secrets #UNUSED RN
"""

# Configure application
app = Flask(__name__)

# Session setup
"""
# stolen from https://stackoverflow.com/questions/34902378/where-do-i-get-a-secret-key-for-flask/34903502 because ... eh, cbf
himitsu_key = secrets.token_hex(16)
print("secret key is: ",himitsu_key)
app.config['SECRET_KEY'] = himitsu_key
app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf' # set as fixed
"""
# NOTE TO SELF - DISABLED THE ENTIRE BLOCK ABOVE DUE TO WORKAROUND BY DISABLING MKDTEMP() ALONE GETS THE APP TO WORK 
# NOTE: read up on jwt authentication
# REFACTOR TO A BETTER SESSION-HANDLING METHOD ONCE PRIMARY FUNCTIONALITY IS ESTABLISHED
#   https://stackoverflow.com/questions/44769152/difficulty-implementing-server-side-session-storage-using-redis-and-flask
# FOR HEROKU, YOU NEED TO SAVE SESSIONS SOMEWHERE BECAUSE SESSION IS NOT SHARED BETWEEN GUNICORN 'WORKERS'
#   THIS MEANS SESSION DICTIONARY ENDS UP EMPTY
# STUDY NOTES:
#   https://stackoverflow.com/questions/30984622/flask-session-not-persistent-across-requests-in-flask-app-with-gunicorn-on-herok
#   https://devcenter.heroku.com/articles/java-session-handling-on-heroku
#   https://devcenter.heroku.com/articles/php-sessions
#   https://devcenter.heroku.com/articles/flask-memcache
#   https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true
#   https://flask-session.readthedocs.io/en/latest/

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Commented-out 'app.config["SESSION_FILE_DIR"] = mkdtemp()' for heroku compatibility
# based on https://www.reddit.com/r/cs50/comments/lerroy/using_cookies_in_flask_and_deploying_to_heroku/

Session(app)

# Configure CS50 Library to use postgresql (heroku integration)
# NOTE TO SELF: TRANSITION TO SQLALCHEMY ONCE MAIN FUNCTIONALITY IS ESTABLISHED
db_uri = os.getenv("DATABASE_URL")
# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)
db = SQL(db_uri)

# Permanent dictionary of initially supported languages
all_languages = {
'en': 'English'
'eo': 'Esperanto'
'ja': 'Japanese'
'la': 'Latin'
'es': 'Spanish'
'de': 'German'
'fr': 'French'
'it': 'Italian'
'ru': 'Russian'
'ar': 'Arabic'
'id': 'Indonesian'
'ms': 'Malaysian'
'th': 'Thai'
'vi': 'Vietnamese'
'tl': 'Tagalog'
}

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
            print("test, /register input: username:", request.form.get("username") ," hash:", newpass," tgtlang:", tgtlang," orglang:", 
                orglang, " autotrans (raw):", request.form.get("autotrans")," autotrans (if/else):", autotrans)            
            db.execute("INSERT INTO users (username, hash, tgtlang, orglang, autotrans, wordcount, pincount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                request.form.get("username"), newpass, tgtlang, orglang, autotrans, 0, 0)            
            flash("User registered", category="message")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:   
        # Show page if no user is not logged-in     
        if not session:                    
            return render_template("register.html")
        # Redirect user to home page if already logged in
        else:            
            return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    # NOTE - LOGIN DEFINITION ORIGINALLY FROM CS50PSET9, WITH MODIFICATIONS
    """Log user in"""

    # Forget any userid
    session.clear()

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # NOTE/TODO: temporary code to block none "tester" accounts
        if not request.form.get("username") == "tester":
            return apology("Unauthorized Access", 401)

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        usertable = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        # PRINT TEST BLOCK
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

        # Update current display time - display format: dd/mm/YY H:M:S
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

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # Redirect user to login form
    return redirect("/")

@app.route("/profile")
@login_required
def profile():
    # NOTE/TODO FROM CS50PSET9 SUBMISSION, REVISE AS NECESSARY LATER !!!
    """Profile Page"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    return render_template("profile.html")

@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    # NOTE/TODO FROM CS50PSET9 SUBMISSION, REVISE AS NECESSARY LATER !!!
    """Change Password Page"""

    # Update current display time - display format: dd/mm/YY H:M:S
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

@app.route("/changedefault", methods=["GET", "POST"])
@login_required
def changedefault():
    # NOTE/TODO FROM CS50PSET9 SUBMISSION, REVISE AS NECESSARY LATER !!!
    """Change Settings Page"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Change autotrans value to true/false        
        if request.form.get("autotrans"):
            varautotrans = True
        else:
            varautotrans = False   

        # PRINT TEST BLOCK        
        print("log: current default orglang is ", session["user_orglang"], ", new default orglang is ", request.form.get("originlang"))       
        print("log: current default tgtlang is ", session["user_tgtlang"], ",  new default tgtlang is ", request.form.get("targetlang"))
        print("log: current default autotrans is ", session["user_autotrans"], ", new default autotrans is ", varautotrans)

        # Update User Settings
        db.execute(
            "UPDATE users SET orglang =?, tgtlang = ?, autotrans = ? WHERE userid = ?",
            request.form.get("originlang"), request.form.get("targetlang"), varautotrans, session["user_id"]
        )

       # Update session[] array
        session["user_tgtlang"] = request.form.get("targetlang")
        session["user_orglang"] = request.form.get("originlang")
        session["user_autotrans"] = request.form.get("autotrans")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changedefault.html")

@app.route("/")
@login_required
def index():
    # NOTE - INDEX DEFINITION ORIGINALLY FROM CS50PSET9, WITH MODIFICATIONS
    """Show INDEX.html"""
    
    # RETRIEVE FROM DATABASE
    # CS50 EXECUTE METHOD NOTE: If str is a SELECT, then execute returns a list of zero or more dict objects, 
    #   inside of which are keys and values representing a table’s fields and cells, respectively.
    # NOTE: user table info (name/id + tgtlang/orglang/autotrans + wordcount/pincount) are saved in session[] array (initially in /login, updated as required)
    # NOTE: vocab table = wordid, userlink, strinput, strtrans, langinput, langtrans, time, rating, pin
    usertable = db.execute("SELECT * FROM users WHERE userid = ?", session["user_id"])
    vocabtable = db.execute("SELECT * FROM vocab where userlink = ?", session["user_id"])        
    
    # Update session[] array based on "user" table on database (directly copied from /login route)
    # user_tgtlang/orglang/autotrans are used for layout display, and are dynamic (manually changed in profile options)
    session["user_tgtlang"] = usertable[0]["tgtlang"]
    session["user_orglang"] = usertable[0]["orglang"]
    session["user_autotrans"] = usertable[0]["autotrans"]
    # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
    session["user_wordcount"] = usertable[0]["wordcount"]
    session["user_pincount"] = usertable[0]["pincount"]

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 
    
    # Create empty list, to populate with *list of dictionaries*
    allvocabtable = []
    pinvocabtable = []
    allcount = 25
    pincount = 10

    # PRINT TEST BLOCK
    #print("test, vocabtable[{}]: ", vocabtable)
    #print("test, allvocabtable (before): ", allvocabtable)
    #print("test, pinvocabtable (before): ", pinvocabtable)
    
    # Filter out for allvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    # TODO: limit to 25
    for vocabtable_list in vocabtable:
        #print("test, vocabtable_list (list-of-dict): ", vocabtable_list)
        testvtlist = vocabtable_list.items()                        
        # NOTE: go through all key/value pairs and search if they're for the current user
        for (vt_key, vt_value) in testvtlist:                        
            #print("test, vt_key (", vt_key, ") + vt_value(", vt_value, ")")
            #print("test, allcount: ", allcount)
            
            # NOTE: check if allcount is still > 0
            if allcount > 0:
                if vt_key == "userlink" and vt_value == session["user_id"]:
                    #print("log: userlink match")                                   
                    
                    # NOTE: go through all key/value pairs and search if they're pinned or not
                    for (vt_key, vt_value) in testvtlist:                                        
                        if vt_key == "pin" and vt_value == False:
                            #print("log: pinned=False match")
                            #print("test, vocabtable_list (dict): ", vocabtable_list)
                            allvocabtable.append(vocabtable_list)
                            #print("test, allvocabtable.append: ", allvocabtable)
                            # NOTE: subtract 1 from allcount
                            allcount = allcount - 1
            else:
                # End loop once 25 entries have been detected
                #print("log: function break due to allcount at ", allcount)
                break            
    #print("test, allvocabtable (after): ", allvocabtable)

    # Filter out for pinvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    for vocabtable_list in vocabtable:
        #print("test, vocabtable_list (list-of-dict): ", vocabtable_list)
        testvtlist = vocabtable_list.items()                
        
        # NOTE: go through all key/value pairs and search if they're for the current user
        for (vt_key, vt_value) in testvtlist:                        
            #print("test, vt_key (", vt_key, ") + vt_value(", vt_value, ")")
            #print("test, pincount: ", pincount)

            # NOTE: check if pincount is still > 0
            if pincount > 0:
                if vt_key == "userlink" and vt_value == session["user_id"]:
                    #print("log: userlink match")         

                    for (vt_key, vt_value) in testvtlist:
                    # NOTE: go through all key/value pairs and search if they're pinned or not
                        if vt_key == "pin" and vt_value == True:
                            #print("log: pin=True match")
                            #print("test, vocabtable_list (dict): ", vocabtable_list)
                            pinvocabtable.append(vocabtable_list)
                            #print("test, pinvocabtable.append: ", pinvocabtable)
                            # NOTE: subtract 1 from pincount
                            pincount = pincount - 1
            else:
                # End loop once 30 entries have been detected
                #print("log: function break due to pincount at ", pincount)
                break  
    #print("test, pinvocabtable (after): ", pinvocabtable)

    return render_template("index.html", vocabtable=vocabtable, allvocabtable=allvocabtable, pinvocabtable=pinvocabtable)

@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    """Show INPUT.html"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure word/phrase was submitted
        if not request.form.get("textinput"):
            return apology("must provide word/phrase to record and/or translate", 400)
        
        # Initialize an empty dictionary
        translation = {}

        # Lookup translation if check-box selected
        if request.form.get("autotrans"):
            # Use googletrans library
            # NOTE: class googletrans.models.Translated(src, dest, origin, text, pronunciation, extra_data=None, **kwargs)            
            
            # Use translator function
            translator = Translator()            
            translated = translator.translate(request.form.get("textinput"), src = request.form.get("originlang"), dest = request.form.get("targetlang"))
            
            # Add values to translation dictionry (to pass to review.html)
            translation["input"] = request.form.get("textinput")
            translation["output"] = translated.text
            translation["org"] = translated.src
            translation["tgt"] = translated.dest

            # PRINT TEST BLOCK        
            print("test, input: ", translation["input"])
            print("test, orglang: ", translation["org"])
            print("test, tgtlang: ", translation["tgt"])
            print("test, output(object): ", translated)
            print("test, output(word): ", translation["output"])
            print("log: default orglang is ", session["user_orglang"], "and default tgtlang is ", session["user_tgtlang"])       

        else:
            # Add values to translation dictionary (to pass to review.html)
            translation["input"] = request.form.get("textinput")
            translation["output"] = "n/a (not translated)"
            translation["org"] = request.form.get("originlang")
            translation["tgt"] = "n/a"

            # PRINT TEST BLOCK        
            print("test, input: ", translation["input"])
            print("test, orglang: ", translation["org"])
            print("test, tgtlang: ", translation["tgt"])
            print("log: autotranslation option is not selected, ignoring input string '", request.form.get("textinput"), "'")
            print("log: default orglang is ", session["user_orglang"], "and default tgtlang is ", session["user_tgtlang"])       
        
        # Save translation data to shadow table
        # NOTE: shadow table = shawordid, shauserlink, shastrinput, shastrtrans, shalanginput, shalangtrans, shatime, sharating, shapin
        # NOTE: "pin" value set to 0 to distinguish it from form-submitted ratings of 1-3
        db.execute(
            "INSERT INTO shadow (shauserlink, shastrinput, shastrtrans, shalanginput, shalangtrans, shatime, sharating, shapin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            session["user_id"], translation["input"], translation["output"], translation["org"], translation["tgt"], datetime.now(), 0, False
        )
        
        # Redirect to review.html
        return render_template("review.html", translation=translation)

    # User reached route via GET (as by clicking a link or via redirect)
    else:   
        return render_template("input.html")

@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    """Show REVIEW.html"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # NOTE: only /review route should not purge shadow table

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get a copy of translation data in shadow table and wordcount/pincount from user table
        shadowcopy = db.execute("SELECT * FROM shadow WHERE shauserlink = ?", session["user_id"])      
        usernumbers = db.execute("SELECT pincount, wordcount FROM users WHERE userid = ?", session["user_id"])
                
        # Change inputpin value to true/false        
        if request.form.get("inputpin") == "true":
            varinputpin = True
            # Update user table wordcount and pincount
            db.execute(
                "UPDATE users SET wordcount = ?, pincount = ? WHERE userid = ?",
                usernumbers[0]["wordcount"] + 1, usernumbers[0]["pincount"] + 1, session["user_id"]
            )
        else:
            varinputpin = False
            # Update user table wordcount only
            db.execute(
                "UPDATE users SET wordcount = ? WHERE userid = ?",
                usernumbers[0]["wordcount"] + 1, session["user_id"]
            )     

        # Update session[] array based on "user" table on database (directly copied from /login route)
        # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
        session["user_wordcount"] = usernumbers[0]["wordcount"] + 1
        session["user_pincount"] = usernumbers[0]["pincount"] + 1

        # Print Test
        print("test, shadowcopy[0]: ", shadowcopy[0])
        print("test, difficulty: ", request.form.get("difficulty"))
        print("test, inputpin (raw):", request.form.get("inputpin"))
        print("test, inputpin (cleaned):", varinputpin)
        
        # Insert values from shadowcopy to vocab table, but utilize difficulty/inputpin values from review.html
        db.execute(
            "INSERT INTO vocab (userlink, strinput, strtrans, langinput, langtrans, time, rating, pin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            shadowcopy[0]["shauserlink"], shadowcopy[0]["shastrinput"], shadowcopy[0]["shastrtrans"], 
            shadowcopy[0]["shalanginput"], shadowcopy[0]["shalangtrans"], shadowcopy[0]["shatime"], 
            request.form.get("difficulty"), varinputpin
        )

        # Purge shadow table after every successful insertion to vocab table
        db.execute("DELETE FROM shadow") 

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # /review should not be directly accessible (redirect to /input instead)
        return redirect("/input") 

@app.route("/recallall")
@login_required
def recallall():
    """Show RECALLALL.html"""

    # RETRIEVE FROM DATABASE
    # CS50 EXECUTE METHOD NOTE: If str is a SELECT, then execute returns a list of zero or more dict objects, 
    #   inside of which are keys and values representing a table’s fields and cells, respectively.
    # NOTE: user table info (name/id + tgtlang/orglang/autotrans + wordcount/pincount) are saved in session[] array (initially in /login, updated as required)
    # NOTE: vocab table = wordid, userlink, strinput, strtrans, langinput, langtrans, time, rating, pin
    usertable = db.execute("SELECT * FROM users WHERE userid = ?", session["user_id"])
    vocabtable = db.execute("SELECT * FROM vocab where userlink = ?", session["user_id"])        
    
    # Update session[] array based on "user" table on database (directly copied from /login route)
    # user_tgtlang/orglang/autotrans are used for layout display, and are dynamic (manually changed in profile options)
    session["user_tgtlang"] = usertable[0]["tgtlang"]
    session["user_orglang"] = usertable[0]["orglang"]
    session["user_autotrans"] = usertable[0]["autotrans"]
    # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
    session["user_wordcount"] = usertable[0]["wordcount"]
    session["user_pincount"] = usertable[0]["pincount"]

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # Create empty list, to populate with *list of dictionaries*
    fullvocabtable = []

    # PRINT TEST BLOCK
    #print("test, vocabtable[{}]: ", vocabtable)
    #print("test, fullvocabtable (before): ", fullvocabtable)
    
    # Filter out for fullvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    for vocabtable_list in vocabtable:
        #print("test, vocabtable_list (list-of-dict): ", vocabtable_list)
        testvtlist = vocabtable_list.items()                        
        # NOTE: go through all key/value pairs and search if they're for the current user
        for (vt_key, vt_value) in testvtlist:                        
            if vt_key == "userlink" and vt_value == session["user_id"]:
                #print("log: userlink match")                
                #print("test, vocabtable_list (dict): ", vocabtable_list)
                fullvocabtable.append(vocabtable_list)
                #print("test, fullvocabtable.append: ", fullvocabtable)
    #print("test, fullvocabtable (after): ", fullvocabtable)

    return render_template("recallall.html", fullvocabtable=fullvocabtable)

@app.route("/recallpin")
@login_required
def recallpin():
    """Show RECALLPIN.html"""

    # RETRIEVE FROM DATABASE
    # CS50 EXECUTE METHOD NOTE: If str is a SELECT, then execute returns a list of zero or more dict objects, 
    #   inside of which are keys and values representing a table’s fields and cells, respectively.
    # NOTE: user table info (name/id + tgtlang/orglang/autotrans + wordcount/pincount) are saved in session[] array (initially in /login, updated as required)
    # NOTE: vocab table = wordid, userlink, strinput, strtrans, langinput, langtrans, time, rating, pin
    usertable = db.execute("SELECT * FROM users WHERE userid = ?", session["user_id"])
    vocabtable = db.execute("SELECT * FROM vocab where userlink = ?", session["user_id"])        
    
    # Update session[] array based on "user" table on database (directly copied from /login route)
    # user_tgtlang/orglang/autotrans are used for layout display, and are dynamic (manually changed in profile options)
    session["user_tgtlang"] = usertable[0]["tgtlang"]
    session["user_orglang"] = usertable[0]["orglang"]
    session["user_autotrans"] = usertable[0]["autotrans"]
    # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
    session["user_wordcount"] = usertable[0]["wordcount"]
    session["user_pincount"] = usertable[0]["pincount"]

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # Create empty list, to populate with *list of dictionaries*
    pinnedvocabtable = []

    # PRINT TEST BLOCK
    #print("test, vocabtable[{}]: ", vocabtable)
    #print("test, pinnedvocabtable (before): ", pinnedvocabtable)
    
    # Filter out for pinnedvocabtable
    # NOTE: go through all dictionary items within the list that db.execute returns
    for vocabtable_list in vocabtable:
        #print("test, vocabtable_list (list-of-dict): ", vocabtable_list)
        testvtlist = vocabtable_list.items()                        
        # NOTE: go through all key/value pairs and search if they're for the current user
        for (vt_key, vt_value) in testvtlist:                        
            if vt_key == "userlink" and vt_value == session["user_id"]:
                #print("log: userlink match")                                
                # NOTE: go through all key/value pairs and search if they're pinned or not
                for (vt_key, vt_value) in testvtlist:                
                    if vt_key == "pin" and vt_value == True:
                        #print("log: pin=True match")
                        #print("test, vocabtable_list (dict): ", vocabtable_list)
                        pinnedvocabtable.append(vocabtable_list)
    #print("test, pinnedvocabtable (after): ", pinnedvocabtable)

    return render_template("recallpin.html", pinnedvocabtable=pinnedvocabtable)

@app.route("/deletecheck", methods=["GET", "POST"])
@login_required
def deletecheck():
    """Show DELETE.html"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        print("log: /deletecheck-POST reached")
        deletiontable = db.execute("SELECT * FROM vocab where wordid = ?", request.form.get("deleteword"))
        print("test, deletiontable[0]: ", deletiontable[0])
        # Redirect to /deletion
        return render_template("delete.html", deletiontable=deletiontable)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("log: /deletecheck-GET reached")
        # /deletion should not be directly accessible (redirect to /input instead)
        return redirect("/input") 

@app.route("/deletion", methods=["GET", "POST"])
@login_required
def deletion():
    """Enact deletion (behind the scenes)"""

    # Update current display time - display format: dd/mm/YY H:M:S
    session["current_time"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Purge shadow table to ensure no errant entries
    db.execute("DELETE FROM shadow") 

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        print("log: /deletion-POST reached")
        deletiontable = db.execute("SELECT * FROM vocab where wordid = ?", request.form.get("confirmdelete"))
        usernumbers = db.execute("SELECT pincount, wordcount FROM users WHERE userid = ?", session["user_id"])
        print("test, deletiontable[0]: ", deletiontable[0])

        # Check if deleted entry is pinned/not
        if deletiontable[0]["pin"] == True:
            # Update user table wordcount and pincount
            db.execute(
                "UPDATE users SET wordcount = ?, pincount = ? WHERE userid = ?",
                usernumbers[0]["wordcount"] - 1, usernumbers[0]["pincount"] - 1, session["user_id"]
            )
        else:
            # Update user table wordcount only
            db.execute(
                "UPDATE users SET wordcount = ? WHERE userid = ?",
                usernumbers[0]["wordcount"] - 1, session["user_id"]
            )     

        # Update session[] array based on "user" table on database (directly copied from /login route)
        # user_allcount/pincount are also used for layout display, and are dynamic (automatically increased/decreased)
        session["user_wordcount"] = usernumbers[0]["wordcount"] - 1
        session["user_pincount"] = usernumbers[0]["pincount"] - 1
        
        # Delete entry from vocab table
        db.execute("DELETE FROM vocab WHERE wordid = ?", request.form.get("confirmdelete"))  
        
        # Redirect to index.html
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("log: /deletion-GET reached")
        # /deletion should not be directly accessible (redirect to /input instead)
        return redirect("/input") 

# NOTE CS50PSET9 BASE CODE BELOW RETAINED
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# TODO: add new functionality