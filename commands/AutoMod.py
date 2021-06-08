import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class AutoMod(commands.Cog): 

	def __init__(self, client):
		self.client = client
		
	@commands.Cog.listener()
	async def on_member_join(self, member): 
		if "twitter.com/h0nde" in member.name.lower(): 
			try:
				await member.ban(reason="spam account") 
			except: 
				pass

        
def setup(client):
    client.add_cog(AutoMod(client))
