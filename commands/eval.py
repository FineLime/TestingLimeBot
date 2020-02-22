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
        except Exception as e: 
            await ctx.send(f"Failed to run the code: \n{e}")
    
    @commands.command()
    @commands.is_owner()
    async def awaitEval(self, ctx, *, e):
        try:
            await eval(e)
            await ctx.send("Code ran! :white_check_mark:")
        except Exception as e:
            await ctx.send(f"Failed to run code: \n{e}")
            
    @commands.command()
    @commands.is_owner()        
    async def awaitEvalSend(self, ctx, *, e):
        try:
            message = await eval(e)
            await ctx.send(f"{message}")
        except Exception as e:
            await ctx.send(f"Failed to run code: \n{e}")
        
def setup(client):
    client.add_cog(Eval(client))
