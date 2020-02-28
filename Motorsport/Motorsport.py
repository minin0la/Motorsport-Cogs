import discord
from discord.ext import tasks
from discord.ext import commands
from redbot.core import Config
from redbot.core import utils
from redbot.core import commands
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path

import requests
import os
import asyncio
import json
from fuzzywuzzy import process
import pygsheets
import random
import datetime
import time

#PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from .Order import Order
from .Database import Database
from .Membership import Membership

class Motorsport(Order, Database, commands.Cog):
    """Motorsport Database System"""

    def __init__(self, bot):
        self.bot = bot
        self.update_vehicle.start()
        super().__init__()
    
    def cog_unload(self):
        self.update_vehicle.cancel()

    #Updating Vehcile Database
    @commands.command(pass_context=True)
    @commands.has_any_role("Administrator")
    @commands.guild_only()
    async def updatevehicle(self, ctx):
        start_time = time.time()
        await ctx.send("Please wait...")
        veh_price = await super().vehicle_price()
        stocks = await super().vehicle_stock()
        speed = await super().vehicle_speed()
        veh_price = await self.combinedata(veh_price, stocks, speed)
        await self.comparingstocks(veh_price)
        await ctx.send("Done\n--- Took %s seconds ---" % (time.time() - start_time))

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def order(self, ctx):
        author = ctx.author
        guild = ctx.guild
        date = str(datetime.datetime.now().strftime("%d/%m/%y"))
        name, ordering_channel, finished_order = await super().order(ctx, car_name=None, ordering_channel=None)
        membershipinfo = await self.membershipdb.member(author).get_raw()
        if membershipinfo["Name"] == "" and finished_order is True:
            await self.membershipdb.member(author).Name.set(name)
            await self.membershipdb.member(author).MemberID.set(author.id)
            await self.membershipdb.member(author).Joined_Date.set(date)
            customer_role = ctx.guild.get_role(343722834016862211)
            await author.add_roles(customer_role)
            image = await Membership.create_card(self, ctx, author, name, date)
            embed = discord.Embed(
                title="Motorsport Management",
                colour=author.top_role.colour,
                description="Dear {},\n\nThank you for registering a membership with us at Premium Deluxe Motorsport!\nFind out more about your membership by using !membership\nCheck out your order history by !membership orders".format(
                    name
                ),
            )
            embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
            embed.set_image(url="attachment://" + str(author.id) + ".png")
            await ordering_channel.send(file=image, embed=embed)
        await asyncio.sleep(10.0)
        await ordering_channel.delete()
        
    
    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def price(self, ctx, *, car_name: str):
        """Used to search price"""

        pages = []
        price, embed = await self.get_vehicle(ctx, car_name)
        if price is None:
            msg = await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="{} {}".format(price['Name'], "**[NOT FOR SALE]**" if price['For_Sale'] == 'FALSE' else ""), colour=discord.Colour(0x984c87), description=price['Type'])
            embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
            embed.set_image(url=price['Vehicle Image'])
            embed.set_thumbnail(url=price['Brand Image'])
            embed.add_field(name="Brand", value=price['Brand'], inline=True)
            if ctx.channel.id == 343448488715223040:
                embed.add_field(name="Price", value="$ {:,}".format(price['Price']['Normal']), inline=True)
            elif ctx.channel.id == 345788278131261442:
                embed.add_field(name="VIP Price", value="$ {:,}".format(price['Price']['VIP']), inline=True)
            elif ctx.channel.category_id == 360808237802455041:
                embed.add_field(name="Price", value="$ {:,}".format(price['Price']['Normal']), inline=True)
                embed.add_field(name="VIP Price", value="$ {:,}".format(price['Price']['VIP']), inline=True)
            if price['Stock'] is not None:
                embed.add_field(name="Stock ({} Qty)".format(price['Stock']), value="$ {:,}".format(price['Price']['Stock_Price']), inline=True)
            
            embed.add_field(name="Storage (Trunk)", value=price['Storage']['Trunk'], inline=True)
            embed.set_footer(text="Press ➡️ to see vehicle info")
            embed2 = discord.Embed(colour=discord.Colour(0x984c87))
            if price['Speed']['Laptime']['Overall'] is not None:
                embed2.add_field(name="Laptime\n(Overall)", value=price['Speed']['Laptime']['Overall'], inline=True)
                embed2.add_field(name="Laptime\n(Class)", value=price['Speed']['Laptime']['Class'], inline=True)
                embed2.add_field(name="Laptime\n(Time)", value=price['Speed']['Laptime']['Value'], inline=True)
                embed2.add_field(name="Top Speed\n(Overall)", value=price['Speed']['Top_Speed']['Overall'], inline=True)
                embed2.add_field(name="Top Speed\n(Class)", value=price['Speed']['Top_Speed']['Class'], inline=True)
                embed2.add_field(name="Top Speed\n(Speed)", value="{} km/h".format(int(price['Speed']['Top_Speed']['Value'])), inline=True)
            embed2.set_image(url=price['Performance Image'])
            embed2.set_thumbnail(url='https://i.imgur.com/xJyIgAQ.png')    
            embed2.add_field(name="Storage (Trunk)", value=price['Storage']['Trunk'], inline=True)
            embed2.add_field(name="Storage (Glovebox)", value=price['Storage']['Glovebox'], inline=True)
            embed2.add_field(name="Drive", value=price['Drive'], inline=True)
            embed2.add_field(name="Capacity", value=price['Capacity'], inline=False)
            embed2.set_footer(text="Press ➡️ to see vehicle price")
            pages.append(embed)
            pages.append(embed2)
            CONTROLS = {"➡️": utils.menus.next_page}
            await utils.menus.menu(ctx, pages, CONTROLS, timeout=60.0)

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def stock(self, ctx, *, vehicle_name): 
        """
        Used to search in-stock vehicle
        """
        selected_veh, embed = await self.get_vehicle(ctx, vehicle_name)
        if selected_veh is None:
            await ctx.send(embed=embed)
        else:
            if selected_veh['Stock'] is not None:
                await ctx.send("I have found {} {} in-stock for ${:,d}".format(selected_veh['Stock'], selected_veh['Name'], selected_veh['Price']['Stock_Price']))    
            else:
                await ctx.send("Vehicle not in stock")
    
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.default)
    async def allstock(self, ctx):
        stocks = await self.database.guild(ctx.guild).Vehicles()
        classlist = [x['Type'] for x in stocks]
        classlist = list(dict.fromkeys(classlist))
        pages = []
        fieldnumber = 0
        embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF00FF))
        embed.set_thumbnail(url='https://i.imgur.com/xJyIgAQ.png')
        for x in classlist:
            message = ""
            for y in stocks:
                if y['Type'] == x and y['Stock'] is not None:
                    message = message + "{} ({} Qty): ${:,d}\n".format(y['Name'], y['Stock'], y['Price']['Stock_Price'])
            message = utils.chat_formatting.pagify(message, delims='\n', page_length=1000)
            try:
                for num, value in enumerate(message, 1):
                    embed.add_field(name="{} (Page {})".format(x, num), value="```\n" + value + "```", inline=False)
                    fieldnumber = fieldnumber + 1
            except:
                pass
            if fieldnumber > 4:
                pages.append(embed)
                fieldnumber = 0
                embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF00FF))
        msg = await ctx.send('All the stock available in Motorsport Right now\n')
        CONTROLS = {"⬅️": utils.menus.prev_page, "❌": utils.menus.close_menu, "➡️": utils.menus.next_page}
        await utils.menus.menu(ctx, pages, CONTROLS, timeout=60.0)
        themessage = await ctx.channel.history(after=msg.created_at, limit=1).flatten()
        try:
            await themessage[0].delete()
        except:
            pass
        await msg.delete()
    
        
    #----------------------Membership----------------------
    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def membership(self, ctx, option=None):
        """Used to manage membership
        """
        if ctx.invoked_subcommand is None:
            if option is not None:
                if "Bot-Developer" in [x.name for x in ctx.author.roles]:
                    cmd = self.bot.get_command(f"membership info")
                    await ctx.invoke(cmd, user_id=option)
            else:
                cmd = self.bot.get_command(f"membership info")
                await ctx.invoke(cmd, user_id=ctx.author.id)

    # [p]membership info
    @membership.command(pass_context=True)
    async def info(self, ctx, user_id=None):
        """Check membership Info
        """
        if user_id is not None:
            if "Bot-Developer" in [x.name for x in ctx.author.roles]:
                try:
                    author = await ctx.guild.fetch_member(int(user_id))
                except ValueError:
                    ctx.invoked_subcommand = user_id
            else:
                author = ctx.author
        else:
            author = ctx.author
        membershipinfo = await self.membershipdb.member(author).get_raw()
        if membershipinfo["Name"] != "":
            value = 0
            orders = await self.membershipdb.member(author).Orders()
            for x in orders:
                try:
                    value = value + int(float(x["Price"]))
                except:
                    pass
            embed = discord.Embed(colour=author.top_role.colour)
            embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
            embed.set_author(name=membershipinfo["Name"], icon_url=author.avatar_url)
            embed.add_field(
                name="Purchases", value=len(membershipinfo["Orders"]), inline=True
            )
            embed.add_field(
                name="Total spent", value="$ {:,}".format(value), inline=True
            )
            try:
                filename = "users/" + str(author.id) + ".png"
                image = discord.File(str(bundled_data_path(self) / filename))
                embed.set_image(url="attachment://" + str(author.id) + ".png")
                await ctx.send(file=image, embed=embed)
            except:
                pass
        else:
            await ctx.send(
                "Please register by using !membership register or start ordering with !order"
            )
    
    @membership.command(pass_context=True)
    async def register(self, ctx, *, name: str):
        """Register an account with Motorsport

        Usage: !register <name>
        Example: !register Jasper Akerman
        """
        author = ctx.author
        guild = ctx.guild
        date = str(datetime.datetime.now().strftime("%d/%m/%y"))
        membershipinfo = await self.membershipdb.member(author).get_raw()
        if membershipinfo["Name"] == "":
            await self.membershipdb.member(author).Name.set(name)
            await self.membershipdb.member(author).MemberID.set(author.id)
            await self.membershipdb.member(author).Joined_Date.set(date)
            customer_role = ctx.guild.get_role(343722834016862211)
            await author.add_roles(customer_role)
            image = await Membership.create_card(self, ctx, author, name, date)
            embed = discord.Embed(
                title="Motorsport Management",
                colour=author.top_role.colour,
                description="Dear {},\n\nThank you for registering a membership with us at Premium Deluxe Motorsport!".format(
                    name
                ),
            )
            embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
            embed.set_image(url="attachment://" + str(author.id) + ".png")
            await ctx.send(file=image, embed=embed)
        else:
            await ctx.send("You are already registered!")
    
    # [p]membership unregister
    @membership.command(pass_context=True)
    async def unregister(self, ctx, user_id=None):
        """Unregister an account from Motorsport

        Usage: !unregister
        """
        if user_id is not None:
            if "Administrator" in [x.name for x in ctx.author.roles]:
                author = await ctx.guild.fetch_member(int(user_id))
            else:
                author = ctx.author
        else:
            author = ctx.author

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            await ctx.send(
                "Are you sure you want to unregister? All data will be ereased. (Yes/No)"
            )
            answer = await self.bot.wait_for("message", check=check, timeout=120)
            if answer.content.lower() == "yes":
                await self.membershipdb.member(author).clear()
                await ctx.send("You have unregistered your membership here.")
            else:
                await ctx.send("Nothing has been done.")
        except asyncio.TimeoutError:
            await ctx.send("You did not answer in time.")

    # [p]membership orders
    @membership.command(pass_context=True)
    async def orders(self, ctx, user_id=None):
        """Check orders history with Motorsport
        """
        if user_id is not None:
            if "Bot-Developer" in [x.name for x in ctx.author.roles]:
                author = await ctx.guild.fetch_member(int(user_id))
            else:
                author = ctx.author
        else:
            author = ctx.author
        membershipinfo = await self.membershipdb.member(author).get_raw()
        processing = ""
        shipping = ""
        completed = ""
        try:
            if membershipinfo["Name"] != "":
                embed = discord.Embed(
                    title="Motorsport Orders", colour=author.top_role.colour
                )
                embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
                embed.set_author(
                    name=membershipinfo["Name"], icon_url=author.avatar_url
                )
                try:
                    for x in membershipinfo["Orders"]:
                        if x["Status"] == "Processing":
                            processing = processing + "- {} (Order ID: {})\n".format(
                                x["Name"], x["msg_id"]
                            )
                        if x["Status"] == "Shipping":
                            shipping = shipping + "- {} (Order ID: {})\n".format(
                                x["Name"], x["msg_id"]
                            )
                        if x["Status"] == "Completed":
                            completed = completed + "- {} (Order ID: {})\n".format(
                                x["Name"], x["msg_id"]
                            )
                    processing = utils.chat_formatting.pagify(
                        processing, delims="\n", page_length=1000
                    )
                    shipping = utils.chat_formatting.pagify(
                        shipping, delims="\n", page_length=1000
                    )
                    completed = utils.chat_formatting.pagify(
                        completed, delims="\n", page_length=1000
                    )
                    for num, x in enumerate(processing, 1):
                        x = "```diff\n" + x + "```"
                        embed.add_field(
                            name="Processing ({})".format(num), value=x, inline=False
                        )
                    for num, x in enumerate(shipping, 1):
                        x = "```diff\n" + x + "```"
                        embed.add_field(
                            name="Shipping ({})".format(num), value=x, inline=False
                        )
                    for num, x in enumerate(completed, 1):
                        x = "```diff\n" + x + "```"
                        embed.add_field(
                            name="Completed ({})".format(num), value=x, inline=True
                        )
                    await ctx.send(embed=embed)
                except:
                    embed.add_field(name="", value="No history", inline=False)
            else:
                await ctx.send(
                    "Please register by using !membership register or start ordering with !order"
                )
        except:
            pass

    @membership.command(pass_context=True)
    @commands.has_any_role("Administrator")
    async def importall(self, ctx, user_id=None):
        """Import all data from #orders channel to users
        """
        guild = ctx.guild
        channel = self.bot.get_channel(341936700366258177)
        message = await channel.history(limit=3000).flatten()
        counter = 0
        for x in message:
            try:
                message_data = x.embeds[0].to_dict()
                for y in message_data["fields"]:
                    if y["name"] == "Discord":
                        memberid = y["value"]
                    if y["name"] == "Vehicle Name":
                        car_name = y["value"]
                    if y["name"] == "Price":
                        price = y["value"].replace("$ ", "").replace(",", "")
                        price = int(float(price))
                new_memberid = (
                    memberid.replace("<", "")
                    .replace(">", "")
                    .replace("@", "")
                    .replace("!", "")
                )
                if user_id is not None:
                    if new_memberid == user_id:
                        member = guild.get_member(int(new_memberid))
                        spent = await self.membershipdb.member(member).Spent()
                        spent = spent + price
                        async with self.membershipdb.member(member).Orders() as orders:
                            orders.append(
                                {
                                    "Order_ID": x.id,
                                    "Vehicle_Name": car_name,
                                    "Price": price,
                                    "Status": "Completed",
                                }
                            )
                            counter = counter + 1
                else:
                    member = guild.get_member(int(new_memberid))
                    spent = await self.membershipdb.member(member).Spent()
                    spent = spent + price
                    async with self.membershipdb.member(member).Orders() as orders:
                        orders.append(
                            {
                                "msg_id": x.id,
                                "Name": car_name,
                                "Price": price,
                                "Status": "Completed",
                            }
                        )
                        counter = counter + 1
            except:
                pass
        await ctx.send("Imported {}".format(counter))

    @membership.command(pass_context=True)
    @commands.has_any_role("Administrator")
    async def clearorders(self, ctx, user_id=None):
        """Reset user's orders
        """
        guild = ctx.guild
        member = guild.get_member(int(user_id))
        await self.membershipdb.member(member).Orders.set([])
        await self.membershipdb.member(member).Spent.set(0)
        await ctx.send("Order history for {} has been cleared".format(member.mention))

    @membership.command(pass_context=True)
    @checks.is_owner()
    async def resetall(self, ctx):
        """Reset membership database
        """
        await self.database.clear_all()
        await ctx.send("Cleared All")

    @commands.group(pass_context=True)
    @commands.guild_only()
    @commands.has_any_role("Administrator")
    async def membershipset(self, ctx):
        """Set user's data
        """
        pass

    @membershipset.command(pass_context=True)
    @commands.has_any_role("Administrator")
    async def date(self, ctx, user_id: int, *, date: str):
        """Used to set user's registered date
        """
        author = await ctx.guild.fetch_member(user_id)
        name = str(await self.database.member(author).Name())
        date = date
        await self.membershipdb.member(author).Joined_Date.set(date)
        image = await Membership.create_card(self, ctx, author, name, date)
        embed = discord.Embed(
            title="Motorsport Management",
            colour=author.top_role.colour,
            description="The registered date for {} has been set to {}".format(author.mention, date),
        )
        embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
        embed.set_image(url="attachment://" + str(author.id) + ".png")
        await ctx.send(file=image, embed=embed)

    @membershipset.command(pass_context=True)
    @commands.has_any_role("Administrator")
    async def name(self, ctx, user_id: int, *, name: str):
        """Used to set user's name
        """
        author = await ctx.guild.fetch_member(user_id)
        name = name
        date = str(await self.database.member(author).Joined_Date())
        await self.membershipdb.member(author).Name.set(name)
        image = await Membership.create_card(self, ctx, author, name, date)
        embed = discord.Embed(
            title="Motorsport Management",
            colour=author.top_role.colour,
            description="The name for {} has been set to {}".format(author.mention, name),
        )
        embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
        embed.set_image(url="attachment://" + str(author.id) + ".png")
        await ctx.send(file=image, embed=embed)

    @membershipset.command(pass_context=True)
    @commands.has_any_role("Administrator")
    async def newcard(self, ctx, user_id: int):
        """Used to set user's registered date
        """
        author = await ctx.guild.fetch_member(user_id)
        name = str(await self.membershipdb.member(author).Name())
        date = str(await self.membershipdb.member(author).Joined_Date())
        image = await Membership.create_card(self, ctx, author, name, date)
        embed = discord.Embed(
            title="Motorsport Management",
            colour=author.top_role.colour,
            description="The new card for {} has been generated".format(
                author.mention
            ),
        )
        embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
        embed.set_image(url="attachment://" + str(author.id) + ".png")
        await ctx.send(file=image, embed=embed)

    #----------------------Task and Listener----------------------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if payload.channel_id == 341936700366258177 and payload.member.bot is not True:
            if str(payload.emoji) == "🚚":
                order_channel = self.bot.get_channel(341936700366258177)
                message = await order_channel.fetch_message(payload.message_id)
                message_data = message.embeds[0].to_dict()
                for x in message_data['fields']:
                    if x['name'] == 'Discord':
                        memberid = x['value']
                new_memberid = memberid.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                member = guild.get_member(int(new_memberid))
                embed = discord.Embed(title="Motorsport Notification", colour=discord.Colour(
                0xFF0000), description="Your brand new vehicle is on the way to our warehouse at Motorsports\nWe will notify you again when it is arrived.\nStay tuned! :smile:")
                embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
                embed.set_image(url="https://media1.tenor.com/images/cb936926d59302a4944281af827f8992/tenor.gif")
                async with self.membershipdb.member(member).Orders() as orders:
                    for x in orders:
                        if x['msg_id'] == payload.message_id:
                            x['Status'] = "Shipping"
                try:
                    await member.send(embed=embed)
                    await order_channel.send(content="Shipping notification has been sent to {}".format(member.mention))
                except discord.errors.Forbidden:
                    await order_channel.send("**[Warning]** {} turned off his PM".format(member.mention))
            if str(payload.emoji) == "✅":
                order_channel = self.bot.get_channel(341936700366258177)
                message = await order_channel.fetch_message(payload.message_id)
                message_data = message.embeds[0].to_dict()
                for x in message_data['fields']:
                    if x['name'] == 'Discord':
                        memberid = x['value']
                new_memberid = memberid.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                member = guild.get_member(int(new_memberid))
                embed = discord.Embed(title="Motorsport Notification", colour=discord.Colour(
                0xFF0000), description="Your brand new vehicle is ready for collection at Motorsports, the dealership located next to Mors Insurance.\nEnjoy! :smile:")
                embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
                embed.set_image(url="https://i.imgur.com/NssiDxp.png")
                async with self.membershipdb.member(member).Orders() as orders:
                    for x in orders:
                        if x['msg_id'] == payload.message_id:
                            x['Status'] = "Completed"
                try:
                    await member.send(embed=embed)
                    await order_channel.send(content="Order complete notification has been sent to {}".format(member.mention))
                except discord.errors.Forbidden:
                    await order_channel.send("**[Warning]** {} turned off his PM".format(member.mention))
            elif str(payload.emoji) == "🤝":
                order_channel = self.bot.get_channel(341936700366258177)
                customer_role = guild.get_role(343722834016862211)
                message = await order_channel.fetch_message(payload.message_id)
                message_data = message.embeds[0].to_dict()
                for x in message_data['fields']:
                    if x['name'] == 'Discord':
                        memberid = x['value']
                new_memberid = memberid.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                member = guild.get_member(int(new_memberid))
                await member.add_roles(customer_role)
                embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF00FF), description="Dear {},\n\nThank you for shopping at Premium Deluxe Motorsport, we would truly appreciate if you could spare some time to send us a picture of the vehicle you purchased with a small comment in our <#343722557381279745> channel.\n\nWe hope that your purchasing experience here was satisfactory, and a huge thanks to you for supporting Motorsports.\nHave a wonderful day & enjoy your new vehicle!".format(member.display_name))
                embed.set_thumbnail(url='https://i.imgur.com/xJyIgAQ.png')
                await self.membershipdb.member(member).Customer_Status.set(True)
                try:
                    await member.send(embed=embed)
                    await order_channel.send(content="Customer rank notification has been sent to {}".format(member.mention))
                except discord.errors.Forbidden:
                    await order_channel.send("**[Warning]** {} turned off his PM".format(member.mention))
            elif str(payload.emoji) == "💎":
                order_channel = self.bot.get_channel(341936700366258177)
                VIP_role = guild.get_role(345786815959007234)
                message = await order_channel.fetch_message(payload.message_id)
                message_data = message.embeds[0].to_dict()
                for x in message_data['fields']:
                    if x['name'] == 'Discord':
                        memberid = x['value']
                new_memberid = memberid.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                member = guild.get_member(int(new_memberid))
                await member.add_roles(VIP_role)
                embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF0000), description="Dear {},\n\nBecause of your continuous support here at Motorsports, we are pleased to inform you that you are now a VIP customer! View our <#345600420883988481> channel for more details, take note that you are now entitled to VIP discounts!\nHave a fantastic day & enjoy your new perks!".format(member.display_name))
                embed.set_thumbnail(url="http://cdn.quotesgram.com/img/41/24/1219260287-icon_vip.png")
                await self.membershipdb.member(member).VIP_Status.set(True)
                try:
                    await member.send(embed=embed)
                    await order_channel.send(content="VIP rank notification has been sent to {}".format(member.mention))
                except discord.errors.Forbidden:
                    await order_channel.send("**[Warning]** {} turned off his PM".format(member.mention))
    
    @tasks.loop(seconds=300.0)
    async def update_vehicle(self):
        veh_price = await super().vehicle_price()
        stocks = await super().vehicle_stock()
        speed = await super().vehicle_speed()
        veh_price = await self.combinedata(veh_price, stocks, speed)
        await self.comparingstocks(veh_price)

    @update_vehicle.before_loop
    async def before_update_vehicle(self):
        print('waiting...')
        await self.bot.wait_until_ready()

class Membership(Database):
    """This class handles membership processing"""
    
    def __init__(self, ctx, timeout, mode):
        self.cardlist = {
            "Customers": "Customers",
            "Weazel News Partner": "Partner_Client",
            "Los Santos Custom Partner": "Partner_Client",
            "VIP": "VIP",
            "Partners": "Partners",
            "Graphic Designer": "Designer",
            "Founders": "Founders",
            "Assistant": "Assistant",
            "Assistant Manager": "Management",
            "Manager": "Management",
            "Bot-Developer": "Developer",
            "Co-Owner": "Co-Owner",
            "Owner": "Owner",
        }
        super().__init__()
                
    
    async def create_card(self, ctx, author, name: str, date):
        MemberRanks = [x.name for x in author.roles]
        finalrank = [x for x in MemberRanks if x in self.cardlist.keys()]
        card_loc = "template/{}.png".format(self.cardlist[finalrank[-1]])
        img_loc = str(bundled_data_path(self) / card_loc)
        img = Image.open(img_loc)
        draw = ImageDraw.Draw(img)
        font_loc = str(bundled_data_path(self) / "template/BebasNeue.TTF")
        font = ImageFont.truetype(font_loc, 24)
        msg = name
        draw.text((650, 183), msg, (44, 44, 44), font=font)
        msg = author.top_role.name
        draw.text((651, 253), msg, (44, 44, 44), font=font)
        msg = date
        draw.text((650, 323), msg, (44, 44, 44), font=font)
        filename = "users/" + str(author.id) + ".png"
        img.save(str(bundled_data_path(self) / filename))
        image = discord.File(str(bundled_data_path(self) / filename))
        return image