import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from datetime import datetime
import requests
import math

class Fun(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def avatar(self, ctx, user:discord.Member = "None"): 
        
        if user == "None": 
            user = ctx.author
        
        embed = discord.Embed(title=f"{user.name}#{user.discriminator}", color=0x00ff00)
        embed.set_image(url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
        await ctx.send(embed=embed)
        
    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.badArgument):
            await ctx("I couldn't find a member by that name.")
            
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def launch(self, ctx):
        r = requests.get('https://api.spacexdata.com/v3/launches/next').json()
        time = datetime.utcfromtimestamp(r['launch_date_unix'])
        e = time - datetime.now()
        e = divmod(e.days * 86400 + e.seconds, 60);
        minutes = e[0]
        days = math.floor(minutes/1440)
        minutes -= days*1440
        hours = math.floor(minutes/60)
        minutes -= hours*60
        embed = discord.Embed(title=f'{r["mission_name"]} on {time.strftime("%B %d, %Y at %I:%M%p")}', description=f"{r['details']}\n\nT- {days}, days, {hours}, hours, {minutes}, minutes, {e[1]}, seconds")
        
        await ctx.send(embed=embed)

        
def setup(client):
    client.add_cog(Fun(client))
