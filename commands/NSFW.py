import discord
import yippi
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random, requests
import json

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
        await ctx.channel.trigger_typing()
        try:
            data = requests.get(
                "http://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={}&tags={}".format(tags),
                headers={"User-Agent": "linux:memebot:v1.0.0"})
        except json.JSONDecodeError:
            await ctx.send(("nsfw.no_results_found", ctx).format(tags))
            return

        count = len(data)
        if count == 0:
            await ctx.send(("nsfw.no_results_found", ctx).format(tags))
            return
        image_count = 4
        if count < 4:
            image_count = count
        images = []
        for i in range(image_count):
            image = data[random.randint(0, count)]
            images.append("http://img.rule34.xxx/images/{}/{}".format(image["directory"], image["image"]))
        await ctx.send(("nsfw.results", ctx).format(image_count, count, tags, "\n".join(images)))
        
      

        
def setup(client):
    client.add_cog(Nsfw(client))
