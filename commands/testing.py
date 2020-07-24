import discord
from discord.ext import commands

class Purge(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def ppurge(self, ctx, amount:int): 
        
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
                
    @ppurge.command()
    async def match(self, ctx, amount:int, *, text:str):
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        if text is None:
            await ctx.send('Enter type in the text you want to be deleted.')
            return
        
        def isText(m): 
            return m.content.lower() == text.lower()
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=isText)
    
    @ppurge.command()
    async def contains(self, ctx, amount:int, *, text:str):
    
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        if text is None:
            await ctx.send('Enter type in the text you want to be deleted.')
            return
        
        def hasText(m): 
            return text.lower() in m.content.lower()
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=hasText)
        
    @ppurge.command()
    async def files(self, ctx, amount:int):
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        
        def hasImage(m):
                return len(m.attachments) > 0
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=hasImage)
        
    @ppurge.command()
    async def test(self, ctx, testing):
        await ctx.send(testing)
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ppurgeban(self, ctx, type, amount:int, *, text): 
        
        await ctx.message.delete()
        
        
def setup(client):
    client.add_cog(Purge(client))
