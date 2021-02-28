import discord
import os
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random, requests
import json
from xml.etree import ElementTree

class Nsfw(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def e621(self, ctx, *, tags): 
      if ctx.channel.is_nsfw(): 
        search = tags.replace(' ', '+')
        headers = {
            
            'User-Agent':'LimeBot (By FineLime)'   
            
        }
        r = requests.get(f'https://e621.net/posts.json?tags={search}&limit=50', headers=headers, auth=('FineLime', os.getenv('e621_key')))
        post = random.choice(r.json()['posts'])
        
        badwords = ['cub', 'shota', 'loli', 'little', 'young', 'age_difference']
        allowed = True
        for i in badwords:
            if i in post['tags']['general']:
                allowed = False
        if allowed == True:
            await ctx.send(post['file']['url'])
        else:
            await ctx.send("Sorry, those tags are not allowed")
    
    @commands.command()
    async def rule34(self, ctx, *, search): 
      if ctx.channel.is_nsfw(): 
        badwords = ['cub', 'shota', 'loli', 'little', 'young', 'age_difference']
        r = requests.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=50&tags={search}")
        r = ElementTree.fromstring(r.content)
        if int(r.attrib['count']) == 0: 
            await ctx.send("No posts with those tags found.")
            return
        
        post = r[random.randint(0, int(r.attrib['count'])-1)]
        allowed = True
        for i in badwords:
            if i in post.attrib['tags'].lower():
                allowed = False
                break
        if allowed:
            image = post.attrib['file_url']
            await ctx.send(image)
        else:
            await ctx.send("Sorry, those tags are not allowed")
        
      

        
def setup(client):
    client.add_cog(Nsfw(client))
