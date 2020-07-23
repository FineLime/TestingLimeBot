import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from datetime import datetime
import requests
import math
import json
import urllib.request

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
    async def spaceX(self, ctx):
        
        r = requests.get('https://api.spacexdata.com/v3/launches/next').json()
        time = datetime.utcfromtimestamp(r['launch_date_unix'])
        displayTime = ""
        T = ""
        if time > datetime.now() and time is not None:
            e = time - datetime.now()
            e = divmod(e.days * 86400 + e.seconds, 60);
            minutes = e[0]
            days = math.floor(minutes/1440)
            minutes -= days*1440
            hours = math.floor(minutes/60)
            minutes -= hours*60
            displayTime = time.strftime("on %B %d, %Y at %I:%M%p UTC")
            T = f'{days} days, {hours} hours, {minutes} minutes, {e[1]} seconds'
        else:
            displayTime = ""
            T = 'TBD'
            
        link = ""
        if r['links']['video_link']: 
            link = f"\n\nWatch here: {r['links']['video_link']}"
        embed = discord.Embed(title=f'{r["mission_name"]} {displayTime}', description=f"{r['details']}{link}\n\nT- {T}")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def launch(self, ctx):
                              
        req = urllib.request.Request(
            "https://launchlibrary.net/1.4/launch/next/1", 
            headers={
            'User-Agent': 'LimeBot for discord'
        })
        r = urllib.request.urlopen(req).read().decode('utf-8')
        r = json.loads(r)
        r = r['launches'][0]
        try: 
            time = datetime.utcfromtimestamp(r['netstamp'])
            if time < datetime.now(): 
                time = 'TBD'
        except:
            time = 'TBD'
                              
        if time == 'TBD':
            displayTime = '- TBD'     
            T = 'TBD'
        else: 
            e = time - datetime.now()
            e = divmod(e.days * 86400 + e.seconds, 60);
            minutes = e[0]
            days = math.floor(minutes/1440)
            minutes -= days*1440
            hours = math.floor(minutes/60)
            minutes -= hours*60
            displayTime = time.strftime("on %B %d, %Y at %I:%M%p UTC")
            T = f'{days} days, {hours} hours, {minutes} minutes, {e[1]} seconds'
        link = ""
        if r['vidURLs']: 
            link = f"\n\nWatch here: {r['vidURLs'][0]}"
        embed = discord.Embed(title=f'{r["missions"][0]["name"]} {displayTime}', description=f'{r["missions"][0]["description"]}{link}\n\nT- {T}')
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def launchtest(self, ctx):
                              
        r = requests.get('https://ll.thespacedevs.com/2.0.0/launch/upcoming/limit=10&offset=10').json()
        r = r['launches'][0]
        status = r['launches'][0]['status']
        try: 
            time = datetime.utcfromtimestamp(r['netstamp'])
            if time < datetime.now(): 
                time = 'TBD'
        except:
            time = 'TBD'
        
        if status == 3: 
            displayTime= " - Successful"
            T = 'Launched Successfully'
        if time == 'TBD':
            displayTime = '- TBD'     
            T = 'T- TBD'
        else: 
            e = time - datetime.now()
            e = divmod(e.days * 86400 + e.seconds, 60);
            minutes = e[0]
            days = math.floor(minutes/1440)
            minutes -= days*1440
            hours = math.floor(minutes/60)
            minutes -= hours*60
            displayTime = time.strftime("on %B %d, %Y at %I:%M%p UTC")
            T = f'T- {days} days, {hours} hours, {minutes} minutes, {e[1]} seconds'
        link = ""
        if r['vidURLs']: 
            link = f"\n\nWatch here: {r['vidURLs'][0]}"
        embed = discord.Embed(title=f'{r["missions"][0]["name"]} {displayTime}', description=f'{r["missions"][0]["description"]}{link}\n\n{T}')
        await ctx.send(embed=embed)
        
def setup(client):
    client.add_cog(Fun(client))
