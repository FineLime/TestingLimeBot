import discord
import requests
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import json

class Crypto(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["crypto"])
    @commands.cooldown(1, 10, BucketType.user)
    async def coin(self, ctx, c): 
        crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        if crypto.status_code != 200: 
            await ctx.send("An error occurred trying to retrieve this crypto, please make sure it exists.")
            return
            
        price = json.loads(crypto.content)['price']
        await ctx.send(f"The average price of {c.upper()} over the last 5 minutes is \${price}.")
        
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def wallet(self, ctx): 
        coins = await self.client.pg_con.fetch("SELECT * FROM crypto WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id))
        if len(coins) == 0: 
            await ctx.send("You don't have any crypto.") 
            return 
        
        msg = ""
        for i in coins: 
            crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={i["crypto"]}USDT')
            price = float(json.loads(crypto.content)['price'])
            total = "{:.5f}".format(float(i["amount"])*float(price))
            msg += f'Crypto: {i["crypto"]} - Price: {price} - Amount: {i["amount"]} - Total: ${total} \n'
                
        await ctx.send(f"Your wallet: \n\n{msg}")
        
   
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user) 
    async def buy(self, ctx, c, lcoins:int): 
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
        if len(user) == 0: 
            await ctx.send("You don't have any limecoins") 
            return
        if user[0]['coins'] < lcoins: 
            await ctx.send("You don't have that many limecoins") 
        crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        if crypto.status_code != 200: 
            await ctx.send("An error occurred trying to retrieve this crypto, please make sure it exists.")
            return
        price = json.loads(crypto.content)['price'] 
        wallet = await self.client.pg_con.fetch("SELECT * FROM crypto WHERE serverid=$1 AND userid=$2 AND crypto = $3", str(ctx.guild.id), str(ctx.author.id), c.upper())
        if len(wallet) == 0: 
            await self.client.pg_con.execute("INSERT INTO crypto (userid, serverid, crypto, amount) VALUES ($1, $2, $3, $4)", str(ctx.author.id), str(ctx.guild.id), c.upper(), 0)
        
        amount = float("{:.5f}".format(lcoins/float(price)))
        await self.client.pg_con.execute("UPDATE crypto SET amount = amount + $1 WHERE userid = $2 AND serverid = $3 AND crypto = $4", amount, str(ctx.author.id), str(ctx.guild.id), c.upper())
        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", lcoins, str(ctx.author.id), str(ctx.guild.id))
        await ctx.send(f"Bought {amount} {c} for {lcoins}!")

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def sell(self, ctx, c, amount:float): 
        
        if len(str(amount).split('.')[1]) > 5: 
            await ctx.send("Max 5 decimal places")
            return 
        
        wallet = await self.client.pg_con.fetch("SELECT * FROM crypto WHERE serverid=$1 AND userid=$2 AND crypto = $3", str(ctx.guild.id), str(ctx.author.id), c.upper())
        if len(wallet) == 0: 
            await ctx.send("Crypto not found in your wallet") 
            return
        
        if amount > wallet[0]['amount']: 
            await ctx.send(f"You don't have that much {c.upper()}.")
            return
        
        crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        price = json.loads(crypto.content)['price'] 
        lcoins = float("{:.5f}".format(amount*float(price)))
        
        await self.client.pg_con.execute("UPDATE crypto SET amount = amount - $1 WHERE userid = $2 AND serverid = $3 AND crypto = $4", amount, str(ctx.author.id), str(ctx.guild.id), c.upper())
        await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", lcoins, str(ctx.author.id), str(ctx.guild.id))
        await ctx.send(f"Sold {amount} {c.upper()} for {lcoins} coins.") 
        
def setup(client):
    client.add_cog(Crypto(client))
