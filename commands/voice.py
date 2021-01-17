import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Voice(commands.Cog): 

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 10, BucketType.user)
	async def play(self, ctx, *, s): 
		
		async def next_song(): 
			
			await ctx.voice_client.stop()
			s = await self.client.pg_con.fetch("SELECT * FROM queue WHERE serverid = $1 AND qposition = 1", str(ctx.guild.id))
			if len(s) == 0:
				return

			request = self.client.youtube.search().list(
				maxResults=1,
				q=s,
				part="snippet"
			)
			await self.client.pg_con.execute("DELETE FROM queue WHERE serverid = $1 AND qposition = 1", str(ctx.guild.id))
			await self.client.pg_con.execute("UPDATE queue SET qposition = qposition - 1 WHERE serverid = $1", str(ctx.guild.id))
			response = request.execute()
			video_id = response['items'][0]['id']['videoId']
			async with ctx.typing():
				player = await self.client.yt_play.from_url(f"https://www.youtube.com/watch?v={video_id}", loop=self.client.loop, stream=True)
				ctx.voice_client.play(player, after=await next_song())
			await ctx.send("Playing")
		
		request = self.client.youtube.search().list(
			maxResults=1,
			q=s,
			part="snippet"
		)
		response = request.execute()
		video_id = response['items'][0]['id']['videoId']
		
		if ctx.voice_client.is_playing() == False:
			async with ctx.typing():
				player = await self.client.yt_play.from_url(f"https://www.youtube.com/watch?v={video_id}", loop=self.client.loop, stream=True)
				ctx.voice_client.play(player, after=await next_song())
			await ctx.send("Playing")
		else:
			queue = await self.client.pg_con.fetch("SELECT * FROM queue WHERE serverid = $1 ORDER BY qposition", str(ctx.guild.id))
			await self.client.pg_con.execute("INSERT INTO queue (serverid, userid, squery, qposition) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), str(ctx.author.id), s, len(queue)+1)
			await ctx.send("Added to queue")
			
	@play.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel.")
				raise commands.CommandError("Author not connected to a voice channel.")


        
def setup(client):
    client.add_cog(Voice(client))
