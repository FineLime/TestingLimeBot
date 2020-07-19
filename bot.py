import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import random 
import asyncpg

MyDB = os.getenv('DATABASE_URL')
DB = MyDB.split(":")
user = DB[1][2:]
password = DB[2].split("@")[0]
host = DB[2].split("@")[1]
port = DB[3].split("/")[0]
database = DB[3].split("/")[1]

client = commands.Bot(command_prefix=";", case_insensitive=True)
client.remove_command("help")

status = "for commands"

@client.event
async def on_ready():
    print("The bot is ready")
    await client.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))

async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database=database, user=user, password=password, host=host, port=port, ssl="require")

    
@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == 432176723279216640 and payload.message_id == 439327580609445898: 
        server = get(client.guilds, id=payload.guild_id)
        user = get(server.members, id=payload.user_id)
        getRole = get(server.roles, id=role[emotes.index(str(payload.emoji.name)[:1])])
        await user.add_roles(getRole)
        
@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == 432176723279216640 and payload.message_id == 439327580609445898: 
        server = get(client.guilds, id=payload.guild_id)
        user = get(server.members, id=payload.user_id)
        getRole = get(server.roles, id=role[emotes.index(str(payload.emoji.name)[:1])])
        await user.remove_roles(getRole)

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
