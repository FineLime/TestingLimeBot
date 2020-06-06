import discord
from discord.ext import commands

class Purge(commands.Cog): 

    def __init__(self, client):
        self.client = client
        
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, ptype, amount=0, *, text="d3fault m3ssag3 jd93d0w993r"): 
        
        await ctx.message.delete()
        try:
            ptype = int(ptype)
        except:
            ptype = ptype.lower()
        text = text.lower()
        if ptype == 'match':
            def isText(m): 
                
                return m.content.lower() == text
       
            await ctx.channel.purge(limit=amount, check=isText)
        
        elif ptype == 'contains':
            
            def hasText(m): 
                return text in m.content.lower()
            
            await ctx.channel.purge(limit=amount, check=hasText)
        
        elif ptype == 'images':
            
            def hasImage(m):
                return len(m.attachments) > 0
            
            await ctx.channel.purge(limit=amount, check=hasImage)
            
        elif type(ptype) == int and amount == 0:
            
            await ctx.channel.purge(limit=ptype)
            
        
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def purgeban(self, ctx, type, amount:int, *, text): 
        
        await ctx.message.delete()
        type = type.lower()
        text = text.lower()
        ban_users = []
        if type == 'match':
            
            def banText(m): 
                if m.content.lower() == text: 
                    if m.author not in ban_users:
                        ban_users.append(m.author)
                    return True
            await ctx.channel.purge(limit=amount, check=banText)
            
        elif type == 'contain':
            
            def banContains(m): 
                if text in m.content.lower: 
                    if m.author not in ban_users:
                        ban_users.append(m.author)
                    return True
                
            await ctx.channel.purge(limit=amount, check=banContains)
            
            
        for i in ban_users:
            await i.ban(reason=f"Banned from prurge command. Moderator: {ctx.author.name}")
        
def setup(client):
    client.add_cog(Purge(client))
