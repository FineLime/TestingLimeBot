import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Changestatus(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def watch(self, ctx, *, w): 
        await client.change_presence(activity=discord.Activity(name=w, type=discord.ActivityType.watching))
        await ctx.send(f"I am now watching {w}")
    
    @commands.command()
    @commands.is_owner()
    async def listen(self, ctx, *, l): 
        await client.change_presence(activity=discord.Activity(name=l, type=discord.ActivityType.listening))
        await ctx.send(f"I am now listening to {l}")

    @commands.command()
    @commands.is_owner()
    async def play(self, ctx, *, p): 
        await client.change_presence(activity=discord.Activity(name=p, type=discord.ActivityType.playing))
        await ctx.send(f"I am now playing {p}")

    @commands.command()
    @commands.is_owner()
    async def stream(self, ctx, *, s): 
        await client.change_presence(activity=discord.Activity(name=s, type=discord.ActivityType.streaming))
        await ctx.send(f"I am now streaming {s}")

        
def setup(client):
    client.add_cog(Changestatus(client))
