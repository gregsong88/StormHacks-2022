import discord
import os
import config
from discord.ext.commands import Bot

'''Variable Declaration'''
PREFIX = config.PREFIX
TOKEN = config.TOKEN
#These are called "intents"
#Discord recently added them for bots in order for them to be able to see certain aspects of a server for security purposes.
intents = discord.Intents.default() 
intents.members = True
intents.presences = True
#############################################
client = Bot(command_prefix=PREFIX, intents=intents)

'''Code'''
client.remove_command("help") #Removes help command, we'll be re-adding this in a "cog" later.

for filename in os.listdir("./cogs/"): #Scans through the "cogs" folder in this directory for any files ending in .py and loads them.
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN) #Starts the bot