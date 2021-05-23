import discord
import requests
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
import json
import asyncio

class Crypto(commands.Cog): 

    def __init__(self, client):
        self.client = client
        self.update_crypto.start()
        asyncio.sleep(10)
        self.do_limits.start()
    
    @tasks.loop(seconds=61)
    async def update_crypto(self):
        
        print("updating crypto prices")
        cryptoList = json.loads(requests.get("https://api.binance.com/api/v3/ticker/24hr").content)
        dontRefresh = True
        for c in self.client.crypto: 
            
            crypto = self.client.crypto[c]
            compare = cryptoList[crypto['id']] 
            if compare['symbol'] == crypto['symbol']: 
                cryptoid = crypto['id']
                self.client.crypto[c] = compare
                self.client.crypto[c]['id'] = cryptoid
                await asyncio.sleep(60/len(self.client.crypto))
                continue 
            
            dontRefresh = False
            break
        
        if dontRefresh: 
            return
        
        print("Resetting crypto list")
        crypto = json.loads(requests.get("https://api.binance.com/api/v3/ticker/24hr").content)
        self.client.crypto = {}
        for index, i in enumerate(crypto): 
            if i['symbol'].endswith(("BUSD", "USDT", "USDC")) and i['symbol'][:-4] not in self.client.crypto: 
                self.client.crypto[i['symbol'][:-4]] = i
                self.client.crypto[i['symbol'][:-4]]['id'] = index
    
    
    @tasks.loop(seconds=61)
    async def do_limits(self): 
        
        limits = await self.client.pg_con.fetch("SELECT * FROM limits")
        for limit in limits: 
            coin = self.client.crypto[limit['coin']]
            if not coin['lastPrice'] <= limit['price'] and limit['type'] == 'buy': 
                continue
            if not coin['lastPrice'] >= limit['price'] and limit['type'] == 'sell': 
                continue
                
            server = discord.utils.get(self.client.guilds, id=int(limit['serverid']))
            user = discord.utils.get(server.members, id=int(limit['userid']))
            userDB = self.client.pg_con.fetch('SELECT * FROM users WHERE userid = $1 AND serverid = $2', limit['userid'], limit['serverid'])[0]
            
            if limit['type'] == 'buy':
                
                if userDB['coins'] <= 0: 
                    await user.send(f"You set up a limit to buy {limit['coin']} for {limit['percentage']} of your coins in {server.name} but you don't have any.")
                else: 
                    price = userDB['coins']/100*limit['percentage']
                    coinsAmount = price/coin['lastPrice']
                    await self.client.pg_con.execute("UPDATE crypto SET amount = amount + $1 WHERE userid = $2 AND serverid = $3 AND crypto = $4", coinsAmount, limit['userid'], limit['serverid'], limit['coin'])
                    await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", price, limit['userid'], limit['serverid'])
                    await user.send(f"You bought {coinsAmount} of {limit['coin']} for {price} limecoins in {server.name} with your limit buy.")
                    
                await self.client.pg_con.execute("DELETE FROM limits WHERE userid = $1 AND serverid = $2 AND coin = $3 AND price = $4 AND limittype = $5", limit['userid'], limit['serverid'], limit['coin'], limit['price'], limit['limittype'])
                
            elif limit['type'] == 'sell': 
                
                crypto = self.client.pg_con.fetch('SELECT * FROM crypto WHERE userid = $1 AND serverid = $2 AND coin = $3', limit['userid'], limit['serverid'], limit['coin']) 
                if len(crypto) == 0: 
                    await user.send(f"You set up a limit to sell {limit['percentage']} of your {limit['coin']} in {server.name} but you don't have any.")
                elif crypto['amount'] <= 0: 
                    await user.send(f"You set up a limit to sell {limit['percentage']} of your {limit['coin']} in {server.name} but you don't have any.")
                else: 
                    crypto = crypto[0]
                    coinsAmount = crypto['amount']/100*limit['percentage']
                    limecoins = coinsAmount*coin['lastPrice']
                    await self.client.pg_con.execute("UPDATE crypto SET amount = amount - $1 WHERE userid = $2 AND serverid = $3 AND crypto = $4", coinsAmount, limit['userid'], limit['serverid'], limit['coin'])
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", limecoins, limit['userid'], limit['serverid'])
                    await user.send(f"You sold {coinsAmount} of {limit['coin']} for {price} limecoins in {server.name} with your limit sell.")
                    
                    
    @commands.group()
    @commands.cooldown(1, 5, BucketType.user)
    async def limit(self, ctx): 
        
        await ctx.send("You can automatically buy/sell crypto with limits, i will add info on how it works later") 
        
    @limit.command()
    async def buy(self, ctx, coin, price:float, percentage:int): 
        
        coin = coin.upper()
        try: 
            coin = self.client.crypto['coin']
        except: 
            await ctx.send("Coin does not exist")
            return 
        
        if percentage > 100 or percentage <= 0: 
            await ctx.send("Percentage must be between 1-100%") 
            return 
        
        await self.client.pg_con.execute("INSERT INTO limits (limittype, coin, price, percentage, userid, serverid) VALUES ('buy', $1, $2, $3, $4, $5)", coin, price, percentage, string(ctx.author.id), str(ctx.guild.id))
        await ctx.send("Created new limit (W.I.P.)")
    
    @commands.command(aliases=["crypto"])
    @commands.cooldown(1, 10, BucketType.user)
    async def coin(self, ctx, c): 
        
        #crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        #if crypto.status_code != 200: 
        #    crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}BUSD') 
        #    if crypto.status_code != 200:
        #        await ctx.send("An error occurred trying to retrieve this crypto, please make sure it exists.")
        #        return
            
        #price = json.loads(crypto.content)['price']
        
        try:
            price = self.client.crypto[c.upper()]['lastPrice']
        except: 
            await ctx.send("Crypto not found.")
        await ctx.send(f"The average price of {c.upper()} over the last minute is \${price}.")
        
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def wallet(self, ctx): 
        coins = await self.client.pg_con.fetch("SELECT * FROM crypto WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id))
        if len(coins) == 0: 
            await ctx.send("You don't have any crypto.") 
            return 
        
        msg = ""
        for i in coins: 
            busd = False
            crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={i["crypto"]}USDT')
            if crypto.status_code != 200: 
                busd = True
                crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={i["crypto"]}BUSD') 
                                  
            price = float(json.loads(crypto.content)['price'])
            total = "{:.5f}".format(float(i["amount"])*float(price))
            msg += f'[${i["crypto"]}](https://www.binance.com/en/trade/{i["crypto"]}_{"BUSD" if busd else "USDT"}?type=spot) - Price: {price} - Amount: {i["amount"]} - Total: ${total} \n'
        
        embed = discord.Embed(title=f"", description=msg, color=0x00ff00)     
        embed.set_author(name=f"{ctx.author.name}'{'' if ctx.author.name[-1:] == 's' else 's'} Crypto Wallet", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        
   
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user) 
    async def buy(self, ctx, c, lcoins:int): 
        
        if lcoins <= 0: 
            await ctx.send("You must invest at least 1 limecoin")
            return
                         
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
        if len(user) == 0: 
            await ctx.send("You don't have any limecoins") 
            return
                                  
        if user[0]['coins'] < lcoins: 
            await ctx.send("You don't have that many limecoins") 
            return
                                  
        crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
                                  
        if crypto.status_code != 200: 
                                  
            crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}BUSD') 
                                  
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
        await ctx.send(f"Bought {amount} {c} for {lcoins} limecoins!")

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def sell(self, ctx, c, amount): 
        
        wallet = await self.client.pg_con.fetch("SELECT * FROM crypto WHERE serverid=$1 AND userid=$2 AND crypto = $3", str(ctx.guild.id), str(ctx.author.id), c.upper())
        if len(wallet) == 0: 
            await ctx.send("Crypto not found in your wallet") 
            return
                         
        try: 
            amount = float(amount)
        except: 
            if amount in ["*", "max", "all"]: 
                await self.client.pg_con.execute("DELETE FROM crypto WHERE userid = $1 AND serverid = $2 AND crypto = $3", str(ctx.author.id), str(ctx.guild.id), c.upper())
                amount = float(wallet[0]["amount"])
                         
                crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
                if crypto.status_code != 200: 
                    crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}BUSD') 
                price = json.loads(crypto.content)['price'] 
                lcoins = float("{:.5f}".format(amount*float(price)))
                         
                await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", lcoins, str(ctx.author.id), str(ctx.guild.id))
                await ctx.send(f"Sold all of your {c.upper()} for {lcoins}")
                return
                         
            else:
                await ctx.send("Amount must be a number or 'all'")
                return
                         
        if amount <= 0: 
            await ctx.send(f"You must withdraw more than 0 {c.upper()}")
            return
                         
        if len(str(amount).split('.')[1]) > 5: 
            await ctx.send("Max 5 decimal places")
            return 
        
        if amount > wallet[0]['amount']: 
            await ctx.send(f"You don't have that much {c.upper()}.")
            return
        
        crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}USDT')
        if crypto.status_code != 200: 
            crypto = requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={c.upper()}BUSD') 
        price = json.loads(crypto.content)['price'] 
        lcoins = float("{:.5f}".format(amount*float(price)))
        
        if wallet[0]['amount'] - amount == 0: 
            await self.client.pg_con.execute("DELETE FROM crypto WHERE userid = $1 AND serverid = $2 AND crypto = $3", str(ctx.author.id), str(ctx.guild.id), c.upper())
        else:
            await self.client.pg_con.execute("UPDATE crypto SET amount = amount - $1 WHERE userid = $2 AND serverid = $3 AND crypto = $4", amount, str(ctx.author.id), str(ctx.guild.id), c.upper())
        
        await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", lcoins, str(ctx.author.id), str(ctx.guild.id))
        await ctx.send(f"Sold {amount} {c.upper()} for {lcoins} coins.") 
        
def setup(client):
    client.add_cog(Crypto(client))
