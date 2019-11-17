import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import asyncpg 

class Slots(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user) 
    async def slotsleaderboard(self, ctx): 
        leaderboard = await self.client.pg_con.fetch("SELECT * FROM users ORDER BY slotwins DESC NULLS LAST")
        await ctx.send(f"```1) {leaderboard[0]['name']} - {leaderboard[0]['slotwins']}\n2) {leaderboard[1]['name']} - {leaderboard[1]['slotwins']}\n3) {leaderboard[2]['name']} - {leaderboard[2]['slotwins']}```")
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user) 
    async def slotswins(self, ctx): 
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE id = $1", str(ctx.author.id))
        if not user: 
            await self.client.pg_con.execute("INSERT INTO users (id, name, coins, inventory, slotwins) VALUES ($1, $2, 0, '', 0)", str(ctx.author.id), str(ctx.author.name))
        user = await self.client.pg_con.fetchrow("SELECT * FROM users WHERE id = $1", str(ctx.author.id))
        try: 
            await ctx.send(f"{ctx.author.mention}, you have {int(user['slotwins'])} wins")
        except: 
            await ctx.send(f"{ctx.author.mention}, you don't have any wins! Hurry up and get some!")
                           
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def slots(self, ctx): 
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE id = $1", str(ctx.author.id))
        if not user: 
            await self.client.pg_con.execute("INSERT INTO users (id, name, coins, inventory, slotwins) VALUES ($1, $2, 0, '', 0)", str(ctx.author.id), str(ctx.author.name))
        user = await self.client.pg_con.fetchrow("SELECT * FROM users WHERE id = $1", str(ctx.author.id))
        if ctx.author.id == 4637593601:
            await ctx.send("Unblock Lime and stop being a bully to use this command!") 
            return
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
            if str(user['slotwins']) != "None": 
                await self.client.pg_con.execute("UPDATE users SET slotwins = $1 WHERE id=$2", str(int(user['slotwins'])+1), str(ctx.author.id))
            else:
                await self.client.pg_con.execute("UPDATE users SET slotwins = $1 WHERE id=$2", 1, str(ctx.author.id))
        await ctx.send(f"|   {fslots1}{fslots2}{fslots3}\n\▶{slots1}{slots2}{slots3}\n|   {fslots4}{fslots5}{fslots6}\n{win}")



def setup(client):
    client.add_cog(Slots(client))
