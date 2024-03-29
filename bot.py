import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import random 
import asyncpg
import requests
import json

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


status = "anime"

client.crypto = {}
crypto = json.loads(requests.get("https://api.binance.com/api/v3/ticker/24hr").content)
for index, i in enumerate(crypto): 
    if i['symbol'].endswith(("BUSD", "USDT", "USDC")) and i['symbol'][:-4] not in client.crypto: 
        client.crypto[i['symbol'][:-4]] = i
        client.crypto[i['symbol'][:-4]]['id'] = index


@client.event
async def on_ready():
    print("The bot is ready")
    await client.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))

async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database=database, user=user, password=password, host=host, port=port, ssl="require")

@client.command()
async def help(ctx):
    await ctx.send("Soon")
    
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
