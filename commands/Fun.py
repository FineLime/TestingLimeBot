import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from datetime import datetime

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
        time = datetime.utcfromtimestamp(r[launch_date_unix]).strftime('%Y-%m-%dT%H:%M:%SZ')
        await ctx.send(f'Mission {r[mission_name]} is set to launch at {time}\nThe mission is:{r['details']})

        
def setup(client):
    client.add_cog(Fun(client))
