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
        ban_users = []
        if type == 'match':
            def isText(m): 
                
                return m.content.lower() == text
       
            await ctx.channel.purge(limit=amount, check=isText)
        
        elif type == 'contains':
            
            def hasText(m): 
                return text in m.content.lower()
            
            await ctx.channel.purge(limit=amount, check=hasText)
            
        elif type == 'banmatch':
            
            def banText(m): 
                if m.content.lower() == text: 
                    if m.author not in ban_users:
                        ban_users.append(m.author)
                    return True
            await ctx.channel.purge(limit=amount, check=banText)
            
        elif type == 'bancontain':
            
            def banContains(m): 
                if text in m.content.lower: 
                    if m.author not in ban_users:
                        ban_users.append(m.author)
                    return True
                
            await ctx.channel.purge(limit=amount, check=banContains)
        
def setup(client):
    client.add_cog(Purge(client))
