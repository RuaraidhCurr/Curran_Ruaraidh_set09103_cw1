from flask import Flask, request, render_template, url_for, g, flash, redirect, session
from logging import FileHandler, WARNING
import sqlite3 as sql

app = Flask(__name__)
file_handler = FileHandler("./static/errorlog.txt")
file_handler.setLevel(WARNING)

app.logger.addHandler(file_handler)

# ERROR LOG TEST
# @app.route("/errortest/")
# def errortest():
#     return 1 / 0

DATABASE = "films.db"

# Helper Functions
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def verified_login(username, password):
    with sql.connect("films.db") as db:
        cur = db.cursor()
        find_user = ("select * from users where username = ? and password = ?")
        cur.execute(find_user, [username, password])
        data = cur.fetchone()
        if data:
            return True
        else:
            return False


def new_user(username):
    with sql.connect("films.db") as db:
        userData = None
        cur = db.cursor()
        findUser = ("select * from users where username = ?")
        cur.execute(findUser, [username])
        userData = cur.fetchall()
        # checks and sees if there is any userdata matching
        if userData:
            return True
        else:
            return False

# create account url


@app.route("/registeruser/")
@app.route("/newuser/")
@app.route("/createnewuser/")
@app.route("/register/")
def register():
    return render_template("register.html")


@app.route("/")
@app.route("/start/")
@app.route("/main/")
def route():
    if "username" in session:
        return redirect(url_for('home'))
    else:
        flash("Please Log in or register new user account")
        return redirect(url_for("login"))


@app.route("/registeruser", methods=["GET", "POST"])
def registeruser():
    db = get_db()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        varpass = request.form["varpass"]
        if password == varpass:
            if new_user(username):
                flash("Username allready Found")
                # redirects user to the login page
                return redirect(url_for("login"))
            else:
                with sql.connect("films.db") as db:
                    cur = db.cursor()
                    cur.execute(
                        "insert into users (username, password) values (?,?)", (username, password))
                    db.commit()
                    flash("User account Registered!     Please Log in")
            return redirect(url_for("login"))
        else:
            flash("passwords did not match, Please try again")
            return redirect("register")

    else:
        flash("Please Log in or register new user account")
    return redirect(url_for("login"))

#Log in screen


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Checks to see if the sucessful login params were met
        if verified_login(request.form["username"], request.form["password"]):
            # stores flash message for sucseful login
            flash("Login Succseful")
            # stores username in username session
            session["username"] = request.form["username"]
            return redirect(url_for("home"))
        else:
            flash("Invalid username and/or passwords")
    return render_template("login.html")


@app.route("/Films/logout/")
@app.route("/Film/logout/")
@app.route("/films/logout/")
@app.route("/film/logout/")
@app.route("/addfilmresult/logout")
@app.route("/main/logout/")
@app.route("/home/logout/")
@app.route("/logout")
def logout():
    # deletes the session
    session.pop("username", None)
    # redirects to login
    return redirect(url_for("login"))


@app.route("/Home/")
@app.route("/home")
def home():
    # if the session has a username stores in warningit
    if "username" in session:
        # gets username from session
        return render_template("home.html", username=session["username"])
    else:
        flash("Please log in or create account!")
        return redirect(url_for("login"))


@app.route("/home/addfilms/")
@app.route("/home/addfilm/")
@app.route("/addfilm/")
@app.route("/addfilms/")
def addfilm():
    if "username" in session:
        return render_template("addfilm.html")
    else:
        flash("Please Log in")
        return redirect(url_for("login"))


@app.route("/addfilmresult/", methods=["GET", "POST"])
def addfilmresult():
    if "username" in session:
        db = get_db()
        if request.method == "POST":
            try:
                title = request.form["title"]
                year = request.form["year"]
                genre = request.form["genre"]
                run_time = request.form["run_time"]
                director = request.form["director"]

                with sql.connect('films.db') as db:
                    cur = db.cursor()
                    cur.execute("insert into films (title,year,genre,run_time,director) values (?,?,?,?,?)", (
                        title, year, genre, run_time, director))
                    db.commit()
                    flash("Film added to database!")
            except:
                db.rollback()
                flash(
                    "Error with insert oporation: Please make sure you are not entering the same data more than once")

            finally:
                db.close()
                return redirect(url_for('home'))
    else:
        flash("Please Log in")
        return redirect(url_for("login"))


@app.route("/filmslist/")
@app.route("/films/")
@app.route("/filmlist/")
def filmlist():
    if "username" in session:
        db = get_db()
        db.row_factory = sql.Row

        cur = db.cursor()
        cur.execute("select * from films")
        header = "Films in database!"
        rows = cur.fetchall()
        return render_template("films.html", rows=rows, header=header)
    else:
        flash("Please Log in")
        return redirect(url_for("login"))


@app.route("/query/films")
@app.route("/query/film")
@app.route("/search/film")
@app.route("/search/query")
@app.route("/search")
@app.route("/query")
def query():
    if "username" in session:
        return render_template("queryfilm.html")
    else:
        flash("Please Log in")
        return redirect(url_for("login"))


@app.route("/queryresult/", methods=["GET", "POST"])
def queryresult():
    if "username" in session:
        db = get_db()
        db.row_factory = sql.Row
        cur = db.cursor()
        if request.method == "POST":
            genre = request.form["genre"]
            director = request.form["director"]
            title = request.form["title"]
            year = request.form["year"]
            max_run_time = request.form["max_run_time"]
            min_run_time = request.form["min_run_time"]
            if max_run_time == "":
                max_run_time = 500
            if min_run_time == "":
                min_run_time = 0
            cur.execute("select * from films where"
                        " (lower(title) is null or lower(title) like '%' ||?|| '%') and"
                        " (lower(genre) is null or lower(genre) like '%' ||?|| '%') and"
                        " (lower(director) is null or lower(director) like '%' ||?|| '%') and"
                        " (year is null or year like '%' ||?|| '%') and"
                        " (run_time < ?) and"
                        " (run_time > ?)",
                        [title.lower(), genre.lower(), director.lower(), year, max_run_time, min_run_time])
            rows = cur.fetchall()
            header = "Queryed Film!"
        else:
            db.rollback()
        return render_template("films.html", rows=rows, header=header)
    else:
        flash("Please Log in")
        return redirect(url_for("login"))

# Error pages


@app.errorhandler(404)
def page_not_found(error):
    if "username" in session:
        flash("Sorry that page was not found")
        return redirect(url_for('home'))
    else:
        flash("Please log in and try again")
        return redirect(url_for('login'))


if __name__ == "__main__":
    # urandom(12) passkey for sessions and cookies
    app.secret_key = "]\x17\xa7x\xba4[\\\xb9\x12\xae\x85"
    app.run()
    # debug=True
