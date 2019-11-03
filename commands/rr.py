import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import random
import asyncpg
import asyncio
import math

class RR(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["roulette", "russianroulette"])
    @commands.cooldown(1, 10, BucketType.user)
    async def rr(self, ctx): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", "None")
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id)) 
        if server['mutedrole'] != "None": 
            role = get(ctx.guild.roles, id=int(server['mutedrole'])) 
        else:
            role = "None"
      
        if random.randint(1, 5) == 3: 
            if role != "None":
                await ctx.send(f":gun: BANG! It was the bullet, I'll revive you but it may take some time!")
                await ctx.author.add_roles(role)
                await asyncio.sleep(300)
                await ctx.author.remove_roles(role)
                await ctx.send(f"{ctx.author.mention} has been revived!")
            else:    
                await ctx.send(f":gun: BANG! It was the bullet but don't worry, I revived you!")
                
        else:
            await ctx.send(f":gun: BANG! The gods want you to live another day, it was a blank!")
    
    @commands.command(asliases=["kms", "killme"])
    @commands.cooldown(1, 10, BucketType.user)
    async def suicide(self, ctx): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", "None")
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id)) 
        if server['mutedrole'] != "None": 
            role = get(ctx.guild.roles, id=int(server['mutedrole'])) 
        else:
            role = "None"

        if random.randint(1, 5) > 0: 
            if role != "None":
                await ctx.send(f":gun: BANG! I put {ctx.author.mention} out of their misery, i'll revive them soon.")
                await ctx.author.add_roles(role)
                await asyncio.sleep(300)
                await ctx.author.remove_roles(role)
                await ctx.send(f"{ctx.author.mention} has been revived!")
            else:    
                await ctx.send(f":gun: BANG! I put you out of your misery but I have to revive you.")
            
       
        
def setup(client):
    client.add_cog(RR(client))
