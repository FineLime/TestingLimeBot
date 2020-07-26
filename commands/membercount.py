import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import asyncpg

class Membercount(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def setmemberchannel(self, ctx, channel:discord.VoiceChannel):
        guild = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if not guild: 
            await self.client.pg_con.execute("INSERT INTO servers (serverid, mutedrole, logschannel, memberschannel, prefix) VALUES ($1, $2, $3, $4, $5)", str(ctx.guild.id), "None", "None", "None", ";")
        
        server = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        mchannel = channel.id
        await self.client.pg_con.execute("UPDATE servers SET memberschannel = $1 WHERE serverid = $2", str(mchannel), str(ctx.guild.id))
        await ctx.send("Did it mate! :white_check_mark:")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guildid = str(member.guild.id)
        guild = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", guildid)
        if not guild:
            return
        guild = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", guildid)
        if not guild['memberschannel']:
            return
        if guild['memberschannel'] == "None":
            return

        mchannel = get(member.guild.channels, id=int(guild['memberschannel']))
        await mchannel.edit(name=f'Membercount: {len(member.guild.members)}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guildid = str(member.guild.id)
        guild = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", guildid)
        if not guild:
            return
        guild = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", guildid)
        if not guild['memberschannel']:
            return
        if guild['memberschannel'] == "None":
            return

        mchannel = get(member.guild.channels, id=int(guild['memberschannel']))
        await mchannel.edit(name=f'Member Count: {len(member.guild.members)}')

    
        
def setup(client):
    client.add_cog(Membercount(client))
