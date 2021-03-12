import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo  # installation difference
# had to pip3 install flask_pymongo
from bson.objectid import ObjectId  # render the ObjectId
# import werkzeug password checks
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# ^ In order to use our environment variables,
# we need to import the 'env' package.
# Since we are not going to push the env.py file to GitHub,
# once our app is deployed to
# Heroku, it won't be able to find the
# env.py file, so it will throw an error.
# This is why we need to only import env if the os
# can find an existing file path for
# the env.py file itself.

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")  # grab db name
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")  # get url
app.secret_key = os.environ.get("SECRET_KEY")

# This is the Flask 'app' object we've defined above,
# and is the final step to ensure our
mongo = PyMongo(app)


# routing is a string that, when we attach it
# to a URL, will redirect to a particular function in our Flask app.
# particular function in our Flask app.
@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    tasks = list(mongo.db.tasks.find())  # gen data from tasks coll
    return render_template("tasks.html", tasks=tasks)  # template we render
    # first tasks is = to 2nd tasks which is the tasks passed into it


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
             # want to include 2nd confirm password field, do it here
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        # Redirect a user to their profile after registering
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
        # Redirect a user to their profile after registering
                        return redirect(url_for(
                          "profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    # 1st username is what template is expecting to retrieve on html
    # 2nd is what we've defined on the line above
    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Remove user from session cookies
    flash('You have been logged out')
    # session.clear() clears all user sessions
    session.pop('user')
    return redirect(url_for('login')) # show link for login


@app.route("/add_task")
def add_task():
    return render_template("add_task.html")


# tell app how or where to run our application (in what port)
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
