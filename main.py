from __future__ import with_statement   # Only necessary for Python 2.5
from flask import Flask, request, redirect, render_template
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from twilio.rest import Client
from user import User
from google.appengine.api import taskqueue  # Tasks
import time
import logging


app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None).lower()
    timestamp = str(datetime.now())

    logging.log(logging.INFO, "incoming_sms: " + from_number + " " + body)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'call':
        resp.message("Alright! We're going to connect you with someone as soon as possible. We'll send some conversation starters, and we'll call you when we're ready!")
        resp.message('CONVERSATION STARTERS: What is your neighborhood like?')
        user = User.get_user(from_number)
        if not user:
            user = User.create_user("markus aurielous", from_number, True)
        else:
            User.add_to_queue(user)
        if not user:
            logging.log(logging.INFO, "incoming_sms: " + str(user))
        logging.log(logging.INFO, "incoming_sms: " + user.phonenumber)
        if User.check_queue():
            call(from_number)
    elif body == 'start':
        resp.message("Welcome to TinCan! When you're ready to start a call, please text the word CALL.")
    else:
        resp.message("Sorry, I didn't understand that. Try either START or CALL")

    return str(resp)

@app.route("/call", methods=["POST"])
def call_handler():
    logging.log(logging.INFO, "call_handler:")
    from_number = request.values.get("To", None)
    User.remove_user_from_queue(from_number)

    resp = VoiceResponse()
    # Greet the caller by name
    resp.say("Hello user")

    # Say a command, and listen for the caller to press a key. When they press
    # a key, redirect them to /handle-key.
    g = Gather(numDigits=1, action="/handle-key", method="POST")
    g.say("To connect to the other Tin Can user, press 1. Press any other key to start over.")
    resp.append(g)

    return str(resp)

@app.route("/celia", methods=["POST"])
def calling_your_mom():

    from_number = request.values.get("from", None)
    logging.log(logging.INFO, "calling_your_mom: " + from_number)

    account_sid = "AC9d771823f9faeac7a14c1dc6aa61b575"
    auth_token = "3844c8588ee16a4c6c41af767dd03cc7"

    logging.log(logging.INFO, from_number)
    client = Client(account_sid, auth_token)

    call = client.calls.create(to=from_number, from_="+15104471108", url="https://code2040hack-tincan.appspot.com/call")
    logging.log(logging.INFO, from_number)

    return "Hola"

@app.route("/handle-key", methods=["POST"])
def handle_key():
    """Handle key press from a user."""

    # Get the digit pressed by the user
    digit_pressed = request.values.get("Digits", None)
    # BUGG: can't get number from reuqest body
    # from_number = request.value.get("From", None)
    if digit_pressed == "1":
        resp = VoiceResponse()
        user = User.pop_queue()
        if not user:
            logging.log(logging.INFO, "handle_key: " + str(user))
            return "no one else in queue"
        logging.log(logging.INFO, "handle_key: " + user.phonenumber)
        # Dial number - connect that number to the incoming caller.
        resp.dial(user.phonenumber)
        # If the dial fails:
        resp.say("The call failed, or the remote party hung up. Goodbye.")

        return str(resp)

    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        return redirect("/")

@app.route('/create/<name>/<number>')
def create_user(name, number):
    user = User.create_user(name, number, False)
    key = user.put()
    return 'Created user: ' + str(key)

@app.route('/add/<number>')
def add_to_queue(number):
    user = User.get_user(number)
    if not user:
        return 'No matching user with phonenumber ' + number
    User.add_to_queue(user)
    queue = User.get_queue()
    names = queue_to_string(queue)
    return 'New queue: ' + names

@app.route('/remove/<number>')
def remove_from_queue(number):
    user = User.get_user(number)
    if not user:
        return 'No matching user with phonenumber ' + number
    User.remove_from_queue(user)
    queue = User.get_queue()
    names = queue_to_string(queue)
    return 'New queue: ' + names

@app.route('/queue')
def print_queue():
    queue = User.get_queue()
    names = queue_to_string(queue)
    return 'Queue: ' + names

def queue_to_string(queue):
    names = '</br>'
    for user in queue:
        names += user.name + ' '
        names += user.queue_join_date.strftime('%x %X') + '</br>'
    return names

def call(from_number):
    logging.log(logging.INFO, from_number)
    task = taskqueue.add(
        url='/celia',
        target='main',
        params={'from': from_number})


if __name__ == "__main__":
    app.run(debug=True)
