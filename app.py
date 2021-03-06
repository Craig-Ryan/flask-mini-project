import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo  # installation difference
# had to pip3 install flask_pymongo

# we've imported ObjectId from BSON, which allows
# us to properly render MongoDB documents by their unique ID.
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

# create index in teminal as to do it inside the function 
# would store too many indexes
@app.route("/search", methods=["GET", "POST"])
def search():
    # This dictionary uses '$text', which itself is expecting another dictionary of '$search'.
    # Essentially, this means that we want to perform a '$search' on any '$text Index' for this
    query = request.form.get("query")
    tasks = list(mongo.db.tasks.find({"$text": {"$search": query}}))
    return render_template("tasks.html", tasks=tasks)

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
            "password": generate_password_hash(request.form.get("password"))}
            # want to include 2nd confirm password field, do it here
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
    return redirect(url_for('login'))  # show link for login


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":  # code runs when function is called and POST
        # set k, v pairs
        # grabs name attributes to grab data and store to DB
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.insert_one(task)  # will add request.form.to.dict later
        flash("Task successfully added!")
        return redirect(url_for("get_tasks"))

    # find categories in MongoDB and load them into app
    categories = mongo.db.categories.find().sort("category_name", 1)
    # categories are loaded with template
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":  # code runs when function is called and POST
        # set k, v pairs
        # grabs name attributes to grab data and store to DB
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit)  # will add request.form.to.dict later
        flash("Task successfully Updated!")

    # translates to BSON
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    # task var above is passed to render_template
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)

# As a reminder, this first 'categories' is what gets passed into our template to use.
# The second 'categories' is the variable defined above, what's actually being returned from
# the database.


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
  # if the POST method is called, add data to the Mongo DB DB
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

  # otherwise GET will redirect user to the add_category page
    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))
          
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)

# Will delete immediately, good idea to add def programming prompts 
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# tell app how or where to run our application (in what port)
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
