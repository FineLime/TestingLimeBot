import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import datetime
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
    async def launch(self, ctx, *, lsp=None):
        
        r = ""
        if True:
            r = requests.get('https://ll.thespacedevs.com/2.0.0/launch/upcoming/?status=1')
        else:
            pass
                        
        r = json.loads(r.content)['results'][0]
                  
        try:
            
            status = r['status']['id']
            try: 
                time = r['net'].split("T")
                ymd = time[0].split("-")
                hms = time[1].split(":")
                time = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hms[0]), int(hms[1]), int(hms[2][0:2]))
                if time < datetime.datetime.now(): 
                    time = 'TBD'
            except:
                time = 'TBD'

            if status == 3:
                displayTime = '- Successful'
                T =  'Launched Successfully'
            elif time == 'TBD':
                displayTime = '- TBD'     
                T = 'Launch Time - TBD'
            else: 
                e = time - datetime.datetime.now()
                e = divmod(e.days * 86400 + e.seconds, 60);
                minutes = e[0]
                days = math.floor(minutes/1440)
                minutes -= days*1440
                hours = math.floor(minutes/60)
                minutes -= hours*60
                displayTime = time.strftime("on %B %d, %Y at %I:%M%p UTC")
                T = f'T- {days} days, {hours} hours, {minutes} minutes, {e[1]} seconds'
            link = ""
            if r['webcast_live']: 
                link = f"\n\n[Watch here]({r['webcast_live']})"
            
            mission = r['mission']['description']
            missionname = r['mission']['name']
            embed = discord.Embed(title=f'{missionname} {displayTime}', description=f'{mission}\n\n{T}{link}')
            await ctx.send(embed=embed)
        except Exception as e:
            print (e.message)
            
        
def setup(client):
    client.add_cog(Fun(client))
