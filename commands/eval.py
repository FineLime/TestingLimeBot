import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
from discord.ext.commands.cooldowns import BucketType
import random
import string
import asyncio
from copy import copy

class Eval(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(no_pm=True)
    @commands.is_owner()
    async def eval(self, ctx, *, e):
        try: 
            await ctx.send(f'{discord.utils.escape_mentions(str(eval(e)))}`')
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
            
    @commands.command()
    @commands.is_owner()
    async def exec(self, ctx, *, e):
        try:
            exec(e)
            await ctx.send("Code ran! :white_check_mark:")
        except Exception as e:
            await ctx.send(f"Failed to run code: \n{e}")
            
    @commands.command()
    @commands.is_owner()
    async def aexec(self, ctx, *, e):
        try:
            exec(
                f'async def __ex(): ' +
                ''.join(f'\n {l}' for l in e.split('\n'))
            )

            # Get `__ex` from local variables, call it and return the result
            return await locals()['__ex']()
        except Exception as e:
            await ctx.send(f"Failed to run code: \n{e}")
            
    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, user:discord.User, *, text):
        
        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name=user.name)
        await webhook.send(str(text), username=user.name, avatar_url=user.avatar_url)
        asyncio.sleep(60)
        await webhook.delete()
        
def setup(client):
    client.add_cog(Eval(client))
