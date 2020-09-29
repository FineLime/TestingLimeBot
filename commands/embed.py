import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Embed(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, p): 
        ps = p.split('=["')
        ce = ""
        t = ""
        title = "I didn't set a title!"
        description = "I didn't set a description!"
        image = ""
        footer = ""
        
        for i in range(len(ps)):
            if i == 0:
                ce = ps[1].split('"]')
                if ps[0].strip().lower() == 'title':
                    title = ce[0]
                elif ps[0].strip().lower() == 'description':
                    description = ce[0]
                elif ps[0].strip().lower() == 'image':
                    image = ce[0]
                elif ps[0].strip().lower() == 'footer':
                    footer = ce[0]
            elif i == len(ps)-1:
                break;
            else:
                ce = ps[i].split('"]')[1].strip().lower()
                t = ps[i+1].split('"]')[0].strip()
                if ce == 'title':
                    title = t
                elif ce == 'description':
                    description = t
                elif ce == 'image':
                    image = t
                elif ce == 'footer':
                    footer = t
                    
        embed = discord.Embed(title=title, description=description)
        if footer != "":
            embed.set_footer(text=footer)
        if image != "":
            embed.set_image(url=image)
                    
        await ctx.send(embed=embed)
                 
                    
            
                    
                
                

        
def setup(client):
    client.add_cog(Embed(client))
