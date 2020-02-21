from discord.ext import tasks
from redbot.core import Config
import discord
import os
import asyncio
from discord.ext import commands
import json
from fuzzywuzzy import process
from redbot.core import commands

class MOTORSPORT_ORDER(commands.Cog):
    """Motorsport Order System"""

    def __init__(self, bot):
        self.bot = bot
        self.prices = Config.get_conf(None, identifier=1, cog_name='MOTORSPORT_PRICE')
        self.membership = Config.get_conf(None, identifier=1, cog_name="MOTORSPORT_CUSTOMERS")
        data = {"Name": "",
                "MemberID": "",
                "Orders": [],
                "VIP_Status": False,
                "Customer_Status": False,
                "Shopper_Status": True,
        }
        self.membership.register_member(**data)

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def order(self, ctx, *, car_name=None):
        def check(m):
            return m.channel == ordering_channel and m.author == ctx.author
        guild = ctx.guild
        author = ctx.author
        order_channel = self.bot.get_channel(341936700366258177)
        member = guild.get_member(author.id)
        ordering_channel = self.bot.get_channel(629301622870376448)
        car_name_recieve = 0
        if len(ordering_channel.overwrites) > 1:
            await ctx.send("""Someone else is placing order right now. Please try again later!""")
        else:
            await ordering_channel.set_permissions(author, read_messages=True)
            await ordering_channel.send(author.mention)
            if any(r.name == 'VIP' for r in member.roles):
                msg = await ordering_channel.send("""Hi, Welcome to Premium Deluxe Motorsport **VIP** Ordering System""")
                VIP = 1
            else:
                msg = await ordering_channel.send("""Hi, Welcome to Premium Deluxe Motorsport Ordering System""")
                VIP = 0
            while True:
                try:
                    await ordering_channel.send("""What is your First and Last name? (Character Name)""")
                    customer_name = await self.bot.wait_for('message', check=check, timeout=120)
                    await ordering_channel.send("""What is your phone number? (If you do not have your  phone, type 'None')""")
                    contact_number = await self.bot.wait_for('message', check=check, timeout=120)
                    await ordering_channel.send("""Do you preferred to be contacted by Phone (In-game) or Email (Discord)?""")
                    contact_method = await self.bot.wait_for('message', check=check, timeout=120)
                except asyncio.TimeoutError: 
                    await ordering_channel.send("Timeout! Please type !order to place order again")
                    break
                try:
                    await ordering_channel.send("""Any questions and comments?""")
                    customer_remarks = await self.bot.wait_for('message', check=check, timeout=120)
                    customer_remarks = customer_remarks.content
                except asyncio.TimeoutError: 
                    await ordering_channel.send("""Nothing? Alright.""")
                    customer_remarks = "None"
                while True:
                    if car_name is None:
                        await ordering_channel.send("What is the vehicle name?")
                        try:
                            car_name = await self.bot.wait_for('message', check=check, timeout=120)
                            car_name = car_name.content
                        except asyncio.TimeoutError: 
                            await ordering_channel.send("Timeout! Please type !order to place order again")
                            break
                    else:
                        Prices = await self.prices.guild(ctx.guild).Prices()
                        car_list = [d['Vehicle Name'] for d in Prices]
                        car_name_matched = process.extractBests(car_name.lower(), car_list, score_cutoff=80, limit=2)
                        not_matched = False
                        multiple_match = False
                        if str(car_name_matched) == '[]':
                            not_matched = True
                        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
                            multiple_match = True
                        if not_matched == False and multiple_match != True:
                            for price in Prices:
                                if price["Vehicle Name"] == car_name_matched[0][0]:
                                    embed2 = discord.Embed(colour=discord.Colour(0x984c87))
                                    embed2.set_image(url=price['Performance Image'])
                                    embed2.add_field(name="Capacity:", value=price['Capacity'], inline=True)
                                    embed2.add_field(name="Drive:", value=price['Drive'], inline=True)
                                    embed = discord.Embed(title=price['Vehicle Name'], colour=discord.Colour(0x984c87), description=price['Types'])
                                    embed.set_image(url=price['Vehicle Image'])
                                    embed.set_thumbnail(url=price['Brand Image'])
                                    embed.add_field(name="Brand:", value=price['Brand'], inline=True)
                                    if VIP == 1:
                                        embed.add_field(name="VIP Price:", value=price['VIP Price'], inline=True)
                                        final_price = price['VIP Price']
                                    else:
                                        embed.add_field(name="Price:", value=price['Price'], inline=True)
                                        final_price = price['Price']
                                    embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                                    final_vehname = price['Vehicle Name']
                                    final_vehclass = price['Types']
                                    car_name_recieve = 1
                            if car_name_recieve == 1:
                                break
                        else:
                            if multiple_match != True:
                                thesimilarresult = "__**Did you mean?**__\n"
                                car_name_matched = process.extract(car_name, car_list, limit=5)
                                if car_name_matched[0][0] != "Vehicle Name":
                                    for i in range(len(list(car_name_matched))):
                                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                                    await ordering_channel.send("""**Vehicle not found\nTry to provide more details on your search**\n\n""" + thesimilarresult)
                                    car_name = None
                                    pass
                                else:
                                    await ordering_channel.send("""**Vehicle not found\nTry to provide more details on your search**\n\n""")
                                    car_name = None
                                    pass
                            else:
                                await ordering_channel.send("""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))
                                car_name = None
                                pass
                if car_name_recieve == 0:
                    break
                elif car_name_recieve == 1:
                    await ordering_channel.send("""__**Please check the following:**__""", embed=embed)
                    await ordering_channel.send(embed=embed2)
                    embed3 = discord.Embed(colour=discord.Colour(0x984c87))
                    embed3.set_thumbnail(url="http://www.buygosleep.com/wp-content/uploads/2016/01/Car-Icon.png")
                    embed3.set_author(name=customer_name.content, icon_url=author.avatar_url)
                    embed3.set_footer(text="Posted by " + author.name + "#" + author.discriminator)
                    embed3.add_field(name="Vehicle Name", value=final_vehname + " ({})".format(final_vehclass), inline=True)
                    embed3.add_field(name="Price", value=final_price, inline=True)
                    embed3.add_field(name="Preferred to be contacted by", value=contact_method.content, inline=True)
                    embed3.add_field(name="Phone Number", value=contact_number.content, inline=True)
                    embed3.add_field(name="Discord", value=author.mention, inline=True)
                    embed3.add_field(name="Remarks", value=customer_remarks)
                    await ordering_channel.send(embed=embed3)
                    await ordering_channel.send("""Is that correct? (**Yes**/**No**)""")
                    try:
                        answer = await self.bot.wait_for('message', check=check, timeout=120)
                        if answer.content.lower() == 'yes':
                            if VIP == 1:
                                embed4 = discord.Embed(colour=discord.Colour(0xFF0000))
                            else:
                                embed4 = discord.Embed(colour=discord.Colour(0x7CFC00))
                            embed4.set_thumbnail(url="http://www.buygosleep.com/wp-content/uploads/2016/01/Car-Icon.png")
                            embed4.set_author(name=customer_name.content, icon_url=author.avatar_url)
                            embed4.set_footer(text="Posted by " + author.name + "#" + author.discriminator)
                            embed4.add_field(name="Vehicle Name", value=final_vehname + " ({})".format(final_vehclass), inline=True)
                            embed4.add_field(name="Price", value=final_price, inline=True)
                            embed4.add_field(name="Preferred to be contacted by", value=contact_method.content, inline=True)
                            embed4.add_field(name="Phone Number", value=contact_number.content, inline=True)
                            embed4.add_field(name="Discord", value=author.mention, inline=True)
                            embed4.add_field(name="Remarks", value=customer_remarks)
                            if VIP == 1:
                                msg = await order_channel.send(content="@everyone, we have new order from **VIP** {}.".format(author.mention), embed=embed4)
                            else:
                                msg = await order_channel.send(content="@everyone, we have new order from {}.".format(author.mention), embed=embed4)
                            await ordering_channel.send("""Thank you for shopping with **Premium Deluxe Motorsport**, **{}**. Our sales team will contact you as soon as possible.""".format(customer_name.content))
                            await msg.add_reaction("✅")
                            await msg.add_reaction("🤝")
                            await msg.add_reaction("💎")
                            await self.membership.member(author).Name.set(customer_name.content)
                            await self.membership.member(author).MemberID.set(author.id)
                            price = final_price.replace("$ ","").replace(',',"")
                            price = int(price)
                            async with self.membership.member(author).Orders() as orders:
                                orders.append({"Order_ID": msg.id, "Vehicle_Name": final_vehname, "Price": price, "Status": "Shipping"})
                            break
                        elif answer.content.lower() == 'no':
                            car_name = None
                            pass
                    except asyncio.TimeoutError: 
                        await ordering_channel.send("Timeout! Please type !order to place order again")
                        break
            try:
                await self.bot.wait_for('message', check=check, timeout=10)
                await ordering_channel.set_permissions(author, overwrite=None)
                await ordering_channel.purge(around=msg)
            except asyncio.TimeoutError:
                try:
                    await ordering_channel.set_permissions(author, overwrite=None)
                    await ordering_channel.purge(around=msg)
                except discord.NotFound:
                    pass