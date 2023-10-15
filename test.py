from twilio.rest import Client

# Your Twilio Account SID and Auth Token
account_sid = "ACf2494ab3a07460275fd6ee36411b1c15"
auth_token = "7e1bf68864242a870e849716f8790c50"

# Create a Twilio client
client = Client(account_sid, auth_token)

# Your Twilio phone number (get it from your Twilio account)
twilio_phone_number = "+17606218054"

# Recipient phone number in India (format: +91XXXXXXXXXX)
recipient_phone_number = "+919717290637"  # Replace with the recipient's phone number

# Message to send
message = client.messages.create(
    body="Bhukamp, Bhago bc.",
    from_=twilio_phone_number,
    to=recipient_phone_number
)

print("Message SID:", message.sid)
