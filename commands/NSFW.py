import discord
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
        search = tags.replace(' ', '+')
        headers = {
            
            'User-Agent'='LimeBot (By FineLime)'   
            
        }
        r = requests.get(f'https://e621.net/posts.json?tags={search}&limit=50', headers=headers, auth=('FineLime', 'yjWn25kgWyi5sZepWVBezW2n'))
        posts = r.json()['posts']
        await ctx.send(random.choice(posts)['url'])
    
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
