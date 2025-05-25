import os
from flask import Flask, render_template, request, redirect, session
from zenora import APIClient
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("CLIENT_TOKEN")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OAUTH_URL = os.getenv("OAUTH_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")
app = Flask(__name__)
client = APIClient(BOT_TOKEN, client_secret=CLIENT_SECRET)

app.config["SECRET_KEY"] = "verysecret69"


@app.route("/")
def home():
    access_token = session.get("access_token")

    if not access_token:
        return render_template("index.html")

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    print(current_user.discriminator)
    return render_template("index.html", user=current_user)


@app.route("/login")
def login():
    return redirect(OAUTH_URL)


@app.route("/logout")
def logout():
    session.pop("access_token")
    return redirect("/")


@app.route("/oauth/callback")
def oauth_callback():
    arguments = request.args
    if not "error" in arguments:
        code = arguments["code"]
        access_token = client.oauth.get_access_token(
            code, redirect_uri=REDIRECT_URI
        ).access_token
        session["access_token"] = access_token
        return redirect("/")
    else:
        return redirect("/")


def run():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


def keep_alive():
    t = Thread(target=run)
    t.start()
