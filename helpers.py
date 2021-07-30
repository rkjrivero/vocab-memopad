### NOTE / DISCLAIMER: GENERAL APPLICATION FOUNDATION IS BUILT UPON THE HELPERS.PY FILE OF CS50 PSET 9
from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):    
    # NOTE - APOLOGY DEFINITION ORIGINALLY FROM CS50PSET9, WITHOUT MODIFICATIONS
    """Render message as an apology to user."""    
    
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):    
    # NOTE - LOGIN_REQUIRED DEFINITION ORIGINALLY FROM CS50PSET9, WITHOUT MODIFICATIONS
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function