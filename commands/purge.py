import discord
from discord.ext import commands

class Purge(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int): 
        
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
                
    @purge.command()
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
    
    @purge.command()
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
        
    @purge.command()
    async def files(self, ctx, amount:int):
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        
        def hasImage(m):
                return len(m.attachments) > 0
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=hasImage)
    
    
    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def purgeban(self, ctx, amount:int): 
        
        await ctx.send('**USAGE:** ;purgeban [contains/match] [amount]')
                
    @purgeban.command()
    async def match(self, ctx, amount:int, *, text:str):
        ban_members = []
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        if text is None:
            await ctx.send('Enter type in the text you want to be deleted.')
            return
        
        def isText(m): 
            if m.content.lower() == text.lower():
                if m.author not in ban_members:
                    ban_members.append(m.author)
                return True
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=isText)
        for i in ban_members:
            await i.ban(reason=f"Banned from purgeban command, banning all members sending messages that matches {text}. Moderator: {ctx.author.name}")
    
    @purgeban.command()
    async def contains(self, ctx, amount:int, *, text:str):
    
        if amount is None:
            await ctx.send('Enter the amount of messages you wish to be deleted')
            return
        if text is None:
            await ctx.send('Enter type in the text you want to be deleted.')
            return
        
        def hasText(m): 
            if text.lower() in m.content.lower():
                if m.author not in ban_members:
                    ban_members.append(m.author)
                return True
        
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount, check=hasText)
        for i in ban_members:
            await i.ban(reason=f"Banned from purgeban command, banning all members sending messages containing {text}. Moderator: {ctx.author.name}")
        
        
def setup(client):
    client.add_cog(Purge(client))
