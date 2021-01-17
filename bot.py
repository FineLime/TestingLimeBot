import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import random 
import asyncpg
from googleapiclient.discovery import build
import youtube_dl

MyDB = os.getenv('DATABASE_URL')
DB = MyDB.split(":")
user = DB[1][2:]
password = DB[2].split("@")[0]
host = DB[2].split("@")[1]
port = DB[3].split("/")[0]
database = DB[3].split("/")[1]


async def prefix(bot, message):
    
    return [';', '<@!458265636896768001> ', '<@458265636896768001> ']



intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
client.remove_command("help")


api_key = os.getenv('google_key')
client.youtube = build('youtube', 'v3', developerKey=api_key)


status = "for ;help commands"

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
client.yt_play = YTDLSource

@client.event
async def on_ready():
    print("The bot is ready")
    await client.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))

async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database=database, user=user, password=password, host=host, port=port, ssl="require")

@client.command()
async def help(ctx):
    await ctx.send("Find the list of commands at https://finelime.github.io/docs")
    
@client.event
async def on_guild_remove(guild):
    await client.pg_con.execute("DELETE FROM servers WHERE serverid = $1", str(guild.id))
    await client.pg_con.execute("DELETE FROM autorole WHERE server = $1", str(guild.id))
    await client.pg_con.execute("DELETE FROM reactionroles WHERE serverid = $1", str(guild.id))
    await client.pg_con.execute("DELETE FROM mutes WHERE serverid = $1", str(guild.id))
    
@client.command()
@commands.is_owner()
async def load(ctx, extenstion):
    client.load_extension(f'commands.{extenstion}')

@client.command()
@commands.is_owner()
async def unload(ctx, extenstion):
    client.unload_extension(f'commands.{extenstion}')

@client.command()
@commands.is_owner()
async def reload(ctx, extenstion):
    client.unload_extension(f'commands.{extenstion}')
    client.load_extension(f'commands.{extenstion}')

for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        client.load_extension(f'commands.{filename[:-3]}')

    
client.loop.run_until_complete(create_db_pool())  
client.run(os.getenv('TOKEN'))
