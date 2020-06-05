import discord
from discord.ext import commands

class Purge(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=1): 
        await ctx.channel.purge(limit=amount)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purgebanana(self, ctx, type, amount:int, *, text): 
        
        await ctx.message.delete()
        type = type.lower()
        text = text.lower()
        if type == 'match':
            def isText(m): 
                return m.content.lower() == text
       
            await ctx.channel.purge(limit=amount, check=isText)
        
        elif type == 'contains':
            def hasText(m): 
                return text in m.content.lower()
            
            await ctx.channel.purge(limit=amount, check=hasText)
            
        elif type == 'banmatch':
            async def banText(m): 
                if m.content.lower() == text: 
                    try:
                        await m.author.ban()
                    except:
                        pass
                    return True
            await ctx.channel.purge(limit=amount, check=banText)
            
        elif type == 'bancontain':
            async def banContains(m): 
                if text in m.content.lower: 
                    try:
                        m.author.ban()
                    except:
                        pass
                    return True
            await ctx.channel.purge(limit=amount, check=banContains)
        
def setup(client):
    client.add_cog(Purge(client))
