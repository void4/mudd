from argparse import ArgumentParser
from configparser import ConfigParser
import asyncio
import os.path
import pickle
import zlib

import discord
from discord.abc import PrivateChannel
from discord.ext.tasks import loop

from objects import *

config = ConfigParser()
config.read("config.ini")[0]
config = config["DEFAULT"]

world = None
idplayermap = {}

connections = {}

parser = ArgumentParser(description="Multi User Discord Dungeon")
parser.add_argument("--dbpath", type=str, default="database.pickle", help="Path to database file")
namespace = parser.parse_args()

def load_or_create_db(path):
    global world, idplayermap
    if os.path.exists(path):
        print("Loading database:", path)
        idplayermap, world = pickle.loads(zlib.decompress(open(path, "rb").read()))
        recreate_objmap(world)
    else:
        world = Room(name="The Ether", description="This is all there is right now", location=world)
        print("Creating new database")

def save_db(path):
    print("Saving database:", path)
    with open(path, "wb+") as dbfile:
        # TODO zlib compress
        dbfile.write(zlib.compress(pickle.dumps([idplayermap, world])))

load_or_create_db(namespace.dbpath)

@loop(seconds=1)
async def output_task():
    for uid, channel in connections.items():
        pass

    print(".", end="")

def create_player(id, name):
    global world
    player = new_player(name, world)
    idplayermap[id] = player.id
    return player

def get_player(id):
    return OBJMAP[idplayermap[id]]

class Bot(discord.Client):
    async def on_ready(self):
        print('Logged in as', self.user)

    async def on_message(self, message):

        # Only respond to private DMs
        if not isinstance(message.channel, PrivateChannel):
            return

        # Don't respond to ourselves
        if message.author == self.user:
            return

        async def send(msg):
            await message.channel.send(msg)

        player = None

        if message.author.id not in connections:
            #await send("Reconnecting...")

            # Save the Discord channel so we can use it for broadcasts
            connections[message.author.id] = message.channel

            # Create Player if they do not exist
            if message.author.id not in idplayermap:
                await send("First login, creating player...")
                player = create_player(message.author.id, str(message.author))
                await send("Player created, welcome!")
            else:
                player = get_player(message.author.id)

            #await send("Logged in!")
        else:
            player = get_player(message.author.id)

        cmd = message.content
        cmd = cmd.strip()

        response = None

        c = cmd.split()[0]
        cmd = cmd.split()

        if c in "look l".split():
            response = player.look()

        elif c in "dig d".split():
            target = get_obj(cmd[2], player, world, True)
            if target is None:
                target = cmd[2]
                print("not found, new room")
            player.dig(world, player.location, cmd[1], target)
            response = "Dug a room!"

        elif c in "where w".split():
            response = where(world)

        elif c in "go g".split():
            obj = get_obj(cmd[1], player)

            if isinstance(obj, Door):
                if obj.use(player):
                    response = f"Moved to {obj.target.name}"

        elif c in "stats s".split():
            response = f"I have {player.mana} mana\n"

        elif c in "inventory i".split():
            response = player.inventory()

        elif c in "create c".split():
            player.create(world, cmd[1])

        if response:
            await send(response)

bot = Bot()
output_task.start()

try:
    bot.run(config["DISCORDTOKEN"])
except TypeError as e:
    print(e)
print("Shutting down gracefully...")
save_db(namespace.dbpath)
print("Done.")
