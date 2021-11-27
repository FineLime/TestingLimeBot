import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image
import requests
from io import BytesIO

class NewEmoji(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def newemoji(self, ctx, emojiname): 
        image = await ctx.message.attachments[0].read()
        newemote = await ctx.guild.create_custom_emoji(name=emojiname, image=image)
        await ctx.send(f"Created a new emoji! {str(newemote)}")
        
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def ripemoji(self, ctx, emoji:discord.PartialEmoji, name=None): 
        if not name: 
            name = emoji.name

        response = requests.get(emoji.url)
        img = BytesIO(response.content).read()

        newemote = await ctx.guild.create_custom_emoji(image=img, name=name)
        await ctx.send(f"Created a new emoji! {str(newemote)}")
        
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def lotsofemojis(self, ctx, *, emojis): 
        emojis = emojis.split(' ')
        msg = await ctx.send("Creating emojis, please wait...")
        for i in emojis: 
            try:
                i = await PartialEmojiConverter.convert(PartialEmojiConverter, ctx, i)
                response = requests.get(i.url)
                print(response)
                img = BytesIO(response.content).read()
                newemote = await ctx.guild.create_custom_emoji(image=img, name=i.name)
                await msg.edit(f"{msg.content} {newemote}")
                await asyncio.sleep(1.5)
            except: 
                await ctx.send(f"Something went wrong trying to steal {i}")
                continue
        await ctx.send("Created emojis")
        
def setup(client):
    client.add_cog(NewEmoji(client))
