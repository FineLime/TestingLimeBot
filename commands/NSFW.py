import discord
import yippi
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random

class Nsfw(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def e621(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        print(tags.split())
        await ctx.send(random.choice(results).file_url)
        
      

        
def setup(client):
    client.add_cog(Nsfw(client))
