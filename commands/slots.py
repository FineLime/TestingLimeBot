import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random

class Slots(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    '''                       
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

        '''

def setup(client):
    client.add_cog(Slots(client))
