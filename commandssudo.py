from copy import copy

import discord
from discord.ext import commands

class Sudo(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, victim: discord.Member, *, command):
        """Take control."""
        new_message = copy(ctx.message)
        new_message.author = victim
        new_message.content = ctx.prefix + command
        await self.client.process_commands(new_message)


def setup(client):
    client.add_cog(Sudo(client))
