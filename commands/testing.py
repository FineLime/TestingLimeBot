import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Testing(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.group(pass_context=True)
    @commands.cooldown(1, 10, BucketType.user)
    async def test(self, ctx): 
        if ctx.invoked_subcommand is None:
            await ctx.send('You did not use a subcommand')
            
    @test.command()
    async def this(self, ctx):
        await ctx.send('You used the \'this\' subcommand')
          
    @test.command()
    async def that(self, ctx):
        await ctx.send('You used the \'that\' subcommand')   
        
    @commands.group(pass_context=True)
    @commands.cooldown(1, 10, BucketType.user)
    async def test2(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('You did not use a subcommand on test 2')
            
    @test2.command()
    async def sub(self, ctx):
        await ctx.send('You did use a subcommand on test 2')   
        
def setup(client):
    client.add_cog(Testing(client))
