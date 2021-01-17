import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Voice(commands.Cog): 

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 10, BucketType.user)
	async def play(self, ctx, *, s): 
		request = self.client.youtube.search().list(
			maxResults=1,
			q=s,
			part="snippet"
		)
		response = request.execute()
		video_id = response['items'][0]['id']['videoId']

		async with ctx.typing():
			player = await self.client.yt_play.from_url(f"https://www.youtube.com/watch?v={video_id}", loop=self.client.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
		await ctx.send("Playing")
		
	@play.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel.")
				raise commands.CommandError("Author not connected to a voice channel.")
		elif ctx.voice_client.is_playing():
			ctx.voice_client.stop()


        
def setup(client):
    client.add_cog(Voice(client))
