import datetime
import smtplib
from misc import emailserver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


HTML = """\
<html>
    <body style="background:#20206e; color:white">
        <h1>The server has been shut down<br/></hr></h1>
        <p style="background:"#a0a0ff; margin:35px>
            The discord bot function <strong>"bot.py"</strong> has stopped working </br>
            This could be because of an error or something other. </br>
            Time of the shutdown was {wkday} {t.day}/{t.month} ({t.year}) at {t.hour}:{t.minute} {t.second}s.
            If there is severe bug concearning the bot, please contact us at <a href=https://discord.gg/8Uv4XV4>our discord server</a>.
        </p>
    </body>
</html>
"""


WEEKDAYS = ["Monday",
            "Day after monday",
            "Wednessday",
            "Thursday",
            "Fryday",
            "Saturday",
            "Sunday"]
running = True

while running:
    try:
        import bot
    except Exception as e:
        print("-----------------")
        print("An error occured at {}:".format(datetime.datetime.now().isoformat()))
        print(e)

    time = datetime.datetime.now()
    print("-----------------")
    print("Shutdown")
    print("Shutdown occured {wkday} {t.day}/{t.month} ({t.year}) at {t.hour}:{t.minute} {t.second}s".format(t = time, wkday = WEEKDAYS[time.weekday()]))

    if emailserver is not None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Server shutdown"
        msg["From"] = "executerdiscordbot@outlook.com"
        msg["To"] = "felni474@school.lu"
        html_part = MIMEText(HTML.format(t = time, wkday = WEEKDAYS[time.weekday()]), "html")
        txt_part = MIMEText("The server shutted down at {dt}\nsee server for more informations".format(dt=datetime.datetime.now().isoformat()), "text")
        msg.attach(html_part)
        msg.attach(txt_part)
        try:
            emailserver.send_message(msg)
        except Exception:
            pass
    
    user_inp = input("Restart?[Y|N]")
    if user_inp.lower() != "y":
        running = False
