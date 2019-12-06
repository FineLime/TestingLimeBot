import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Fun(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def avatar(self, ctx, user:discord.Member = "None"): 
        
        if user == "None": 
            user = ctx.author
        
        embed = discord.Embed(title=user.mention, color=0x00ff00)
        embed.set_image(url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.mention}")
        await get(ctx.guild.channels, id=int(server[0]["logschannel"])).send(embed=embed)

        
def setup(client):
    client.add_cog(Fun(client))
