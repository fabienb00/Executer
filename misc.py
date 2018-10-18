from json import load as json_load
import os
import smtplib


def isint(string):
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True

try:
    const_file = open("configs/constants.json", "r")
except FileNotFoundError:
    raise FileNotFoundError("There should be a file named \'constants.json\' in teh folder, but there isn\'t")
else:
    consts = json_load(const_file)
    const_file.close()

with open("configs/auth.json", "r") as auth_file:
    auth = json_load(auth_file)

if consts["email"]:
    emailserver = smtplib.SMTP("smtp.live.com")
    emailserver.connect("smtp.live.com")
    emailserver.ehlo()
    emailserver.starttls()
    emailserver.login("executerdiscordbot@outlook.com", auth["email_password2"])
else:
    emailserver = None


sense = None
try:
    import sense_hat
except ModuleNotFoundError:
    pass
else:
    sense = sense_hat.SenseHat()

DIR = os.path.dirname(os.path.realpath(__file__))
