import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Embed(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, title='Title', description='description', thumbnail='thumbnail', image='image'): 
        await ctx.send(f'Title: {title} | description: {description} | thumbnail: {thumbnail}| image: {image}')

        
def setup(client):
    client.add_cog(Embed(client))
