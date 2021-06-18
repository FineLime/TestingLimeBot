import discord
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter
from discord.ext.commands.cooldowns import BucketType
import random
import math
import time
import asyncpg
import asyncio
import time

class Currency(commands.Cog): 
    
    #i regret this
    #but i love you
    def __init__(self, client):
        self.client = client
        self.next_lottery = time.time() 
        asyncio.sleep(10)
        self.get_winners.start()
    
            
    @commands.Cog.listener()
    async def on_message(self, message): 
        
        author = message.author
        if author.bot:
            return
        elif message.content.startswith((";", '<@!458265636896768001> ', '<@458265636896768001> ')):
            return
        elif message.content.lower in ["hit", "h", "s", "stand"]:
            return
        
        else:
            user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(message.guild.id), str(author.id))
        
            if len(user) == 0: 
                await self.client.pg_con.execute("INSERT INTO users (userid, serverid, coins, time) VALUES ($1, $2, $3, $4)", str(author.id), str(message.guild.id), 100, str(int(time.time())))
                return
            
            user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(message.guild.id), str(author.id))
            if user[0]["coins"] < 0:
                await self.client.pg_con.execute("UPDATE Users SET coins = 0 WHERE userid = $1 AND serverid = $2", str(author.id), str(message.guild.id))
            if (int(time.time()) - int(user[0]["time"])) > 60: 
                await self.client.pg_con.execute("UPDATE Users SET coins = coins + $1, time = $2 WHERE userid = $3 AND serverid = $4", random.randint(10, 25), str(int(time.time())), str(author.id), str(message.guild.id))
    
    @commands.command()
    @commands.is_owner()
    async def give(self, ctx, user:discord.User, coins:int):
        await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", coins, str(user.id), str(ctx.guild.id))
        await ctx.send("Done")
        
    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 10, BucketType.user)
    async def lottery(self, ctx):
        await ctx.send("type `;lottery buy` to buy a ticket")
    
    @lottery.command()
    async def pot(self, ctx):
        tickets = await self.client.pg_con.fetch("SELECT * FROM tickets")
        pot = len(tickets)*100
        await ctx.send(f"Current lottery pot is: {pot}")
        
    @lottery.command()
    async def buy(self, ctx):
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id))
        if len(user) == 0:
            await ctx.send("You don't have any coins.")
            return
        if user[0]['coins'] < 100:
            await ctx.send("You don't have enough for a lottery ticket")
            return
        await self.client.pg_con.execute("UPDATE users SET coins = coins - 100 WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))
        await self.client.pg_con.execute("INSERT INTO tickets (userid, serverid) VALUES ($1, $2)", str(ctx.author.id), str(ctx.guild.id))
        await ctx.send("You bought a lottery ticket for 100")
        
    @lottery.command()
    async def tickets(self, ctx):
        tickets = await self.client.pg_con.fetch("SELECT * FROM tickets WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id))
        await ctx.send(f"{ctx.author.mention}, you have {len(tickets)} tickets.")
    
    @lottery.command()
    async def next(self, ctx):
        time_now = time.time()
        next_l = self.next_lottery - time_now
        time_left = ''
        if next_l < 60:
            time_left = f'{next_l:9.2f} seconds left until lottery is drawn.'
        else:
            time_left = next_l/60
            time_left = f'{math.ceil(next_l/60)} minutes left until lottery is drawn.'
        await ctx.send(time_left)
        
        
    @tasks.loop(seconds=1800)
    async def get_winners(self):
        try:
            tickets = await self.client.pg_con.fetch("SELECT * FROM tickets")
            if len(tickets) == 0:
                return
            winner = random.choice(tickets)
            coins = len(tickets)*100 
            try:
                class fakectx():
                    def __init__(self, bot, guild):
                        self.bot = bot
                        self.guild = guild
                    
                guild = discord.utils.get(self.client.guilds, id=int(winner['serverid']))
                fake = fakectx(self.client, guild)
                user = await MemberConverter().convert(fake, winner["userid"])
                await user.send(f"You won the lottery in {discord.utils.get(self.client.guilds, id=int(winner['serverid']))}!")
            except Exception as e:
                print(e)
            print(f'{winner["userid"]} WON - ADDED THIS SO IT IS MORE VISIBLE IN LOGS!\nADDED THIS SO IT IS MORE VISIBLE WINNER WINNER WINNER')
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", coins, winner['userid'], winner['serverid'])
            await self.client.pg_con.execute("DELETE FROM tickets")
        except Exception as e: 
            print(e)
        self.next_lottery += 30*60
              
            
            
        
                
    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def blackjack(self, ctx, bid:int = 0):
        
        first_run = True
        double_down = False
        split_cards = False
        bid2 = bid
        outcome = 0
        current = 1
        natural = [False, False]
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
        if bid < 250 and bid != 0:
            await ctx.send("Minimum bid is 250")
            return
        if len(user) == 0:
            await ctx.send("You have no coins, get out of here")
            return
        if bid > user[0]['coins']: 
            await ctx.send("You're too poor to bid that much")
            return
        
        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id)) 
        
        def check(m): 
            if ctx.author != m.author:
                  return False
            if first_run:
                if m.content.lower() in ["hit", "stand", "h", "s"]: 
                    return True
                elif m.content.lower() in ["d"]:
                    return True
                elif m.content.lower() in ["split"] and split_cards == False:
                    return True
                else:
                    return False
            return m.content.lower() in ["hit", "stand", "h", "s"]
       
        def get_card_value(list):
            v = 0
            a = 0
            a2 = 0
            for i in list:
                if i[0] in ["J", "Q", "K"] or i.startswith("10"): 
                    v += 10
                elif i[0] == "A":
                    a += 1
                    a2 += 1
                else: 
                    v += int(i[0])
                    
            for i in range(0, a):
                if v + 11 + a2-1 > 21:  
                    v += 1
                    a2 -= 1
                else:
                    v += 11
                    a2 -= 1
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
        
        users_cards2 = []
        users_total2 = 0
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
            message += "\n\nSend H to hit, S to stand, D to double down"
            if users_cards[0][:-2] == users_cards[1][:-2]: 
                  message += ", Split to Split"
            embed = discord.Embed(title="BlackJack", description=message)
            await ctx.send(embed=embed)
            while True:
                
                try:
                    msg = await self.client.wait_for('message', timeout=60.0, check=check)
                except Exception as e:
                    print(e)
                    await ctx.send(f"{ctx.author.mention} ran away from the blackjack table but forgot to take their coins.\nI guess they're mine now.")
                    return
                
                first_run = False
                msg = msg.content.lower()
                if split_cards: 
                    if msg in ["s", "stand"]: 
                        if current == 1:
                            if natural[1]:
                                break
                            message = "**DEALERS CARDS: **" 
                            message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                            message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"          
                            message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                            message += "\n\nSend H to hit, S to stand, D to Double Down"
                            embed = discord.Embed(title="BlackJack", description=message)
                            await ctx.send(embed=embed)
                            current = 2
                            first_run = True
                            continue
                        else:
                            break
                    if msg in ["d"]:
                        check_coins = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
                        check_bid = bid if current == 1 else bid2
                        if check_bid > check_coins[0]['coins']:
                            await ctx.send("You do not have enough money to double down")
                            continue
                        else:
                            await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id))
                            if current == 1:
                                bid *= 2
                                users_cards.append(random.choice(cards))
                                cards.remove(users_cards[-1])
                                users_total = get_card_value(users_cards)
                                if natural[1]:
                                    break
                                message = "**DEALERS CARDS: **" 
                                message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"          
                                message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                                message += "\n\nSend H to hit, S to stand, D to Double Down"
                                embed = discord.Embed(title="BlackJack", description=message)
                                await ctx.send(embed=embed)
                                continue
                            else:
                                bid2 *= 2
                                users_cards2.append(random.choice(cards))
                                cards.remove(users_cards2[-1])
                                users_total2 = get_card_value(users_cards2)
                                break
                                    
                    if msg in ["h", "hit"]:
                        if current == 1:
                            users_cards.append(random.choice(cards))
                            cards.remove(users_cards[-1])
                            users_total = get_card_value(users_cards)
                            if users_total >= 21:
                                if natural[1]:
                                    break
                                current = 2
                                first_run = True
                                message = "**DEALERS CARDS: **" 
                                message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"          
                                message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                                message += "\n\nSend H to hit, S to stand, D to Double Down"
                                embed = discord.Embed(title="BlackJack", description=message)
                                await ctx.send(embed=embed)
                                continue
                            message = "**DEALERS CARDS: **" 
                            message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                            message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                            message += "\n\nSend H to hit, S to stand"
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"          
                            message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                            embed = discord.Embed(title="BlackJack", description=message)
                            await ctx.send(embed=embed)
                            continue
                        else: 
                            users_cards2.append(random.choice(cards))
                            cards.remove(users_cards2[-1])
                            users_total2 = get_card_value(users_cards2)
                            if users_total2 >= 21:
                                break
                            message = "**DEALERS CARDS: **" 
                            message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                            message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                            message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"          
                            message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                            message += "\n\nSend H to hit, S to stand"
                            embed = discord.Embed(title="BlackJack", description=message)
                            await ctx.send(embed=embed)
                            continue
                            
                                    
                                
                
                if msg in ["s", "stand"]: 
                    break
            
                if msg in ["d"]: 
                    check_coins = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
                    if bid > check_coins[0]['coins']:
                        await ctx.send("You do not have enough money to double down")
                        continue
                    else:
                        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id))
                        bid *= 2
                        users_cards.append(random.choice(cards))
                        cards.remove(users_cards[-1])
                        users_total = get_card_value(users_cards)
                        break
                 
                if msg == "split":
                    check_coins = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1 AND userid=$2", str(ctx.guild.id), str(ctx.author.id)) 
                    if bid > check_coins[0]['coins']:
                        await ctx.send("You do not have enough money to double down")
                        continue
                    else: 
                        await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE serverid = $2 AND userid = $3", bid, str(ctx.guild.id), str(ctx.author.id))
                        
                        users_cards2.append(users_cards[1])
                        users_cards.pop()
                        users_cards.append(random.choice(cards))
                        cards.remove(users_cards[-1])
                        users_cards2.append(random.choice(cards))
                        cards.remove(users_cards2[-1])
                        users_total = get_card_value(users_cards)
                        users_total2 = get_card_value(users_cards2)
                        if users_total == 21:
                            natural[0] = True
                        if users_total2 == 21:
                            natural[1] == True
                        if natural[0] and natural[1]:
                            break
                        split_cards = True
                        message = "**DEALERS CARDS: **" 
                        message += f"\n{dealers_cards[0]}  🂠 (Total: ?)" 
                        message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**"          
                        message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                        if natural[0]:
                            message += "\n\nA natural BlackJack"
                            current = 2
                        else:
                            message += "\n\nSend H to hit, S to stand, D to double down"
                        
                        message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**"  
                        message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})"
                        if natural[1]: 
                            message += "\n\nA natural BlackJack"
                        elif natural[0]: 
                            message += "\n\nSend H to hit, S to stand, D to double down"
                        
                        embed = discord.Embed(title="BlackJack", description=message)
                        await ctx.send(embed=embed)
                        continue
                  
                users_cards.append(random.choice(cards))
                cards.remove(users_cards[-1])
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
            
                  
            if users_total > 21 and split_cards == False: 
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
                cards.remove(dealers_cards[-1])
                dealers_total = get_card_value(dealers_cards)
            
            if split_cards:
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 1:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})\n"
                if natural[0]: 
                    message+="A natural blackjack!"
                    outcome += int(bid*1.5)
                elif users_total > 21:
                    message+="YOU WENT BUST"
                    outcome -= bid
                elif users_total > dealers_total: 
                    message+="WON"
                    if users_total == 21:
                        outcome += int(bid/2)
                    outcome += bid
                elif dealers_total <= 21:
                    message += "LOST"
                    outcome -= bid
                elif users_total == dealers_total:
                    message += "TIE"
                else:
                    if users_total == 21:
                        outcome += int(bid/2)
                    message += "DEALER WENT BUST"
                    outcome += bid
                 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS 2:**" 
                message += f"\n{'  '.join(users_cards2)} (Total: {users_total2})\n"
                
                if natural[1]: 
                    message+="A natural blackjack!"
                    outcome += int(bid2*1.5)
                elif users_total2 > 21:
                    message+="BUST"
                    outcome -= bid2
                elif users_total2 > dealers_total: 
                    message+="WON"
                    if users_total == 21:
                        outcome += int(bid2/2)
                    outcome += bid2
                elif dealers_total <= 21:
                    message += "LOST"
                    outcome -= bid2
                elif users_total2 == dealers_total:
                    message += "TIE"
                else:
                    message += "DEALER WENT BUST"
                    outcome += bid2
                  
                message+="\n\n"
                if outcome == 0:
                    if bid == 0:
                        message+="You earned nothing."
                elif outcome > 0:
                    message+=f"You earned {outcome}."
                else:
                    message+=f"You lost {abs(outcome)}."
                
                if bid == 0:
                    outcome += bid
                    outcome += bid2
                    await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE serverid = $2 AND userid = $3", outcome, str(ctx.guild.id), str(ctx.author.id))
                embed = discord.Embed(title="BlackJack", description=message)
                await ctx.send(embed=embed) 
                return
                
                    
                  
               
                        
            if dealers_total > 21: 
                message = "**DEALERS CARDS: **" 
                message += f"\n{'  '.join(dealers_cards)} (Total: {dealers_total})" 
                message += f"\n\n**{ctx.author.name.upper()}\'s CARDS:**" 
                message += f"\n{'  '.join(users_cards)} (Total: {users_total})"
                message += "\n\nBUST - You Win"
                if bid == 0: 
                    message += f"\nYou won!"
                elif users_total == 21:
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
                if bid == 0: 
                    message += f"\nYou won!"
                elif users_total == 21:
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

            
    @commands.command(aliases=["flip", "flipcoin"])
    @commands.cooldown(1, 5, BucketType.user)
    async def coinflip(self, ctx, guess, bid:int = 0): 
        guess = guess.lower()
        if bid < 250 and bid != 0:
            await ctx.send("Minimum bid for coinflipping is 250, this aint a children's game.")
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
            if bid > 0:
                msg+= "\nLooks like I'll be keeping your money, and don't you go crying to me about it."
        else:
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", bid, str(ctx.author.id), str(ctx.guild.id))
            if bid > 0:
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
            await ctx.send(f"{u.mention}, you have {user[0]['coins']} coins")
        else: 
            await ctx.send(f"{u.name} has {user[0]['coins']} coins")               
                           
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
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
    @commands.cooldown(1, 5, BucketType.user)
    async def richest(self, ctx):
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE serverid=$1ORDER BY coins DESC LIMIT 5", str(ctx.guild.id))
        msg = ""    
        for u in range(0, len(user)):
            msg += f"{u+1}. <@!{user[u]['userid']}> - {int(user[u]['coins'])}\n"            
        embed = discord.Embed(title=f"Richest in Server", description=msg, color=0x00ff00)
                       
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def slots(self, ctx, bid:int=0): 
        
        
        if bid != 0 and bid < 50:
            await ctx.send("Minimum bid is 50")
            return
                       
        user = await self.client.pg_con.fetch("SELECT * FROM users WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))              
        if bid > user[0]["coins"]:
            await ctx.send("You're too poor to bid that much.")
            return
        else:
            await self.client.pg_con.execute("UPDATE users SET coins = coins - $1 WHERE userid = $2 AND serverid = $3", bid, str(ctx.author.id), str(ctx.guild.id))
               
                       
                       
        choices1 = [":grapes:", ":pear:", ":apple:", ":tangerine:", ":lemon:", ":cherries:", ":avocado:", ":pineapple:", ":peach:", ":strawberry:"]
        choices2 = [":grapes:", ":pear:", ":apple:", ":tangerine:", ":lemon:", ":cherries:", ":avocado:", ":pineapple:", ":peach:", ":strawberry:"]
        choices3 = [":grapes:", ":pear:", ":apple:", ":tangerine:", ":lemon:", ":cherries:", ":avocado:", ":pineapple:", ":peach:", ":strawberry:"]

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

        winmessage = "Sorry, you lost!"
        win = 0
        if slots1 == slots2 == slots3 and fslots1 == fslots2 == fslots3 and fslots4 == fslots5 == fslots6: 
            winmessage = "Holy shit, what the fuck!"
            win = bid*4321
                           
        elif slots1 == slots2 == slots3: 
            if fslots1 == fslots2 == fslots3 or fslots4 == fslots5 == fslots6: 
                winmessage = "That's amazing!" 
                win = bid*225
            else:
                winmessage = "Winner!!!"
                win = bid*120
        elif fslots1 == fslots2 == fslots3 and fslots4 == fslots5 == fslots6:  
            winmessage = "Hey, that's pretty cool!" 
            win = bid*175
        elif fslots1 == fslots2 == fslots3 or fslots4 == fslots5 == fslots6:
            winmessage = "Not a dub but have a bonus"
            win = bid*15
        else: 
            winmessage = f"You lost!"
        
        if win > 0: 
            if bid > 0:            
                winmessage += f"\n**{ctx.author.name}** won {win} coins."
            else:
                winmessage += f"\n**{ctx.author.name}** won nothing, what a pepega for not bidding."
        else:
            if bid > 0:
                winmessage += f"\n**{ctx.author.name}** lost {bid} coins."
            else:
                winmessage += f"\n**{ctx.author.name}** lost nothing."
                           
                          
        await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", win, str(ctx.author.id), str(ctx.guild.id)) 
        await ctx.send(f"|   {fslots1}{fslots2}{fslots3}\n\▶{slots1}{slots2}{slots3}\n|   {fslots4}{fslots5}{fslots6}\n{winmessage}")

    
    @commands.command()
    @commands.cooldown(1, 600, BucketType.user)
    async def mine(self, ctx): 
        pickaxe = await self.client.pg_con.fetch("SELECT * FROM useritems WHERE userid = $1 AND serverid = $2 AND itemid = 1", str(ctx.author.id), str(ctx.guild.id))
        if len(pickaxe) == 0: 
            await ctx.send("You don't have a pickaxe.")
            ctx.command.reset_cooldown(ctx)
            return
        if random.randint(0, 16) == 8: 
            await ctx.send("You tried to mine but your pickaxe broke!")
            await self.client.pg_con.execute("DELETE FROM useritems WHERE ctid IN (SELECT ctid FROM useritems WHERE userid=$1 AND serverid=$2 AND itemid = 1 LIMIT 1)", str(ctx.author.id), str(ctx.guild.id))
            return
        else:
            win = random.randint(10, 150) 
            await ctx.send(f"You successfully mined {win} coins worth of ore.")
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", win, str(ctx.author.id), str(ctx.guild.id))
    
    @mine.error
    async def mine_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            t_left = math.ceil(float(str(error).split(" ")[-1][:-1]))
            await ctx.send(f"You're too tired to go mining, try again in {t_left} seconds.")
                           
    @commands.command()
    @commands.cooldown(1, 600, BucketType.user)
    async def fish(self, ctx): 
        
        def check(m): 
            if ctx.author != m.author:
                return False
            if m.content.lower() == "come to me, loch ness monster": 
                return True
            else:
                return False
                           
                           
        rod = await self.client.pg_con.fetch("SELECT * FROM useritems WHERE userid = $1 AND serverid = $2 AND itemid = 2", str(ctx.author.id), str(ctx.guild.id))
        if len(rod) == 0: 
            await ctx.send("You don't have a fishing rod.")
            ctx.command.reset_cooldown(ctx)
            return
        if random.randint(0, 16) == 8: 
            await ctx.send("Your fishing rod broke while fishing! You came home with nothing.")
            await self.client.pg_con.execute("DELETE FROM useritems WHERE ctid IN (SELECT ctid FROM useritems WHERE userid=$1 AND serverid=$2 AND itemid = 2 LIMIT 1)", str(ctx.author.id), str(ctx.guild.id))
            return
        else:
            win = random.randint(0, 100)
            if win <= 70: 
                win = random.randint(25, 75)
                await ctx.send(f"You went fishing and caught {win} coins worth of fish.")
            elif win <= 90: 
                win = random.randint(100, 200)
                await ctx.send(f"While fishing you caught a huge one worth {win} coins.")
            elif win <= 99: 
                win = random.randint(250, 500)
                await ctx.send(f"While fishing, you caught a MASSIVE one worth {win} coins.")
            else: 
                await ctx.send("Holy $#!t!? Is that the Loch Ness Monster? Quickly, type `come to me, loch ness monster`")
                try:
                    msg = await self.client.wait_for('message', timeout=20.0, check=check)
                except:
                    await ctx.send("The loch ness monster swam away! You returned home with nothing.")
                    return
                win = random.randint(3000, 8000)
                await ctx.send(f"What?! You caught the Loch Ness Monster?!\nSold `Loch Ness Monster` for {win} coins.")
                           
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", win, str(ctx.author.id), str(ctx.guild.id))
    
    @fish.error
    async def mine_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            t_left = math.ceil(float(str(error).split(" ")[-1][:-1]))
            await ctx.send(f"You're too tired to go fishing, try again in {t_left} seconds.")
                           
    @commands.command()
    @commands.cooldown(1, 600, BucketType.user)
    async def hunt(self, ctx): 
        
        def check(m): 
            if ctx.author != m.author:
                return False
            if m.content.lower() in ["fight", "flee"]:
                return True
            else:
                return False
                           
                           
        sword = await self.client.pg_con.fetch("SELECT * FROM useritems WHERE userid = $1 AND serverid = $2 AND itemid = 3", str(ctx.author.id), str(ctx.guild.id))
        if len(sword) == 0: 
            await ctx.send("You don't have a sword and you're too weak to hunt with your fists.")
            ctx.command.reset_cooldown(ctx)
            return
        if random.randint(0, 16) == 8: 
            await ctx.send("You go to slash at a rabbit but then the sword snapped. You go home with nothing but a broken sword.")
            await self.client.pg_con.execute("DELETE FROM useritems WHERE ctid IN (SELECT ctid FROM useritems WHERE userid=$1 AND serverid=$2 AND itemid = 3 LIMIT 1)", str(ctx.author.id), str(ctx.guild.id))
            return
        else:
            win = random.randint(0, 100)
            if win <= 60: 
                           
                await ctx.send("While hunting you encounter a rabbit.\nWill you `fight` or `flee`")
                msg = await self.client.wait_for('message', timeout=20.0, check=check)
                if msg.content.lower() == "fight":
                    win = random.randint(10, 50)
                    await ctx.send("You fought a rabbit and successfully won, how brave of you.")
                else:
                    await ctx.send("Did you just run away from a rabbit? I don't think this is the right job for you")
                    win = 0
                           
            elif win <= 85: 
                           
                await ctx.send("While hunting you encounter a deer.\nWill you `fight` or `flee` (Success 90%)")
                msg = await self.client.wait_for('message', timeout=20.0, check=check)
                if msg.content.lower() == "fight":
                    if random.randint(0, 100) <= 90:
                        win = random.randint(120, 180)
                        await ctx.send("You hunted down the deer and went home with it!")
                    else:
                        win = -(random.randint(0, 200))
                        await ctx.send("The deer spotted you and then proceeded to knock you out, you got robbed while you were knocked out.")
                else:
                    await ctx.send("You questioned your life choices and went home.")
                    win = 0
                           
            elif win <= 99: 
                           
                await ctx.send("While hunting you encounter a boar.\nWill you `fight` or `flee` (Success 75%)")
                msg = await self.client.wait_for('message', timeout=20.0, check=check)
                if msg.content.lower() == "fight":
                    if random.randint(0, 100) <= 75:
                        win = random.randint(250, 450)
                        await ctx.send("After a tough fight, you won and went home with a boar!")
                    else:
                        win = -(random.randint(200, 500))
                        await ctx.send("As soon as you go to slash at the boar, it headbutts you and then beats you up.")
                else:
                    await ctx.send("You decided you were to weak for such an enemy and ran home crying.")
                    win = 0
                           
            else: 
                await ctx.send("While hunting you encoun-WTF IS THAT A DRAGON? GET IT!\nWill you `fight` or `flee` (Success 50%)")
                msg = await self.client.wait_for('message', timeout=20.0, check=check)
                if msg.content.lower() == "fight":
                    if random.randint(0, 100) <= 50:
                        win = random.randint(8000, 12000)
                        await ctx.send("Did.. you just defeat a DRAGON?")
                    else:
                        win = -(random.randint(2000, 4000))
                        await ctx.send("Why did you think fighting a dragon was a good idea? You were burned alive.")
                else:
                    await ctx.send("You didn't have a death wish so you went home, you look back to see the dragon flying to a nearby village, uh oh.")
                    win = 0
          
            await self.client.pg_con.execute("UPDATE users SET coins = coins + $1 WHERE userid = $2 AND serverid = $3", win, str(ctx.author.id), str(ctx.guild.id))
            if win > 0: 
                await ctx.send(f"You earned {win} coins!")
            elif win < 0:
                await ctx.send(f"You lost {win} coins!")
            else:
                await ctx.send(f"You went home with nothing!")        
    
    @hunt.error
    async def mine_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandOnCooldown):
            t_left = math.ceil(float(str(error).split(" ")[-1][:-1]))
            await ctx.send(f"You're too tired to go hunting, try again in {t_left} seconds.")
                           
    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def inventory(self, ctx): 
        items = await self.client.pg_con.fetch("SELECT * FROM useritems WHERE userid = $1 AND serverid = $2", str(ctx.author.id), str(ctx.guild.id))
        if len(items) == 0:
            await ctx.send("You have nothing, <:omegaLUL:616657657486376961>")
            return
        message = ""
        for i in items:
            message += f"[{i['itemid']}] {i['itemname']}\n"
        embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", description=message)
        await ctx.send(embed=embed)
            
                           
def setup(client):
    client.add_cog(Currency(client))
