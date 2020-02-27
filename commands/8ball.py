import discord
from discord.ext import commands
import random
from discord.ext.commands.cooldowns import BucketType

choices = ["Yes.", "Possibly", "Most likely.", "It is most certain.", "Signs point to yes", "Positive.", "Of course.", "No.", "It is unlikely.", "Chances are slim.", "That is impossible.", "Don't bet on it.", "Negative.", "Concentrate harder and ask again.", "I am unsure.", "The gods have not given me an answer."]

class _8ball(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["8ball"])
    @commands.cooldown(1, 10, BucketType.user)
    async def _8ball(self, ctx, *, question): 
        await ctx.send(f'**Question**: {discord.utils.escape_markdown(discord.utils.escape_mentions(question))} \n**Answer**: {random.choice(choices)}')
    
    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("**Usage:** ;8ball [Question]")
        else:
            await ctx.send("**Unknown error while running this command, Please contact Lime#6045. \nHow on earth do you break 8ball?")
    
def setup(client):
    client.add_cog(_8ball(client))
