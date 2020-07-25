import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import asyncpg

class ServerSetup(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def muterole(self, ctx, muterole:discord.Role): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", "None")
        
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        await self.client.pg_con.execute("UPDATE servers SET mutedrole = $1 WHERE serverid=$2", str(muterole.id), str(ctx.guild.id))
        if server['logschannel'] != "None":
            embed = discord.Embed(title="Logs | MutedRole", description="The server's mute role has been changed.")
            embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="MutedRole", value=mutedrole.mention, inline=True)
            await get(ctx.guild.channels, id=int(server['logschannel'])).send(embed=embed)

        await ctx.send("The mute role has been changed! :white_check_mark:")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logs(self, ctx): 
        await ctx.send("**USAGE:** ;logs [channel/remove] {set} {channel}")
    
    @logs.command()
    async def remove(self, ctx):
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", "None")
            await ctx.send("You do not have a logs channel.")
            return
        server = server[0]
        if server['logschannel'] == 'None':
            await ctx.send("You do not have a logs channel.")
            return
        await self.client.pg_con.execute("UPDATE servers SET logschannel='None' WHERE serverid=$1", str(ctx.guild.id))
        await ctx.send("Logs channel has been removed")
                       
    @logs.group(invoke_without_command=True)
    async def channel(self, ctx):
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", "None")
            await ctx.send("You currently do not have a logs channel. Set one with ;logs channel set [channel]")
            return
        server = server[0]
        if server['logschannel'] = 'None':
            await ctx.send("You currently do not have a logs channel. Set one with ;logs channel set [channel]")
            return
        
        await ctx.send(f"The current logs channel is: {discord.utils.get(ctx.guild.channels, id=int(server['logschannel'])).mention}")
   
     @channel.command()
     async def set(self, ctx, channel:discord.Channel):
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
            if len(server) == 0: 
                await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel) VALUES ($1, $2, $3)", str(ctx.guild.id), "None", str(channel.id))
                await ctx.send(f"Your logs channel has been set to: {channel.mention}")
                return
        server = server[0]
        await self.client.pg_con.execute("UPDATE servers SET logschannel=$1 WHERE serverid=$2", str(channel.id), str(ctx.guild.id))
        await ctx.send(f"Your logs channel has been updated to: {channel.mention}")
                       
def setup(client):
    client.add_cog(ServerSetup(client))
