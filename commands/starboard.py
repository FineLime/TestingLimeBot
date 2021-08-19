import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Starboard(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def starboard(self, ctx): 
        await ctx.send("**USAGE:** \n;starboard channel set {channel} \n;starboard remove \n;starboard minimumstars [minimumstars]")
        
    @starboard.command()
    async def remove(self, ctx): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, memberschannel) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", "None", "None")
            await ctx.send("You do not have a starboard channel.")
            return
        
        server = server[0]
        if server['starboardchannel'] == 'None' or server['starboardchannel'] is None:
            await ctx.send("You do not have a starboard channel.")
            return
        
        await self.client.pg_con.execute("UPDATE servers SET starboardchannel='None' WHERE serverid=$1", str(ctx.guild.id))
        await ctx.send("Starboard channel has been removed")
        
    @starboard.group(invoke_without_command=True)
    async def channel(self, ctx):
        
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, memberschannel) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", "None", "None")
            await ctx.send("You currently do not have a starboard channel.")
            return
        server = server[0]
        if server['starboardchannel'] == 'None' or server['starboardchannel'] is None:
            await ctx.send("You currently do not have a starboard channel.")
            return
        
        await ctx.send(f"The current logs channel is: {discord.utils.get(ctx.guild.channels, id=int(server['starboardchannel'])).mention}")
        
    @channel.command()
    async def set(self, ctx, channel:discord.TextChannel): 
        
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, memberschannel) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", str(channel.id), "None")
            await ctx.send(f"Your logs channel has been set to: {channel.mention}")
            return
        server = server[0]
        await self.client.pg_con.execute("UPDATE servers SET starboardchannel=$1 WHERE serverid=$2", str(channel.id), str(ctx.guild.id))
        await ctx.send(f"Your starboard channel has been updated to: {channel.mention}")
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload): 
        
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(payload.guild_id))

        
def setup(client):
    client.add_cog(Starboard(client))
