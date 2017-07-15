from __future__ import with_statement   # Only necessary for Python 2.5
from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import time
from twilio.rest import Client

app = Flask(__name__)

account_sid = "Get these from Teresa"
auth_token = "Get these from Teresa"
client = Client(account_sid, auth_token)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None).lower()
    timestamp = str(datetime.now())

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'call':
        resp.message("Alright! We're going to connect you with someone as soon as possible. We'll send some conversation starters, and we'll call you when we're ready!")
        resp.message('CONVERSATION STARTERS: What is your neighborhood like?')

        call(from_number)
    elif body == 'start':
        resp.message("Welcome to TinCan! When you're ready to start a call, please text the word CALL.")
    else:
        resp.message("Sorry, I didn't understand that.")

    return str(resp)

@app.route("/call", methods=['GET', 'POST'])
def call():
    from_number = request.values.get('From', None)

    resp = VoiceResponse()
    # Greet the caller by name
    resp.say("Hello user")

    # Say a command, and listen for the caller to press a key. When they press
    # a key, redirect them to /handle-key.
    g = Gather(numDigits=1, action="/handle-key", method="POST")
    g.say("To connect to the other Tin Can user, press 1. Press any other key to start over.")
    resp.append(g)

    return str(resp)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    """Handle key press from a user."""

    # Get the digit pressed by the user
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        resp = VoiceResponse()
        # Dial demo number - connect that number to the incoming caller.
        resp.dial("+14158670706")
        # If the dial fails:
        resp.say("The call failed, or the remote party hung up. Goodbye.")

        return str(resp)

    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        return redirect("/")

def call(from_number):
    time.sleep(60)
    call = client.calls.create(to=from_number,
                   from_="+15104471108",
                   url="https://90ed11f2.ngrok.io/call")

if __name__ == "__main__":
    app.run(debug=True)
