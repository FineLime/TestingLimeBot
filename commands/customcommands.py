import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

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
            
        await message.channel.send(response)
         
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def createcommand(self, ctx, name, perms, *, response):
        
        if perms not in ["everyone", "admin"]: 
            await ctx.send("Perms must either `everyone` or `admin`"]
            return
        
        await self.client.pg_con.execute('''INSERT INTO customcommands (commandname, response, perms, serverid) VALUES ($1, $2, $3, $4)''', name, response, perms, str(ctx.guild.id))
        await ctx.send("Command created")

        
def setup(client):
    client.add_cog(CustomCommands(client))
