import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Shop(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True)
    async def shop(self, ctx):
        message = ""
        items = item = await self.client.pg_con.fetch("SELECT * FROM items")
        for i in items: 
            message += f"\n**{i['itemname']} - id:{i['itemid']}**
            message += f"\nPrice: {i['price']} coins\n"
            
        embed = discord.Embed(title="SHOP", description=message)
        await ctx.send(embed=embed)
    
    @shop.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def buy(self, ctx, *, i:str): 
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))
        if len(user) == 0:
            await ctx.send("Silence, I don't want to hear what you want to buy, I can see you have no money")
            return
                           
        item = await self.client.pg_con.fetch("SELECT * FROM items WHERE itemname = $1", i)
        if len(item) == 0:
            try:
                item = await self.client.pg_con.fetch("SELECT * FROM items WHERE itemid = $1", int(i))
            except Exception as e:
                print(e)
                return
        if len(item) == 0:
            await ctx.send("Could not find that item in the shop")
            return
                             
        if user[0]['coins'] >= item[0]['price']:
            await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", item[0]['price'], str(ctx.author.id), str(ctx.guild.id))
            await self.client.pg_con.execute("INSERT INTO useritems (userid, serverid, itemid, itemname) VALUES ($1, $2, $3, $4)", user[0]['userid'], user[0]['serverid'], item[0]['itemid'], item[0]['itemname'])
            await ctx.send(f"Purchased {item[0]['itemname']} for {item[0]['price']} coins!")
        else:
            await ctx.send("You can't afford that.")

        
def setup(client):
    client.add_cog((client))
