import discord
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
import asyncpg
import datetime
import sys

class Moderation(commands.Cog): 

    def __init__(self, client):
        self.client = client
    
    '''[WIP]
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user:discord.Member, time, *, reason='No reason given'):
        role = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
        if len(role) == 0:
            await ctx.send("There is not a mute role set up in this server! Set one up with ;muterole [role]")
            return
        role = role[0]
        if role['mutedrole'] == 'None':
            await ctx.send("There is not a mute role set up in this server! Set one up with ;muterole [role]")
            return
        
        if ctx.author.top_role.position > user.top_role.position:
            
            if time[-1] not in ['m', 'h', 'd']:
                await ctx.send("**USAGE:** ;mute user [time] {reason}\nTo set time, put 'm', 'h', or 'd' after a number. Max 7 days.")
                return
            
            try:
                num = int(time[:-1])
            except:
                await ctx.send("**USAGE:** ;mute user [time] {reason}\nTo set time, put 'm', 'h', or 'd' after a number. Max 7 days.")
                return
            
            logtime = f'{time[:-1]}'
            if time[-1] == 'd':
                num *= 1440
                logtime += ' days'
            elif time[-1] == 'h':
                num *= 60
                logtime += ' hours'
            else:
                logtime += ' minutes'
                
            mutetime = datetime.timedelta(minutes=num)
            unmute = datetime.datetime.now() + datetime.timedelta(minutes=num)
            
            try:
                await self.client.pg_con.execute("INSERT INTO mutes (user, server, unmute) VALUES ($1, $2, $3)", str(user.id), str(ctx.guild.id), unmute.strftime('%d/%m/%Y %H:%M'))
            except:
                print(f"This is not working: {sys.exc_info()[0]}")
                print(f"num: {num}\nuser:{user.id},unmute: {unmute.strftime('%d/%m/%Y %H:%M')})
                
            await user.add_roles(discord.utils.get(ctx.guild.roles, id=role['mutedrole'])) 
            
            try:
                await user.send(f"You have been muted in **{ctx.guild.name}** for {logtime}\nReason:`{reason}`")
            except:
                pass
            
            if role["logschannel"] != "None": 
                embed = discord.Embed(title="Logs | User Muted")
                embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="User", value=f"{user.name}#{user.discriminator} ({user.mention})", inline=True)
                embed.add_field(name="Mute Time", value=logtime, inline=True)
                embed.add_field(name="Reason", value=reason, inline=True)
                await get(ctx.guild.channels, id=int(role["logschannel"])).send(embed=embed)
    
    @tasks.loop(seconds=60)
    async def unmute_users(self):
        unmute = await self.client.pg_con.fetch("SELECT * FROM mutes WHERE unmute=$1", datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
        for i in unmute:
            try:
                role = await self.client.pg_con.fetchrow("SELECT * FROM servers WHERE serverid=$1", i['server'])
                if role["logschannel"] != "None": 
                    embed = discord.Embed(title="Logs | User Unmuted")
                    embed.set_author(name="Limebot", icon_url=self.client.user.avatar_url)
                    embed.add_field(name="Moderator", value='LimeBot')
                    embed.add_field(name="User", value=f"<@{i['user']}>", inline=True)
                    embed.add_field(name="Reason", value='Mute Ended', inline=True)
                    await get(ctx.guild.channels, id=int(role["logschannel"])).send(embed=embed)
                                    
            except:
                pass
                                    
            try:
                server = discord.utils.get(self.client.guilds, id=int(i['server']))
                discord.utils.get(server.members, id=int(i['user'])).remove_roles(discord.utils.get(server.roles, id=int(role['mutedrole'])))
                                                                                  
            except:
                pass
                                                                                  
            self.client.pg_con.execute("DELETE FROM mutes WHERE server=$1 AND user=$2", i['server'], i['user'])                                                                           
    
    '''
                                    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user : discord.Member, *, reason='No reason given'): 
        if ctx.author.top_role.position > user.top_role.position: 
            try:
                await user.send(f"You have been kicked from **{ctx.guild.name}**\nReason:`{reason}`")
            except:
                pass
            await user.kick(reason=reason)
            await ctx.send(f"**{user.name}** has been kicked by **{ctx.author.name}**\nReason:`{reason}`")
        else: 
            await ctx.send("You don't have permission to use that command")
            return
            
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
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
    async def ban(self, ctx, user : discord.Member, *, reason='No reason given'): 
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
        
        server = await self.client.pg_con.fetch("SELECT * FROM servers WHERE serverid=$1", str(ctx.guild.id))
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
