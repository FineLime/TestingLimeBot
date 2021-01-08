import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import time
import asyncpg

class Currency(commands.Cog): 

    def __init__(self, client):
        self.client = client
       
    @commands.Cog.listener()
    async def on_message_sent(message): 
        
        author = ctx.message.author
        if author.bot:
            return
        
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE server=$1 AND user=$2", str(message.guild.id), str(author.id))
        
        if user is None: 
            await self.client.pg_con.execute('''INSERT INTO Users (user, server, coins, time) VALUES ($1, $2, $3, $4)''', str(author.id), str(message.guild.id), 100, str(int(time.time())))
            return
            
        user = await self.client.pg_con.fetchone("SELECT * FROM users WHERE server=$1 AND user=$2", str(message.guild.id), str(author.id))
        if (time.time - user["time"]) > 60: 
            await self.client.pg_con.execute("UPDATE Users SET coins = $1, time = $2 WHERE user = $3 AND server = $4", user['coins']+random.randint(20, 100), str(int(time.time())), author.id, message.guild.id)
            
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def coins(self, ctx):
        user = await self.client.pg_con.fetchone("SELECT * FROM users WHERE server=$1 AND user=$2", str(ctx.guild.id), str(ctx.author.id))
        await ctx.send(f"You have {user['coins']} coin(s)")
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def slots(self, ctx): 
        
        choices1 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]
        choices2 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]
        choices3 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]

        slots1 = random.choice(choices1)
        slots2 = random.choice(choices2)
        slots3 = random.choice(choices3)

        choices1.remove(slots1)
        choices2.remove(slots2)
        choices3.remove(slots3)

        fslots1 = random.choice(choices1)
        fslots2 = random.choice(choices2)
        fslots3 = random.choice(choices3)

        choices1.remove(fslots1)
        choices2.remove(fslots2)
        choices3.remove(fslots3)

        fslots4 = random.choice(choices1)
        fslots5 = random.choice(choices2)
        fslots6 = random.choice(choices3)

        win = "Sorry, you lost!"
        if slots1 == slots2 == slots3: 
            win = "Winner!!! You won nothing! Congratz!"
        await ctx.send(f"|   {fslots1}{fslots2}{fslots3}\n\▶{slots1}{slots2}{slots3}\n|   {fslots4}{fslots5}{fslots6}\n{win}")



def setup(client):
    client.add_cog(Currency(client))
