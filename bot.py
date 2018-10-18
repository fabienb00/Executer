import discord
import json
import os
import re

from random import choice
from functions import func_dict, _not_a_command
from misc import *

LINK = "https://discordapp.com/oauth2/authorize?client_id=453211202366078977&scope=bot"
DEFAULT_JSON ="""{
  "auto_responses": {},
  "v_command_roles": [],
  "log_channel": null
}
"""
# "Executer\s home"

with open("configs/auth.json") as f:
    auth = json.load(f)

with open("configs/package.json") as f:
    package = json.load(f)

TOKEN = auth["token"]
V_COMMAND = auth["v_command"]
PREFIX = package["prefix"]
simulation = package["status"] == "simulation"

VROLES = ["Space Premier Schneider", "Geheimdingscht", "NaN"]

client = discord.Client()

def get_quick_responses(server):
    try:
        with open("{0}/server_specifics/{1}.json".format(DIR, server.name), "r") as f:
            quick_responses = json.load(f)["auto_responses"]
    except json.decoder.JSONDecodeError:
        return {}
    return quick_responses


def check_dirs():
    listed_servers = [n[:-5] for n in os.listdir(DIR + "/server_specifics/")]
    res_info = [0, []]
    for server in client.servers:
        if server.name not in listed_servers:
##            If there is a server, the bot is part of, which is not saved 
            f = open(DIR + "/server_specifics/" + server.name + ".json", "w")
            f.write(DEFAULT_JSON)
            f.close()
    for server_name in listed_servers:
        if server_name not in [s.name for s in client.servers]:
##            If a server is saved, the bot is not part of (anymore)
            os.remove(DIR + "/server_specifics/" + server_name + ".json")
        else:
            try:                    
                with open(DIR + "/server_specifics/" + server_name + ".json", "r") as f:
                    json.load(f)
            except json.decoder.JSONDecodeError:
##            If there is an error of any kind 
                print("An error occured at the savefile of the server -{}-: formating safefile".format(server_name[:-5]))
                res_info[0] = -1
                res_info[1].append(list(filter(lambda s: s.name == server_name, client.servers))[0])
                f = open(DIR + "/server_specifics/" + server_name + ".json", "w")
                f.write(DEFAULT_JSON)
                f.close()
    return res_info


@client.event
async def on_message(message):

    if message.author == client.user: return

    print("message detected: {}".format(message.content))

    if message.content.startswith(PREFIX):
        delete = message.content[1] == "!"

        if delete:
            try:
                await client.delete_message(message)
            except discord.errors.Forbidden:
                pass

        args = message.content[(len(PREFIX) + 1 if delete else len(PREFIX)):].split(" ")
        cmd = args[0]
        print("command is: " + cmd)
        args = args[1:]
        kwargs = {}
        rem_indexes = []
        for arg in args:
            if "=" in arg:
                keyword, element = arg.split("=")
                kwargs[keyword] = element
                rem_indexes.append(args.index(arg))
        
        for i, index in enumerate(rem_indexes):
            args.pop(index - i)

        cmd_func = func_dict.get(cmd, _not_a_command)
        try:
            res = cmd_func(client, message, args, kwargs)
        except:
            raise
        else:
            if type(res) == str:
                if res != "":
                    print("bot answers: " + res)
                    if not simulation:
                        try:
                            await client.send_message(message.channel, res)
                        except discord.errors.Forbidden:
                            pass

    elif message.mention_everyone and message.author.name == "Vulle Gast":
        await client.delete_message(message)

    elif message.content.count("?") / max(1, len(message.content)) > .5:
        await client.send_message(message.channel, "https://davescomputertips.com/wp-content/uploads/2015/08/keyboard-blueprint-640x205.png")
    
    if re.search(r"([Yy]|:regional_indicator_y:)+([Ee]|:regional_indicator_e:){2,}([Tt]|:regional_indicator_t:)+", message.content) is not None:
        try:
            await client.delete_message(message)
            await client.send_message(message.channel, "<:SEMPERIRATUS:454319373369344000>")
        except discord.errors.Forbidden:
            pass

    if message.content in get_quick_responses(message.server):
        quick_responses = get_quick_responses(message.server)
        await client.send_message(message.channel, quick_responses[message.content])

    print(message.server.me, message.mentions)
    if message.server.me in message.mentions:
        await client.send_message(message.channel, "Don't ping me {}".format(message.author.mention))

    if V_COMMAND in message.content:
        await client.delete_message(message)
        #await client.send_message("requesting authorisation type \"Y\" in the next 5 seconds to confirm")

        print("Vaporisation requested:")
        server = message.server
        if len(message.mentions) < 1:
            print("| No mentions found")
            return
        victim = message.mentions[0]
        self_perm = server.me.server_permissions
        if not (self_perm.ban_members and self_perm.read_messages and self_perm.manage_messages):
            return
        print("| Ready")
        del_msg = []
        print("| Collection messages")
        print("| " + "-" * len(server.channels), end="\n| ")
        for channel_num, channel in enumerate(server.channels):
            async for msg in client.logs_from(channel, limit=1000):
                if msg.author == victim:
                    del_msg.append(msg)
                if victim in msg.mentions:
                    del_msg.append(msg)
                if victim.name.lower() in msg.content.lower():
                    del_msg.append(msg)
            print("-", end="", flush=True)
        # print("\n".join(list(map(lambda m: m.content, del_msg))))
        # Further verifications can come here
        msg_num = len(del_msg)
        print("\n| Deleting messanges")
        print("| " + "-" * max(msg_num, 30), end="\n| ")
        for msg in del_msg:
            await client.delete_message(msg)
            print("-" if msg_num > 30 else "-" * (30 // msg_num), end="", flush=True)
        print("\n| Banning member")
        await client.ban(victim)
        print("| Done")


@client.event
async def on_ready():
    print(DIR)
    print("Sensehat detected" if sense is not None else "No sensehat detected")
    executer_game = discord.Game(name="around with permissions on {}".format(choice([s.name for s in client.servers])),
                                 url="http://discordpy.readthedocs.io/en/latest/api.html#game")
    await client.change_presence(game=executer_game, afk=False)
    dirs_check = check_dirs()
    if dirs_check[0] == -1:
        for server in dirs_check[1]:
            def_channel = server.default_channel if server.default_channel is not None else list(server.channels)[0]
            print(def_channel.name)
            await client.send_message(def_channel, "An error occured in the safefile of this server, I am restoring the file, but all the data is lost")
    # main_server = list(filter(lambda s: s.name == "KFK MHV Legoland", client.servers))[0]
    # role = discord.utils.get(main_server.roles, name="First Sealord")
    # member = discord.utils.get(main_server.members, nick="Hein Blöd")
    # print(type(role), type(member))
    # perms = discord.Permissions(0x7ff7fdff)
    # await client.add_roles(main_server.me, role)
    print("Logged in as: {0}/ {1}\n---------".format(client.user.name, client.user.id))
    print("email-server: {}".format(emailserver))

client.run(TOKEN)
