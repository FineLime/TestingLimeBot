import discord
from discord.ext import commands
import asyncpg

class Autorole(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx): 
        await ctx.send("**USAGE:** ;autorole [add/remove] [role]")
        
    @autorole.command()
    async def add(self, ctx, role:discord.Role):
        
        check = await self.client.pg_con.fetch("SELECT * FROM autorole WHERE server=$1 AND role=$2", str(ctx.guild.id), str(role.id))
        if len(check):
            await ctx.send("That role is already set up as an autorole")
            return
        await self.client.pg_con.execute("INSERT INTO autorole (server, role) VALUES ($1, $2)", str(ctx.guild.id), str(role.id))
        await ctx.send("New autorole added! :white_check_mark:")
        
    @autorole.command()
    async def remove(self, ctx, role:discord.Role):
        await self.client.pg_con.execute("DELETE FROM autorole WHERE server=$1 AND role=$2", str(ctx.guild.id), str(role.id))
        await ctx.send("Removed autorole! :white_check_mark:")
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        autoroles = await self.client.pg_con.fetch("SELECT * FROM autorole WHERE server=$1", str(member.guild.id))
        if len(autoroles):
            return
        for i in autoroles:
            try:
                await member.add_role(discord.utils.get(member.guild.roles, id=i[f"{int(role)}"]))
            except:
                pass
        
def setup(client):
    client.add_cog(Autorole(client))
