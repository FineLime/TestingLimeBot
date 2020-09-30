import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Poll(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, poll): 
        #Poll format: ;poll Should x be allowed to join? | :Zero:=Yes / :One:=No /
        poll = poll.split(" | ")
        title = poll[0]
        pollmessage = ""
        poll = poll[1].split(" / ")
        reactions = []
        for i in poll: 
            a = i.split("=")
            pollmessage += f"\n{a[0].strip()} {a[1].strip()}"
            reactions.append(f"{a[0].strip()}")
            
        embed = discord.Embed(title=title, description=pollmessage)
        reactto = await ctx.send(embed=embed)
        for i in reactions:
            await reactto.add_reaction(i)
        
def setup(client):
    client.add_cog(Poll(client))
