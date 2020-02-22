import discord
import yippi
import rule34
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
rule34 = rule34.Sync()

class Nsfw(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def e621(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        search = tags.split()
        results = yippi.search.post(search)
        await ctx.send(random.choice(results).file_url)
    
    @commands.command()
    @commands.cooldown(1, 1, BucketType.user)
    async def rule34(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        images = rule34.getImages(tags=tags)
        await ctx.send(random.choice(images))
        
      

        
def setup(client):
    client.add_cog(Nsfw(client))
