from twilio.rest import Client

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

# Your Twilio phone number (get it from your Twilio account)
twilio_phone_number = "+17606218054"

# Recipient phone number in India (format: +91XXXXXXXXXX)
recipient_phone_number = "+918178761665"  # Replace with the recipient's phone number

# Message to send
message = client.messages.create(
    body="Bhukamp, Bhago bc.",
    from_=twilio_phone_number,
    to=recipient_phone_number
)

print("Message SID:", message.sid)
