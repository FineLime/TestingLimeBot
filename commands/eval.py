import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random

class Eval(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(no_pm=True)
    @commands.is_owner()
    async def eval(self, ctx, *, e):
        try: 
            await ctx.send(f'`{str(eval(e))}`')
        except: 
            await ctx.send("Failed to run the code.")
    
    @commands.command()
    @commands.is_owner()
    async def awaitEval(self, ctx, *, e):
        try:
            await eval(e)
            await ctx.send("Code ran! :white_check_mark:")
        except:
            await ctx.send("Failed to run code.")
            
    @commands.command()
    @commands.is_owner()        
    async def awaitEvalSend(self, ctx, *, e):
        try:
            message = await eval(e)
            await ctx.send(f"{message}")
        except:
            await ctx.send("Failed to run code.")
        
def setup(client):
    client.add_cog(Eval(client))
