import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import asyncpg

class Addreactionrole(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def createreactionrole(self, ctx, msgid:str, roleid:discord.Role, emoji:str): 
        roleid = str(roleid.id)
        rr = await self.client.pg_con.fetch("SELECT * FROM reactionroles WHERE channelid=$1 AND messageid=$2 AND emoji=$3", str(ctx.channel.id), msgid, emoji)
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(rr) > 0: 
            await ctx.send("This message already has a reaction role assigned to it with this emoji.")
            return

        try:
            message = await ctx.channel.fetch_message(int(msgid))
        except: 
            await ctx.send("I couldn't find that message id in this channel, please make sure you're using the command in the right channel and you have the correct message id")
            return

        role = get(ctx.guild.roles, id=int(roleid)) 
        if role == None: 
            await ctx.send("I couldn't find a role in the server with that ID, please make sure you have the correct role id")
            return
        try:
            await message.add_reaction(emoji)
        except: 
            await ctx.send("That's not an emoji!")
            return

        await self.client.pg_con.execute("INSERT INTO reactionroles (messageid, roleid, channelid, emoji) VALUES ($1, $2, $3, $4)", msgid, roleid, str(ctx.channel.id), emoji)
        if len(server) > 0: 
            if server[0]["logschannel"] != "None": 
                embed = discord.Embed(title="Logs | Reactionrole", description="New Reactionrole", url=f"https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{msgid}")
                embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="Emoji", value=emoji, inline=True)
                embed.add_field(name="Role", value=role.mention, inline=True)
                await get(ctx.guild.channels, id=int(server[0]["logschannel"])).send(embed=embed)
        await ctx.send("Successfully created a reaction role! :white_check_mark:")
        
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def deletereactionrole(self, ctx, msgid:str, emoji:str):
        await self.client.pg_con.execute("DELETE FROM reactionroles WHERE messageid=$1 AND emoji=$2", msgid, emoji)
        try:
            message = await ctx.channel.fetch_message(int(msgid))
        except:
            print("oof")
        await message.clear_reaction(emoji)
        await message.add_reaction("👍")
        await ctx.send("Reaction role successfully deleted")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): 
        rr = await self.client.pg_con.fetch("SELECT * FROM reactionroles WHERE messageid=$1 AND emoji=$2", str(payload.message_id), str(payload.emoji))
        if len(rr) == 0:
            return

        rr = rr[0]
        guild = get(self.client.guilds, id=payload.guild_id)
        user = get(guild.members, id=payload.user_id)
        role = get(guild.roles, id=int(rr["roleid"]))
        await user.add_roles(role)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload): 
        rr = await self.client.pg_con.fetch("SELECT * FROM reactionroles WHERE messageid=$1 AND emoji=$2", str(payload.message_id), str(payload.emoji))
        if len(rr) == 0:
            return

        rr = rr[0]
        guild = get(self.client.guilds, id=payload.guild_id)
        user = get(guild.members, id=payload.user_id)
        role = get(guild.roles, id=int(rr["roleid"]))
        await user.remove_roles(role)



        
def setup(client):
    client.add_cog(Addreactionrole(client))
