import discord
from discord.ext import commands

class Purge(commands.Cog): 

    def __init__(self, client):
        self.client = client
    
    def isText(m, text): 
        return m.message == text
        #lol
        
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=1): 
        await ctx.channel.purge(limit=amount)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purgebanana(self, ctx, amount=1): 
        await ctx.channel.purge(limit=amount, check=isText("banana"))
        
def setup(client):
    client.add_cog(Purge(client))
