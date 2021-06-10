import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import ffmpeg
import os
import asyncio

class FFmpeg(commands.Cog): 

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 10, BucketType.user)
	async def optimize(self, ctx): 
		
		try: 
			file = ctx.message.attachments[0].url 
		except:
			print("no file")
			return
		
		if not file.endswith((".avi", ".mp4", ".webm", ".mov")): 
			print("REEE")
			return
		
		filename = f'{ctx.message.attachments[0].filename.split(".")[0]}_{random.randint(100, 1000)}_optimized'
		
		async with ctx.channel.typing()
			process = (
			ffmpeg
			.input("http://cdn.discordapp.com/attachments/481802328702189569/852674636219023420/4efgwu78a0s51.mp4")
			.output(discord.File(filename), format='mp4', vcodec="libx264", crf="28")
			.run_async()
			)
			asyncio.sleep(10)
			await ctx.send(file=filename)
			os.remove(filename)

        
def setup(client):
    client.add_cog(FFmpeg(client))
