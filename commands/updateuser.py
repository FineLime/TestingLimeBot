import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import asyncpg

class updateuser(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def updateme(self, ctx): 
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE id = $1", str(ctx.author.id))
        if not user: 
            await self.client.pg_con.execute("INSERT INTO users (id, name, coins, inventory, slotwins) VALUES ($1, $2, 0, '', 0)", str(ctx.author.id), str(ctx.author.name))
            await ctx.send("You have been updated!")
        await self.client.pg_con.execute("UPDATE users SET name = $1", str(ctx.author.name))

        
def setup(client):
    client.add_cog(updateuser(client))
