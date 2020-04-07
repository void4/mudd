from argparse import ArgumentParser
from configparser import ConfigParser
import asyncio
import os.path
import pickle

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
        idplayermap, world = pickle.loads(open(path, "rb").read())
    else:
        world = World()
        print("Creating new database")

def save_db(path):
    print("Saving database:", path)
    with open(path, "wb+") as dbfile:
        dbfile.write(pickle.dumps([idplayermap, world]))

load_or_create_db(namespace.dbpath)

@loop(seconds=1)
async def output_task():
    for uid, meta in connections.items():
        tn, channel = meta
        data = tn.read_very_eager()
        if data:
            await channel.send(escape(data))

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

        if message.author.id not in connections:
            await message.channel.send("Reconnecting...")

            # Save the Discord channel so we can use it for broadcasts
            connections[message.author.id] = message.channel

            # Create Player if they do not exist
            if message.author.id not in idplayermap:
                await message.channel.send("First login, creating player...")
                player = create_player(message.author.id, str(message.author))
                await message.channel.send("Player created, welcome!")

            await message.channel.send("Logged in!")
        else:
            player = get_player(message.author.id)

        await message.channel.send("pong")

bot = Bot()
output_task.start()

try:
    bot.run(config["DISCORDTOKEN"])
except TypeError as e:
    print(e)
print("Shutting down gracefully...")
save_db(namespace.dbpath)
print("Done.")
