import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import re

class CustomCommands(commands.Cog): 

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_message(self, message): 
        
        if message.author.bot:
            return
            
        name = message.content.split(" ")[0].lower()
        cmd = await self.client.pg_con.fetch('''SELECT * FROM customcommands WHERE commandname = $1 AND serverid = $2''', name, str(message.guild.id))
        if len(cmd) == 0: 
            return 
         
        params = message.content.split(" ")
        response = cmd[0]['response']
        response = response.replace("{user}", message.author.mention)
        try:
            response = response.replace("{$1}", params[1])
        except:
            pass
        try:
            response = response.replace("{$2}", params[2])
        except:
            pass
            
        while True:
            
            rchoice = re.search(r'''{r\.choice\[("[a-zA-Z0-9.,_=+()£$!?' -]+",( |))+"[a-zA-Z0-9.,_=+()£$!?' -]+"\]}''', response)
            if not rchoice:
                break
                
            choices = response[rchoice.start():rchoice.end()]
            choices = choices[10:-3]
            choices = choices.split('",')
            choice = random.choice(choices).strip()[1:]
            response = response[0:rchoice.start()] + choice + response[rchoice.end():]
            
        while True:
            
            ifs = re.search(r'''{if {\$[1-9]} == [a-zA-Z0-9!?,.@';#~+=_$%^&()" -]+:[a-zA-Z0-9!?,.@';#~+=_$%^&()" -]+}''', response)
            if not ifs:
                break
                
            ifs = response[rchoice.start():rchoice.end()]
            ifs = ifs[4:-1]
            ifs = ifs.split(' == ')
            check1 = ifs[0]
            ifs = ifs[1].split(":")
            check2 = ifs[0]
            response = ifs[1]
            print(check1)
            print(check2)
            print(check1 == check2)
            print(response)
            if check1.lower() == check2.lower():
                response = response[0:rchoice.start()] + response + response[rchoice.end():]
            else: 
                response = response[0:rchoice.start()] + response[rchoice.end():]
                
            #response = f'Check 1: {check1} \nCheck2: {check2} \nCheckTrueOrFalse: {check1.lower() == check2.lower()} \nResponse:{response}'
            
            
        await message.channel.send(response)
         
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def createcommand(self, ctx, name, perms, *, response):
        
        if perms not in ["everyone", "admin"]: 
            await ctx.send("Perms must either be `everyone` or `admin`")
            return
        
        await self.client.pg_con.execute('''INSERT INTO customcommands (commandname, response, perms, serverid) VALUES ($1, $2, $3, $4)''', name, response, perms, str(ctx.guild.id))
        await ctx.send("Command created")

        
def setup(client):
    client.add_cog(CustomCommands(client))
