from __future__ import with_statement 
from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

callers = {
	"+14158675311": "Virgil",
	"+14158675309": "Curious George",
	"+14158675310": "Boots",
	"+14158675312": "Marcel"
}

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	from_number = request.values.get('From', None)
	if from_number in callers:
		caller = callers[from_number]
	else:
		caller = "Tin Can User"

	resp = VoiceResponse()
	# Greet the caller by name
	resp.say("Hello " + caller)

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
		# Dial Teresa - connect that number to the incoming caller.
		resp.dial("+14158670706")
		# If the dial fails:
		resp.say("The call failed, or the remote party hung up. Goodbye.")

		return str(resp)

	# If the caller pressed anything but 1, redirect them to the homepage.
	else:
		return redirect("/")

if __name__ == "__main__":
	app.run(debug=True)
