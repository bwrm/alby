from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'ACcdf985d46bc2ddc5eabcdf6abbda428d'
auth_token = '88fb8e4a0dc6c85d34347980f12453b0'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+13344580572',
                     to='+375293779514'
                 )

print(message.sid)
