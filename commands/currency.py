import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import time
import asyncpg
import asyncio

class Currency(commands.Cog): 

    def __init__(self, client):
        self.client = client
       
    @commands.Cog.listener()
    async def on_message(self, message): 
        
        author = message.author
        if author.bot:
            return
        if message.content.startswith((";", '<@!458265636896768001> ', '<@458265636896768001> ')):
            return
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(message.guild.id), str(author.id))
        
        if len(user) == 0: 
            await self.client.pg_con.execute("INSERT INTO users (userid, serverid, coins, time) VALUES ($1, $2, $3, $4)", str(author.id), str(message.guild.id), 100, str(int(time.time())))
            return
            
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(message.guild.id), str(author.id))
        if user[0]["coins"] < 0:
            await self.client.pg_con.execute("UPDATE Users SET coins = 0 WHERE userid = $1 AND serverid = $2", str(author.id), str(message.guild.id))
        if (int(time.time()) - int(user[0]["time"])) > 60: 
            await self.client.pg_con.execute("UPDATE Users SET coins = $1, time = $2 WHERE userid = $3 AND serverid = $4", user[0]['coins']+random.randint(10, 25), str(int(time.time())), str(author.id), str(message.guild.id))
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def blackjack(self, ctx, bid:int):
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
        if bid < 500:
            await ctx.send("Minimum bid is 500")
            return
        if len(user) == 0:
            await ctx.send("You have no coins, get out of here")
            return
        if bid > user[0]['coins']: 
            await ctx.send("You're too poor to bid that much")
            return
        
        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id)) 
        
        def check(m): 
            return m.author == ctx.author and m.content.lower() in ["hit", "stand", "h", "s"]
       
        def get_card_value(list):
            v = 0
            a = 0
            for i in list:
                if i[0] in ["J", "Q", "K"] or i.startswith("10"): 
                    v += 10
                elif i[0] == "A":
                    a += 1
                else: 
                    v += int(i[0])
                    
            for i in range(0, a):
                if v + 11 > 21: 
                    v += 1
                else:
                    v += 11
            return v
            
        cards = ["A\♠", "2\♠", "3\♠", "4\♠", "5\♠", "6\♠", "7\♠", "8\♠", "9\♠", "10\♠", "J\♠", "Q\♠", "K\♠", "A\♥", "2\♥", "3\♥", "4\♥", "5\♥", "6\♥", "7\♥", "8\♥", "9\♥", "10\♥", "J\♥", "Q\♥", "K\♥", "A\♦", "2\♦", "3\♦", "4\♦", "5\♦", "6\♦", "7\♦", "8\♦", "9\♦", "10\♦", "J\♦", "Q\♦", "K\♦", "A\♣", "2\♣", "3\♣", "4\♣", "5\♣", "6\♣", "7\♣", "8\♣", "9\♣", "10\♣", "J\♣", "Q\♣", "K\♣"]
        dealers_cards = [random.choice(cards)]
        cards.remove(dealers_cards[0])
        dealers_cards.append(random.choice(cards))
        cards.remove(dealers_cards[1])
        dealers_total = get_card_value(dealers_cards)
        
        users_cards = [random.choice(cards)]
        cards.remove(users_cards[0])
        users_cards.append(random.choice(cards))
        cards.remove(users_cards[1])
        users_total = get_card_value(users_cards)
        
        message = "**DEALERS CARDS: **" 
        if dealers_total < 21: 
            message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
        else: 
            message += f"\n{dealers_cards[0]}  {dealers_cards[1]} (Total: 21)\n A natural BlackJack."
        
        message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**"
        
        message += f"\n{users_cards[0]} {users_cards[1]}  (Total: {users_total}){chr(10) + 'A natural BlackJack.' if users_total == 21 else ''}"
        
        if dealers_total == users_total == 21:  
            message += "\n\nTIE"
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id)) 
        elif dealers_total == 21:  
            message += "\n\nDealer Wins!"
            message += f"\nYou lost {bid} coins."
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
        elif users_total == 21:  
            message += "\n\nYou win!"
            message += f"\nYou won {int(bid*2.5-bid)} coins."
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", int(bid*2.5), str(ctx.guild.id), str(ctx.author.id)) 
        else: 
            message += "\n\nSend H to hit, S to stand"
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
            while True:
                
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                msg = msg.content.lower()
                if msg in ["s", "stand"]: 
                    break
                
                users_cards.append(random.choice(cards))
                users_total = get_card_value(users_cards)
                if users_total >= 21:
                    break
                       
                message = "**DEALERS CARDS: **" 
                message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**"          
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nSend H to hit, S to stand"
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed)
                
            if users_total > 21: 
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nBUST - Dealer Wins"
                message += f"\nYou lost {bid} coins."
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed)
                return
            
            while dealers_total < 17:
                dealers_cards.append(random.choice(cards))
                dealers_total = get_card_value(dealers_cards)
                
            if dealers_total > 21: 
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nBUST - You Win"
                if users_total == 21:
                    message += f"\nYou won {int(bid*2.5-bid)} coins."
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", int(bid*2.5), str(ctx.guild.id), str(ctx.author.id)) 
                else:
                    message += f"\nYou won {bid*2-bid} coins."
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", bid*2, str(ctx.guild.id), str(ctx.author.id))
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed) 
                return
            
            if dealers_total > users_total:
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nDealer Wins"
                message += f"\nYou lost {bid} coins."
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed)
                return
                
            if users_total > dealers_total:
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nYou Win"
                if users_total == 21:
                    message += f"\nYou won {int(bid*2.5-bid)} coins."
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", int(bid*2.5), str(ctx.guild.id), str(ctx.author.id)) 
                else:
                    message += f"\nYou won {bid*2-bid} coins."
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", bid*2, str(ctx.guild.id), str(ctx.author.id)) 
 
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed)
                return
                
            
            message = "**DEALERS CARDS: **" 
            message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
            message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
            message += "\n\nTIE"
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id)) 
            
            
    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, asyncio.TimeoutError):
            await ctx(f"{ctx.author.mention} ran away from the blackjack table but forgot to take his coins.\nI guess they're mine now.")
            
    @commands.command(aliases=["flip", "coin", "flipcoin"])
    @commands.cooldown(1, 10, BucketType.user)
    async def coinflip(self, ctx, guess, bid:int): 
        guess = guess.lower()
        if bid < 500:
            await ctx.send("Minimum bid for coinflipping is 500, this aint a children's game.")
            return
        if guess.lower() not in ["heads", "tails"]:
            await ctx.send("Have you have seen a coin before? It has a heads and a tails. Guess what it will land on.")
            return
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))              
        if user[0]["coins"] < bid:
            await ctx.send("You're too poor to bid that much.")
            return
        
        result = random.choice(["heads", "tails"])
        msg = f"I flipped a coin and it landed on {result}."
        if result != guess: 
            await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", bid, str(ctx.author.id), str(ctx.guild.id))
            msg+= "\nLooks like I'll be keeping your money, and don't you go crying to me about it."
        else:
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", bid, str(ctx.author.id), str(ctx.guild.id))
            msg += f"\nHuh, you won, well here you go, take my {bid} coins."
        await ctx.send(msg)
            
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def coins(self, ctx, u:discord.User = None):
        if not u: 
            u = ctx.author
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(u.id))
        if len(user) == 0: 
            await ctx.send(f"{u.name} has 0 coins.")
            return
        if u == ctx.author:
            await ctx.send(f"{u.mention}, you have {user[0]['coins']} coin(s)")
        else: 
            await ctx.send(f"{u.name} has {user[0]['coins']} coin(s)")               
                           
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def gift(self, ctx, u:discord.User, gift:int):
        if u == ctx.author:
            await ctx.send("You want to send coins to yourself? Are you braindead or something.")
            return               
        if gift < 0: 
            await ctx.send("Are you trying to rob from them? Feel free to suggest a rob command if you want it.")
            return               
        if gift == 0:
            await ctx.send("Transaction complete! I didn't actually do anything, but I did it!")
            return
        
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(u.id))
        author = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id))
        if len(author) == 0:
            await ctx.send("You don't have any coins, get out of here.")
            return
        
        if author[0]["coins"] < gift:
            await ctx.send("You're too poor to gift that much.")
            return
                           
        if len(user) == 0: 
            await ctx.send(f"{u.name} doesn't seem to be in my database, tell them to send a message in the chat (non-command).")
            return
        
        await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid=$2 AND userid=$3", gift, str(ctx.guild.id), user[0]["userid"])
        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid=$2 AND userid=$3", gift, str(ctx.guild.id), author[0]["userid"])
        await ctx.send(f"You successfully gifted {gift} coins.")
                           
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def richest(self, ctx):
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1ORDER BY coins DESC LIMIT 5", str(ctx.guild.id))
        msg = ""    
        for u in range(0, len(user)):
            msg += f"{u+1}. <@!{user[u]['userid']}> - {user[u]['coins']}\n"            
        embed = discord.Embed(title=f"Richest in Server", description=msg, color=0x00ff00)
                       
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def slots(self, ctx, bet:int=0): 
        
        
        if bet > 0 and bet < 50:
            await ctx.send("Minimum bid is 50")
            return
                       
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))              
        if user[0]["coins"] < bet:
            await ctx.send("You're too poor to bid that much.")
            return
               
                       
                       
        choices1 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]
        choices2 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]
        choices3 = [":seven:", ":cherries:", ":moneybag:", ":gem:", ":game_die:", ":tada:", ":o:", ":large_orange_diamond:"]

        slots1 = random.choice(choices1)
        slots2 = random.choice(choices2)
        slots3 = random.choice(choices3)

        choices1.remove(slots1)
        choices2.remove(slots2)
        choices3.remove(slots3)

        fslots1 = random.choice(choices1)
        fslots2 = random.choice(choices2)
        fslots3 = random.choice(choices3)

        choices1.remove(fslots1)
        choices2.remove(fslots2)
        choices3.remove(fslots3)

        fslots4 = random.choice(choices1)
        fslots5 = random.choice(choices2)
        fslots6 = random.choice(choices3)

        win = "Sorry, you lost!"
        if slots1 == slots2 == slots3: 
            if bet == 0:
                win = "Winner!!!\nBut since you're a pepega and didn't bid, you get nothing."
            else:
                await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", bet*75, str(ctx.author.id), str(ctx.guild.id))
                win = f"Winner!!!\nYou won yourself {bet*75} coins!"
        elif bet > 0:
            await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", bet, str(ctx.author.id), str(ctx.guild.id))
            win += f"\nYou lost {bet} coins."
        await ctx.send(f"|   {fslots1}{fslots2}{fslots3}\n\▶{slots1}{slots2}{slots3}\n|   {fslots4}{fslots5}{fslots6}\n{win}")



def setup(client):
    client.add_cog(Currency(client))
