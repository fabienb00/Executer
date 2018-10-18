from math import *
from random import choice
from misc import *
from json import load, dump

from email import mime

SWEARLIST = consts["Abuses"]
SPAM_MAX = consts["Spam_max"]

# New Github comment test

#              FUNCTIONS
# -------------------------------------


def dev_help(act_client, raw_message, args, kwargs):
    def_methods_checker = lambda x: not x.startswith("__") and not x.endswith("__")
    strg = "CLIENT STRUCTURE\n" + "-" * 16 + "\n"
    strg += "\n".join(filter(def_methods_checker, dir(act_client)))
    strg += "\nMESSAGE STRUCTURE\n" + "-" * 17 + "\n"
    strg += "\n".join(filter(def_methods_checker, dir(raw_message)))
    strg += "\nCHANNEL STRUCTURE\n" + "-" * 17 + "\n"
    strg += "\n".join(filter(def_methods_checker, dir(raw_message.channel)))
    strg += "\nSERVER STRUCTURE\n" + "-" * 16 + "\n"
    strg += "\n".join(filter(def_methods_checker, dir(raw_message.server)))
    print(strg)
    # return strg
    
def help(act_client, raw_message, args, kwargs):
    return ":thinking:"


def bot_math(act_client, rawmessage, args, kwargs):
    nums = [float(x) for x in args[1:]]
    operator = args[0]

    # Multy-Argument functions
    if len(nums) > 2:
        if operator == "+":
            return " + ".join(args[1:]) + " = " + str(sum(nums))
        if operator == "*":
            prod = 1
            for num in nums:
                prod *= num
            return " * ".join(args[1:]) + " = " + str(prod)

    # Two-Argument functions
    elif len(nums) == 2:
        a, b = nums[0], nums[1]
        if operator == "+":
            return "{0} + {1} = {2:8.5f}".format(a, b, a + b)
        if operator == "*":
            return "{0} * {1} = {2:8.5f}".format(a, b, a * b)
        if operator == "-":
            return "{0} - {1} = {2:>8.5f}".format(a, b, a - b)
        if operator == "/":
            return "{0} / {1} = {2:>8.5f}".format(a, b, a / b)
        if operator == "power":
            return "{0}^{1} = {2:>8.5f}".format(a, b, pow(a, b))
        if operator == "root":
            return "{0}root{1} = {2:>8.5f}".format(a, b, pow(a, 1/b))
        if operator == "log":
            return "log{0}{1} = {2:>8.5f}".format(a, b, log(a, b))
# One argument functions
    elif len(nums) == 1:
        a = nums[0]
        if operator == "sqrt":
            return "sqrt({0}) = {1:>8.5f}".format(a, sqrt(a))
        if operator == "inv":
            return "{0}^-1 = {1:>8.5f}".format(a, 1 / a)
        # trigonometry
        if operator == "sin":
            return "sin({0}rad) = {1:>8.5f}".format(a, sin(a))
        if operator == "cos":
            return "cos({0}rad) = {1:>8.5f}".format(a, cos(a))
        if operator == "tan":
            return "tan({0}rad) = {1:>8.5f}".format(a, tan(a))
        if operator == "asin":
            return "arcsin({0}) = {1:>8.5f}rad".format(a, asin(a))
        if operator == "acos":
            return "arccos({0}) = {1}rad".format(a, acos(a))
        if operator == "atan":
            return "arctan({0}) = {1}rad".format(a, atan(a))
        # deg
        if operator == "sinD":
            return "sin({0}°) = {1:>8.5f}".format(a, sin(radians(a)))
        if operator == "cosD":
            return "cos({0}°) = {1:>8.5f}".format(a, cos(radians(a)))
        if operator == "tanD":
            return "tan({0}°) = {1:>8.5f}".format(a, tan(radians(a)))
        if operator == "asinD":
            return "arcsin({0}) = {1:>8.5f}".format(a, degrees(asin(a)))
        if operator == "acosD":
            return "arccos({0}) = {1}°".format(a, degrees(acos(a)))
        if operator == "atanD":
            return "arctan({0}) = {1}°".format(a, degrees(atan(a)))

    # Zero-Argument functions
    else:
        if operator == "e":
            return "e = 2.71828182846"
        if operator == "pi":
            return "pi = 3.1415926535"

    return "Command {0}  does not exist in the 'math' library".format(" ".join(args))


def swear(act_client, raw_message, args, kwargs):
    victim = ""
    for member in raw_message.server.members:
        if member.name in args or member.nick in args:
            victim += member.mention
            try:
                args.remove(member.name)
            except ValueError:
                args.remove(member.nick)
    if "everyone" in args:
        victim += "@everyone"
        args.remove("everyone")
    if victim == "":
        victim = raw_message.author.mention
    if len(args) > 1:
        return victim + choice(SWEARLIST)
    return victim + " " + " ".join(args[1:])


def spam(act_client, raw_message, args, kwargs):
    txt = "spam"
    times = 3
    if len(args) == 1:
        if isint(args[0]):
            times = int(args[0])
    if len(args) > 1:
        if isint(args[0]):
            times = int(args[0])
            txt = " ".join(args[1:])
        else:
            txt = " ".join(args)
    return "\n".join([txt] * min(times, SPAM_MAX)) + ("\nOk, I'm bored now" if times > SPAM_MAX else "")


def msg(act_client, raw_message, args, kwargs):
    author_text = "Message from: {} \n".format(raw_message.author.name)
    message_text = "Content: {} \n".format(" ".join(args))
    length = max(len(author_text), len(message_text), 18) - 1
    txt = "+++Incomming Transmission+++\n"
    txt += "+" * length + "\n"
    txt += author_text + message_text
    txt += "-Signed, " + raw_message.author.name + "\n"
    txt += "+" * length + "\n"
    txt += "+++Transmission ends+++"
    return txt


def approves(act_client, raw_message, args, kwargs):
    return "{} approves :ok_hand:".format(act_client.user.name)


def _print(act_client, raw_message, args, kwargs):
    return " ".join(args)


def add_quick_response(act_client, raw_message, args, kwargs):
    filename = "{0}/server_specifics/{1}.json".format(DIR, raw_message.server)
    if "->" not in args:
        return "Invalid Syntax"
    trigger = " ".join(args[:args.index("->")])
    response = " ".join(args[args.index("->") + 1:])
    with open(filename, "r") as f:
        current_file = load(f)
    # Open seperatly under write mode to delete everything first
    f = open(filename, "w")
    current_file["auto_responses"][trigger] = response
    dump(current_file, f, indent=2)
    f.close()


def remove_quick_response(act_client, raw_message, args, kwargs):
    filename = "{0}/server_specifics/{1}.json".format(DIR, raw_message.server)
    trigger = " ".join(args)
    with open(filename, "r") as f:
        current_file = load(f)
    # Open seperatly under write mode to delete everything first
    f = open(filename, "w")
    del current_file["auto_responses"][trigger]
    dump(current_file, f, indent=2)
    f.close()


def my_permissions(act_client, raw_message, args, kwargs):
    return "\n".join([perm[0] if perm[1] else "" for perm in raw_message.channel.permissions_for(raw_message.author)])


def wiki(act_client, raw_message, args, kwargs):
    return "https://de.wikipedia.org/wiki/" + " ".join(args)


def infinite_loop(act_client, raw_message, args, kwargs):
    return "%!inf_blink"


def shutup(act_client, raw_message, args, kwargs):
    return "---"


def weather(act_client, raw_message, args, kwargs):
    if sense is None:
        return "No sensehat detected on the server"
    
    temp_cel = sense.temp
    temp_fahr = temp_cel * 1.8 + 32
    temp_kel = temp_cel + 273.15
    
    humidity = sense.humidity
    press_hpa = sense.pressure
    press_pa = press_hpa * 100
    press_atm = press_hpa / 1013
    press_bar = press_hpa / 1000
    press_hg = press_pa / 40635.936
    
    lower_args = list(map(lambda arg: arg.lower(), args))
    
    txt = "Weather Report\n--------------\n\n"
    if "si" in lower_args:
        txt += "Temperature:\n {kel:7.3f} K\n\n".format(kel=temp_kel)
        txt += "Pressure:\n {pa:9.3f} Pa".format(pa=press_pa)        
        return txt
    if "murrica" in lower_args or "imp" in lower_args:
        txt += "Temperature:\n {far:7.3f} {d}F\n\n".format(d=chr(176), far=temp_fahr)
        txt += "Humidity:\n {perc:7.3}%\n\n".format(perc=humidity)
        txt += "Pressure:\n {hg:9.3f} ftHg\n\n".format(hg=press_hg)
        return txt
    txt += "Temperature:\n {cel:7.3f} {d}C;\n {far:7.3f} {d}F;\n {kel:7.3f} K\n\n".format(d=chr(176), cel=temp_cel, far=temp_fahr, kel=temp_kel)
    txt += "Humidity:\n {perc:7.3}%\n\n".format(perc=humidity)
    txt += "Pressure:\n {pa:9.3f} Pa;\n {bar:9.3f} bar;\n {atm:9.3f} atm\n\n".format(pa=press_pa, bar=press_bar, atm=press_atm)
    return txt

def server_client_stats(act_client, raw_message, args, kwargs):
    txt = "Email: " + "None\n" if act_client.email is None else act_client.email
    if sense is not None:
        txt += "Server Temperature: {cel:7.3f}{d}C".format(cel = sense.temp, d=chr(176))
    return txt

def email(act_client, raw_message, args, kwargs):
    mail = mime.multipart.MIMEMultipart("")
    style = kwargs.get("style", "§§style§§")
    content = " ".join(args)
    subject = kwargs.get("subject", "")
    to = kwargs.get("to")
    if to is None:
        return "you have to specify an adress with \"to=ADRESSGOESHERE\""
    
    with open("email_template.html", "r") as f:
        template = f.read()
    html = mime.text.MIMEText(template.replace("§§content§§", content).replace("§§style§§", style), "html")
    mail.attach(html)
    mail["From"] = "executerdiscordbot@outlook.com"
    mail["To"] = to
    mail["Subject"] = subject
    
    if emailserver is not None:
        emailserver.send_message(mail)
        return "e-mail was sent sucessfully [or however sucessfully is written]"
    else:
        print(mail.as_string())
        return "not logged in e-mail is deactivated"

def test_message(act_client, raw_message, args, kwargs):
    return "args = {}:\n\nkwargs = {}".format("\n".join(args), "\n".join([key + " : " + value for key, value in kwargs.items()]))


def _not_a_command(act_client, raw_message, args, kwargs):
    return "\"{mes}\" is not a valid command".format(mes=raw_message.content)


func_dict = {"dev_help": dev_help,
             "help": help,
             "math": bot_math,
             "swear": swear,
             "spam": spam,
             "message": msg,
             "approves": approves,
             "print": _print,
             "add_quick": add_quick_response,
             "rem_quick": remove_quick_response,
             "mypermissions": my_permissions,
             "wiki": wiki,
##             "inf_blink": infinite_loop,
             "shutup": shutup,
             "weather": weather,
             "serv_cli": server_client_stats,
             "e-mail": email,
             "email": email,
             "test": test_message}

if __name__ == "__main__":
    print("everything is fine")
