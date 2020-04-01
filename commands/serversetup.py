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
    async def muterole(self, ctx, muterole:str): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, banned_words) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", "None", "")
        
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        mutedrole = get(ctx.guild.roles, id=int(muterole))
        if mutedrole == None:
            await ctx.send("That's not a role id!")
            return
        await self.client.pg_con.execute("UPDATE servers SET mutedrole = $1 WHERE serverid=$2", muterole, str(ctx.guild.id))
        if server['logschannel'] != "None":
            embed = discord.Embed(title="Logs | MutedRole", description="The server's mute role has been changed.")
            embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="MutedRole", value=mutedrole.mention, inline=True)
            await get(ctx.guild.channels, id=int(server['logschannel'])).send(embed=embed)

        await ctx.send("The mute role has been changed! :white_check_mark:")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def logschannel(self, ctx, ch:str): 
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, banned_words) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", "None", "")
        
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        logsc = get(ctx.guild.channels, id=int(ch))
        if logsc == None:
            await ctx.send("That's not a channel id!")
            return
        await self.client.pg_con.execute("UPDATE servers SET logschannel = $1 WHERE serverid=$2", ch, str(ctx.guild.id))
        if server['logschannel'] != "None":
            embed = discord.Embed(title="Logs | Logs channel", description="The server's logs channel has been changed.")
            embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Channel", value=logsc.mention, inline=True)
            await get(ctx.guild.channels, id=int(server['logschannel'])).send(embed=embed)

        await ctx.send("The mute role has been changed! :white_check_mark:")
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def banword(self, ctx, word):
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(server) == 0: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, banned_words) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), "None", "None", "")
        
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        banned_words = server['banned_words']
        if str(banned_words) == "None": 
            banned_words = ""
        if word.lower() in banned_words.split(): 
            await ctx.send("This word is already banned")
            return
        else: 
            await self.client.pg_con.execute("UPDATE servers SET banned_words = $1 WHERE serverid=$2", f"{banned_words} {word.lower()}", str(ctx.guild.id))
            await ctx.send("The word has been banned!")
         
    @commands.Cog.listener() 
    async def on_message(self, message):
        await message.add_reaction("🤡")
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(message.guild.id))
        if len(server) == 0: 
            return
        server = server[0]
        for word in server['banned_words'].split(): 
            if word in message.content.lower(): 
                await message.delete()
                break;
        
def setup(client):
    client.add_cog(ServerSetup(client))
