import discord
import re

from math import *
from random import choice
from misc import DIR, consts, Queue, emailserver, sense, ReturnMessage
from json import load, dump
from CAH_Core import Player, Game

from email import mime

SWEARLIST = consts["Abuses"]
SPAM_MAX = consts["Spam_max"]


CAH_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Cards_Against_Humanity_logo.png/1200px-Cards_" \
                "Against_Humanity_logo.png"

current_cah_game = None
message_queue = Queue()

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
    return ReturnMessage(":thinking:")


def bot_math(act_client, rawmessage, args, kwargs):
    nums = [float(x) for x in args[1:]]
    operator = args[0]

    # Multy-Argument functions
    if len(nums) > 2:
        if operator == "+":
            return ReturnMessage(" + ".join(args[1:]) + " = " + str(sum(nums)))
        if operator == "*":
            prod = 1
            for num in nums:
                prod *= num
            return ReturnMessage(" * ".join(args[1:]) + " = " + str(prod))

    # Two-Argument functions
    elif len(nums) == 2:
        a, b = nums[0], nums[1]
        if operator == "+":
            return ReturnMessage("{0} + {1} = {2:8.5f}".format(a, b, a + b))
        if operator == "*":
            return ReturnMessage("{0} * {1} = {2:8.5f}".format(a, b, a * b))
        if operator == "-":
            return ReturnMessage("{0} - {1} = {2:>8.5f}".format(a, b, a - b))
        if operator == "/":
            return ReturnMessage("{0} / {1} = {2:>8.5f}".format(a, b, a / b))
        if operator == "power":
            return ReturnMessage("{0}^{1} = {2:>8.5f}".format(a, b, pow(a, b)))
        if operator == "root":
            return ReturnMessage("{0}root{1} = {2:>8.5f}".format(a, b, pow(a, 1 / b)))
        if operator == "log":
            return ReturnMessage("log*{0}* {1} = {2:>8.5f}".format(a, b, log(b, a)))
    # One argument functions
    elif len(nums) == 1:
        a = nums[0]
        if operator == "sqrt":
            return ReturnMessage("sqrt({0}) = {1:>8.5f}".format(a, sqrt(a)))
        if operator == "inv":
            return ReturnMessage("{0}^-1 = {1:>8.5f}".format(a, 1 / a))
        # trigonometry
        if operator == "sin":
            return ReturnMessage("sin({0}rad) = {1:>8.5f}".format(a, sin(a)))
        if operator == "cos":
            return ReturnMessage("cos({0}rad) = {1:>8.5f}".format(a, cos(a)))
        if operator == "tan":
            return ReturnMessage("tan({0}rad) = {1:>8.5f}".format(a, tan(a)))
        if operator == "asin":
            return ReturnMessage("arcsin({0}) = {1:>8.5f}rad".format(a, asin(a)))
        if operator == "acos":
            return ReturnMessage("arccos({0}) = {1}rad".format(a, acos(a)))
        if operator == "atan":
            return ReturnMessage("arctan({0}) = {1}rad".format(a, atan(a)))
        # deg
        if operator == "sinD":
            return ReturnMessage("sin({0}°) = {1:>8.5f}".format(a, sin(radians(a))))
        if operator == "cosD":
            return ReturnMessage("cos({0}°) = {1:>8.5f}".format(a, cos(radians(a))))
        if operator == "tanD":
            return ReturnMessage("tan({0}°) = {1:>8.5f}".format(a, tan(radians(a))))
        if operator == "asinD":
            return ReturnMessage("arcsin({0}) = {1:>8.5f}".format(a, degrees(asin(a))))
        if operator == "acosD":
            return ReturnMessage("arccos({0}) = {1}°".format(a, degrees(acos(a))))
        if operator == "atanD":
            return ReturnMessage("arctan({0}) = {1}°".format(a, degrees(atan(a))))

    # Zero-Argument functions
    else:
        if operator == "e":
            return ReturnMessage("e = 2.71828182846")
        if operator == "pi":
            return ReturnMessage("pi = 3.1415926535")

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
    return ReturnMessage(victim + " " + " ".join(args[1:]))


def spam(act_client, raw_message, args, kwargs):
    txt = "spam"
    times = 3
    if len(args) == 1:
        if isinstance(args[0], int):
            times = int(args[0])
    if len(args) > 1:
        if isinstance(args[0], int):
            times = int(args[0])
            txt = " ".join(args[1:])
        else:
            txt = " ".join(args)
    return ReturnMessage("\n".join([txt] * min(times, SPAM_MAX)) + ("\nOk, I'm bored now" if times > SPAM_MAX else ""))


def msg(act_client, raw_message, args, kwargs):
    #author_text = "Message from: {} \n".format(raw_message.author.name)
    message_text = "Content: {} \n".format(" ".join(args))
    length = max(len(message_text), 18) - 1

    em = discord.Embed(title="+++Incomming Transmission+++\n" + "+" * length + "\n", colour=raw_message.author.color)
    em.description = message_text
    url = raw_message.author.avatar_url
    if url == "":
        url = raw_message.author.default_avatar_url
    em.set_author(name="-Signed, " + raw_message.author.nick, icon_url=url)
    em.set_footer(text="+++Transmission ends+++")
    return ReturnMessage(em)


def approves(act_client, raw_message, args, kwargs):
    em = discord.Embed(title="{} approves :ok_hand:".format(act_client.user.name), colour=0xffff00)
    return ReturnMessage(em)


def _print(act_client, raw_message, args, kwargs):
    if raw_message.author.name == "The Bechet" or raw_message.author.name == "USB Umberto":
        return ReturnMessage("You are not allowed to print!")
    return ReturnMessage(" ".join(args))


def add_quick_response(act_client, raw_message, args, kwargs):
    filename = "{0}/server_specifics/{1}.json".format(DIR, raw_message.server)
    if "->" not in args:
        return ReturnMessage("Invalid Syntax")
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
    return ReturnMessage("\n".join([perm[0] if perm[1] else "" for perm in raw_message.channel.permissions_for(raw_message.author)]))


def cards_against_humanity(act_client, raw_message, args, kwargs):
    global current_cah_game
    author_ment = raw_message.author.mention
    if re.match(r"^%?cah (play \d{1,3}|choose \d|host (rando)?|join|close host|finish|stats|random)\s*$", raw_message.content) is None:
        pass
    if args[0] not in ("host", "random") and current_cah_game is None:
        return ReturnMessage("No game initialized")
    if len(args) >= 2:
        command = args[0]
        if command == "play":
            if any([re.match(r"^\d$", x) is None for x in args[1:]]):
                return ReturnMessage("All arguments must be positive integers between 0 and 9")

            if current_cah_game.game_stat != 1:
                return ReturnMessage("You cannot play now")

            if len(args) - 1 != current_cah_game.cards_needed:
                return ReturnMessage("You have to play exactly {} cards".format(current_cah_game.cards_needed))

            if current_cah_game.tsar.discord_implement == raw_message.author:
                return ReturnMessage("The tsar cannot play")

            message_queue.add_msg(ReturnMessage(current_cah_game.lay_card(raw_message.author.nick, [int(x) for x in args[1:]])))
            if current_cah_game.all_played:
                em = discord.Embed(title="The Cards are laid out", colour=0x000000)
                em.description = current_cah_game.show()
                em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
                message_queue.add_msg(ReturnMessage(em))

            cards_em = discord.Embed(title="White Cards", colour=0x000000)
            cards_em.description = current_cah_game.get_player(raw_message.author.nick).get_cards()
            cards_em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            return ReturnMessage(cards_em, raw_message.author)
        if command == "choose":
            if current_cah_game.tsar.discord_implement != raw_message.author:
                return ReturnMessage("Only the tsar can choose")

            if current_cah_game.game_stat != 2:
                return ReturnMessage("You cannot choose now")

            try:
                player_chosen = int(args[1])
            except ValueError:
                return ReturnMessage(author_ment + "player must be an integer")
            if player_chosen >= current_cah_game.player_num - 1:
                return ReturnMessage(author_ment + "player must be a number between 0 and {}"
                                     .format(current_cah_game.player_num - 2))
            return ReturnMessage(current_cah_game.choose(player_chosen))
            # Choose a player
        if command == "host":
            # Create a new game
            current_cah_game = Game("cah_lib.json", rando=("rando" in args))
            current_cah_game.join(raw_message.author)

            em = discord.Embed(title="New c-a-h game",  colour=0x000000)
            em.description = "{} just created a new \"Cards against Humanity\" game".format(raw_message.author.nick)
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            return ReturnMessage(em)
    elif len(args) == 1:
        command = args[0]
        if command == "host":
            # Create a new game
            current_cah_game = Game("cah_lib.json")
            current_cah_game.join(raw_message.author)

            em = discord.Embed(title="New c-a-h game",  colour=0x000000)
            em.description = "{} just created a new \"Cards against Humanity\" game".format(raw_message.author.nick)
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            return ReturnMessage(em)
        if command == "join":
            if current_cah_game.game_stat != 0:
                return ReturnMessage("You cannot join now")

            current_cah_game.join(raw_message.author)

            em = discord.Embed(title="User Joined", colour=0x20ff1d)
            em.description = author_ment + " just joined ..."
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            # Join a game
            return ReturnMessage(em)
        if command == "leave":
            current_cah_game.leave(raw_message.author)

            em = discord.Embed(title="User Left", colour=0xa305d5)
            em.description = author_ment + " just left ..."
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            return ReturnMessage(em)
        if command == "close_host":
            if current_cah_game.game_stat != 0:
                return ReturnMessage("Host already closed")

            if current_cah_game.tsar.discord_implement != raw_message.author:
                return ReturnMessage("You cannot close the host")

            message_queue.add_msg(ReturnMessage(current_cah_game.close_joining()))

            em = discord.Embed(title="Game Start", colour=0x000000)
            em.description = "Nobody can join now anymore"
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            # Close the joining
            for player in current_cah_game.player_list:
                cards_em = discord.Embed(title="White Cards", colour=0x000000)
                cards_em.description = player.get_cards()
                cards_em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
                message_queue.add_msg(ReturnMessage(cards_em, player.discord_implement))

            return ReturnMessage(em)
        if command == "finish":
            em = discord.Embed(title="Game statistics", colour=0xff1c1d)
            em.description = current_cah_game.stats()
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            message_queue.add_msg(ReturnMessage(em))

            current_cah_game = None
            em = discord.Embed(title="Game Finished", colour=0xff1c1d)
            em.description = "The game has just been finished"
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            # Finish the game
            return ReturnMessage(em)
        if command == "stats":
            em = discord.Embed(title="Game statistics",  colour=0x000000)
            em.description = current_cah_game.stats()
            em.set_author(name="CaH", icon_url=CAH_IMAGE_URL)
            return ReturnMessage(em)
        if command == "random":
            if current_cah_game is None:
                current_cah_game = Game("cah_lib.json")
            if raw_message.author.id == 6988 or raw_message.author.id == 7507:
                return ReturnMessage("Fuck you {mention}:\n{card}".format(mention=author_ment, card=current_cah_game.random()))
            return ReturnMessage(current_cah_game.random())


def wiki(act_client, raw_message, args, kwargs):
    return ReturnMessage("https://de.wikipedia.org/wiki/" + " ".join(args))


def infinite_loop(act_client, raw_message, args, kwargs):
    return ReturnMessage("%!inf_blink")


def shutup(act_client, raw_message, args, kwargs):
    return ReturnMessage("---")


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
    txt += "Temperature:\n {cel:7.3f} {d}C;\n {far:7.3f} {d}F;\n {kel:7.3f} K\n\n".format(d=chr(176), cel=temp_cel,
                                                                                          far=temp_fahr, kel=temp_kel)
    txt += "Humidity:\n {perc:7.3}%\n\n".format(perc=humidity)
    txt += "Pressure:\n {pa:9.3f} Pa;\n {bar:9.3f} bar;\n {atm:9.3f} atm\n\n".format(pa=press_pa, bar=press_bar,
                                                                                     atm=press_atm)
    return ReturnMessage(txt)


def server_client_stats(act_client, raw_message, args, kwargs):
    txt = "Email: " + "None\n" if act_client.email is None else act_client.email
    if sense is not None:
        txt += "Server Temperature: {cel:7.3f}{d}C".format(cel=sense.temp, d=chr(176))
    return ReturnMessage(txt)


def email(act_client, raw_message, args, kwargs):
    mail = mime.multipart.MIMEMultipart("")
    style = kwargs.get("style", "§§style§§")
    content = " ".join(args)
    subject = kwargs.get("subject", "")
    to = kwargs.get("to")
    if to is None:
        return ReturnMessage("you have to specify an adress with \"to=ADRESSGOESHERE\"")

    with open("email_template.html", "r") as f:
        template = f.read()
    html = mime.text.MIMEText(template.replace("§§content§§", content).replace("§§style§§", style), "html")
    mail.attach(html)
    mail["From"] = "executerdiscordbot@outlook.com"
    mail["To"] = to
    mail["Subject"] = subject

    if emailserver is not None:
        emailserver.send_message(mail)
        return ReturnMessage("e-mail was sent sucessfully [or however sucessfully is written]")
    else:
        print(mail.as_string())
        return ReturnMessage("not logged in e-mail is deactivated")


def test_message(act_client, raw_message, args, kwargs):
    return ReturnMessage("args = {}:\n\nkwargs = {}".format("\n".join(args),
                                              "\n".join([key + " : " + value for key, value in kwargs.items()])))


def _not_a_command(act_client, raw_message, args, kwargs):
    return ReturnMessage("\"{mes}\" is not a valid command".format(mes=raw_message.content))


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
             "cah": cards_against_humanity,
             "wiki": wiki,
             # "inf_blink": infinite_loop,
             "shutup": shutup,
             "weather": weather,
             "serv_cli": server_client_stats,
             "e-mail": email,
             "email": email,
             "test": test_message}

if __name__ == "__main__":
    print("everything is fine")
