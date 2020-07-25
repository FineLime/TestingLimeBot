import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import asyncpg

class Moderation(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user : discord.Member, *, reason=None): 
        if ctx.author.top_role.position > user.top_role.position: 
            await user.send(f"You have been kicked from **{ctx.guild.name}**\nReason:`{reason}`")
            await user.kick(reason=reason)
            await ctx.send(f"**{user.name}** has been kicked by **{ctx.author.name}**\nReason:`{reason}`")
        else: 
            await ctx.send("You don't have permission to use that command")
            return
            
        await self.client.pg_con.execute("INSERT INTO reactionroles (messageid, roleid, channelid, emoji) VALUES ($1, $2, $3, $4)", msgid, roleid, str(ctx.channel.id), emoji)
        if len(server) > 0: 
            if server[0]["logschannel"] != "None": 
                embed = discord.Embed(title="Logs | User Kicked")
                embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="User", value=f"{user.name}#{user.discriminator} ({user.mention})", inline=True)
                embed.add_field(name="Reason", value=reason, inline=True)
                await get(ctx.guild.channels, id=int(server[0]["logschannel"])).send(embed=embed)
        
            
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user : discord.Member, *, reason=None): 
        if ctx.author.top_role.position > user.top_role.position: 
            try:
                await user.send(f"You have been banned from **{ctx.guild.name}**\nReason:`{reason}`")
            except:
                pass
            await user.ban(reason=reason)
            await ctx.send(f"**{user.name}** has been banned by **{ctx.author.name}**\nReason:`{reason}`")
        else: 
            await ctx.send("You don't have permission to use that command")        
            return
        
        await self.client.pg_con.execute("INSERT INTO reactionroles (messageid, roleid, channelid, emoji) VALUES ($1, $2, $3, $4)", msgid, roleid, str(ctx.channel.id), emoji)
        if len(server) > 0: 
            if server[0]["logschannel"] != "None": 
                embed = discord.Embed(title="Logs | User Banned")
                embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="User", value=f"{user.name}#{user.discriminator} ({user.mention})", inline=True)
                embed.add_field(name="Reason", value=reason, inline=True)
                await get(ctx.guild.channels, id=int(server[0]["logschannel"])).send(embed=embed)
        
def setup(client):
    client.add_cog(Moderation(client))
