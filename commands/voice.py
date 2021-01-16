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
        video_id = r['items'][0]['id']['videoId']
        
        voice_channel = author.voice_channel
        vc = await client.join_voice_channel(voice_channel)
        print(vc)
        player = await vc.create_ytdl_player(f"https://www.youtube.com/watch?v={video_id}")
        player.start()

        
def setup(client):
    client.add_cog(Ping(client))
