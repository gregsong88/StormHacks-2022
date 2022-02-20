# Honestly you can ignore this whole file.

import discord
from discord.ext.commands import Bot
from discord.ext import commands

class MyHelpCommand(commands.MinimalHelpCommand): #Replaces help command with fancy embed shit

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = ', '.join(c.name for c in commands)
            self.paginator.add_line('__**%s**__' % heading)
            self.paginator.add_line(joined + '\n')

    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=0xdeadaf, description='')

        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

class Misc(commands.Cog, name="Misc"):

    def __init__(self, client):
        self.client = client
        self.client.help_command = MyHelpCommand()

    @commands.command()
    async def ping(self, ctx):
        latency = self.client.latency * 1000
        await ctx.send(f"My ping: `{round(latency, 2)}` ms.")

def setup(client):
    client.add_cog(Misc(client))
    client.help_command.cog = client.cogs["Misc"]