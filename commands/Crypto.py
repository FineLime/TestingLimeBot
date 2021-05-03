import discord
import requests
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import json

class Crypto(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def coin(self, ctx, c): 
        crypto = r.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        if crypto.status_code != 200: 
            await ctx.send("An error occurred trying to retrieve this crypto, please make sure it exists.")
            return
            
        price = json.loads(crypto.content)['price']
        await ctx.send(f"The average price of {c.upper()} over the last 5 minutes is ${price}."}

        
def setup(client):
    client.add_cog(Crypto(client))
