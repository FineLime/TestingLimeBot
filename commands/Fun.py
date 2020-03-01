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
    async def penissize(self, ctx, user:discord.Member = "None"): 
        
        if user == "None": 
            user = ctx.author
            
        await ctx.send(f"{user.name}'s dick size is: 8{'='*user.id[-1:]}D")

        
def setup(client):
    client.add_cog(Fun(client))
