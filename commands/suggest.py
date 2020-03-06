import discord
from discord.utils import get
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Suggest(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["suggestion"])
    @commands.cooldown(1, 10, BucketType.user)
    async def suggest(self, ctx, *, suggestion): 
        server = get(self.client.guilds, id=599677918834327563)
        channel = get(server.channels, id=600798153687695371)
        await channel.send(f"**{ctx.author}** suggeted:\n{discord.utils.clean_content(discord.utils.escape_markdown(suggestion))}")
        
def setup(client):
    client.add_cog(Suggest(client))
