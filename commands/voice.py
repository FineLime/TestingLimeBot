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

		voice_channel = ctx.author.voice.channel
		vc = await voice_channel.connect()
		print(vc)
		player = await self.client.yt_play.from_url(f"https://www.youtube.com/watch?v={video_id}", loop=self.client.loop, stream=True)
		ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)


        
def setup(client):
    client.add_cog(Voice(client))
