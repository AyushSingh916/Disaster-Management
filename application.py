import os
import datetime

from flask import Flask, render_template, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from twilio.rest import Client

import sqlite3

conn = sqlite3.connect("alerts.db", check_same_thread=False)
db = conn.cursor()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Function to read Twilio credentials from the password file
def read_twilio_credentials(filename="password.txt"):
    twilio_credentials = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                key, value = line.strip().split(": ")
                twilio_credentials[key] = value
        return twilio_credentials
    except FileNotFoundError:
        return None

# Read Twilio credentials from the password file
twilio_auth = read_twilio_credentials()
if not twilio_auth or "TWILIO_CLIENT_SID" not in twilio_auth or "TWILIO_AUTH_TOKEN" not in twilio_auth:
    raise Exception("Twilio credentials not found in password file")

# Extract Twilio Account SID and Auth Token
account_sid = twilio_auth["TWILIO_CLIENT_SID"]
auth_token = twilio_auth["TWILIO_AUTH_TOKEN"]

# Create a Twilio client
client = Client(account_sid, auth_token)


# Function to send an SMS
def send_sms(recipient_number, message):
    try:
        message = client.messages.create(
            to=recipient_number,  
            from_="+17606218054",  # Use your Twilio phone number
            body=message,
        )
        print(f"Message sent to {recipient_number} successfully.")
        return f"Message sent to {recipient_number} successfully."
    except Exception as e:
        print(f"Message sending to {recipient_number} failed: {str(e)}")
        return f"Message sending to {recipient_number} failed: {str(e)}"


# Read phone numbers from the text file
with open("phone_numbers.txt", "r") as file:
    phone_numbers = file.read().splitlines()


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/commonalerts", methods=["GET", "POST"])
def commonalerts():
    if request.method == "POST":
        if not request.form.get("calamity"):
            return "Must enter the calamity."
        elif not request.form.get("location"):
            return "Must enter the location"

        c = request.form.get("calamity")
        l = request.form.get("location")
        d = request.form.get("description")
        s = {"success": "yes"}
        db.execute(
            "INSERT INTO commonalerts (calamity, location, description) VALUES (?,?,?)",
            (c, l, d),
        )
        conn.commit()
        return "Alert Issued Successfully.", 200
    else:
        return render_template("alerts.html")


@app.route("/getcommonalerts")
def getcommonalerts():
    alerts = []
    w = db.execute("SELECT * FROM commonalerts ORDER BY id DESC ")
    for w1 in w:
        s = {
            "datetime": w1[1],
            "location": w1[3],
            "calamity": w1[2],
            "description": w1[4],
        }
        alerts.append(s)
    return jsonify(alerts)


@app.route("/govtalerts", methods=["GET", "POST"])
def govtalerts():
    if request.method == "POST":
        if not request.form.get("username"):
            return "Must enter a username"
        elif not request.form.get("password"):
            return "Must enter the password"
        elif not request.form.get("calamity"):
            return "Must enter the calamity"
        elif not request.form.get("location"):
            return "Must enter the location"
        elif not request.form.get("description"):
            return "Must enter the description"

        username = request.form.get("username")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM govtids WHERE username = ?", (username,))
        row = db.fetchone()
        if row is None or not check_password_hash(row[2], request.form.get("password")):
            return "Invalid username and/or password"

        c = request.form.get("calamity")
        l = request.form.get("location")
        d = request.form.get("description")
        s = {"success": "yes"}

        db.execute(
            "INSERT INTO govtalerts (calamity, location, description) VALUES (?,?,?)",
            (c, l, d),
        )
        conn.commit()

        # Send alert messages to everyone in phone_numbers.txt
        alert_message = f"Government Alert: {c} in {l}. {d}"
        for number in phone_numbers:
            result = send_sms(number, alert_message)

        return "Alert Issued Successfully.", 200
    else:
        return render_template("govtalerts.html")


@app.route("/getgovtalerts")
def getgovtalerts():
    alerts = []
    w = db.execute("SELECT * FROM govtalerts ORDER BY id DESC ")
    for w1 in w:
        s = {
            "datetime": w1[1],
            "location": w1[3],
            "calamity": w1[2],
            "description": w1[4],
        }
        alerts.append(s)
    return jsonify(alerts)


@app.route("/viewgovtalerts")
def viewgovtalerts():
    alerts = []
    w = db.execute("SELECT * FROM govtalerts ORDER BY id DESC ")
    for w1 in w:
        s = {
            "datetime": w1[1],
            "location": w1[3],
            "calamity": w1[2],
            "description": w1[4],
        }
        alerts.append(s)
    return render_template("view.html", rows=alerts, alert="Government Issued Alerts")


@app.route("/viewcommonalerts")
def viewcommonalerts():
    alerts = []
    w = db.execute("SELECT * FROM commonalerts ORDER BY id DESC ")
    for w1 in w:
        s = {
            "datetime": w1[1],
            "location": w1[3],
            "calamity": w1[2],
            "description": w1[4],
        }
        alerts.append(s)
    return render_template("view.html", rows=alerts, alert="Common Alerts")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
