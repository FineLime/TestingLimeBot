import discord
import yippi
import rule34
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random, requests
import json

class Nsfw(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def e621(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        search = tags.split()
        results = yippi.search.post(search)
        await ctx.send(random.choice(results).file_url)
    
    @commands.command()
    async def rule34(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        badwords = ['cub', 'shota', 'loli', 'little', 'young', 'age_difference']
        allowed = True
        for i in badwords:
            if i in tags.lower():
                allowed = False
        if allowed == True:
            r34 = rule34.Rule34(self.client.loop)
            images = await r34.getImageURLS(tags=tags)
            await ctx.send(random.choice(images))
        else:
            await ctx.send("Sorry, those tags are not allowed")
        
      

        
def setup(client):
    client.add_cog(Nsfw(client))
