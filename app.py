import os
from flask import Flask
if os.path.exists("env.py"):
    import env

# In order to use our environment variables,
# we need to import the 'env' package.
# Since we are not going to push the env.py file to GitHub,
# once our app is deployed to
# Heroku, it won't be able to find the
# env.py file, so it will throw an error.
# This is why we need to only import env if the os
# can find an existing file path for
# the env.py file itself.

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World ... again!"


# tell app how or where to run our application (in what port)
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

