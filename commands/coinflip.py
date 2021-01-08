import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random

class Coinflip(commands.Cog): 

    def __init__(self, client):
        self.client = client
    
    '''
    @commands.command(aliases=["flip", "coin", "flipcoin"])
    @commands.cooldown(1, 10, BucketType.user)
    async def coinflip(self, ctx): 
        await ctx.send(f'I flipped a coin and it landed on {random.choice(["heads", "tails"])}')
    '''

        
def setup(client):
    client.add_cog(Coinflip(client))
