import os
import asyncio
import datetime

# PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# discord
import discord
from discord.ext import commands

# redbot
from redbot.core import commands
from redbot.core import Config
from redbot.core import utils
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path

class Membership:
    """Its all about Motorsport - Customer Systems"""

    def __init__(self):
        self.membershipdb = Config.get_conf(self, identifier=2)
        data = {"Name": "", "MemberID": "", "Orders": [], "Spent": 0, "Joined_Date": ""}
        self.membershipdb.register_member(**data)
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

    # [p]membership register
    # @membership.command(pass_context=True)
    # async def register(self, ctx, *, name: str):
    #     """Register an account with Motorsport

    #     Usage: !register <name>
    #     Example: !register Jasper Akerman
    #     """
    #     author = ctx.author
    #     guild = ctx.guild
    #     membershipinfo = await self.database.member(author).get_raw()
    #     if membershipinfo["Name"] == "":
    #         await self.database.member(author).Name.set(name)
    #         await self.database.member(author).MemberID.set(author.id)
    #         await self.database.member(author).Joined_Date.set(
    #             str(datetime.datetime.now().strftime("%d/%m/%y"))
    #         )
    #         shopper_role = ctx.guild.get_role(482965019189968927)
    #         await author.add_roles(shopper_role)

    #         embed = discord.Embed(
    #             title="Motorsport Management",
    #             colour=author.top_role.colour,
    #             description="Dear {},\n\nThank you for registering a membership with us at Premium Deluxe Motorsport!".format(
    #                 name
    #             ),
    #         )
    #         embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
    #         MemberRanks = [x.name for x in author.roles]
    #         finalrank = [x for x in MemberRanks if x in self.cardlist.keys()]
    #         card_loc = "template/{}.png".format(self.cardlist[finalrank[-1]])
    #         img_loc = str(bundled_data_path(self) / card_loc)
    #         img = Image.open(img_loc)
    #         draw = ImageDraw.Draw(img)
    #         font_loc = str(bundled_data_path(self) / "template/BebasNeue.ttf")
    #         font = ImageFont.truetype(font_loc, 24)
    #         msg = name
    #         draw.text((650, 183), msg, (44, 44, 44), font=font)
    #         msg = author.top_role.name
    #         draw.text((651, 253), msg, (44, 44, 44), font=font)
    #         msg = str(datetime.datetime.now().strftime("%d/%m/%y"))
    #         draw.text((650, 323), msg, (44, 44, 44), font=font)
    #         filename = "users/" + str(author.id) + ".png"
    #         img.save(str(bundled_data_path(self) / filename))
    #         image = discord.File(str(bundled_data_path(self) / filename))
    #         embed.set_image(url="attachment://" + str(author.id) + ".png")
    #         await ctx.send(file=image, embed=embed)
    #     else:
    #         await ctx.send("You are already registered!")

    # # [p]membership unregister
    # @membership.command(pass_context=True)
    # async def unregister(self, ctx, user_id=None):
    #     """Unregister an account from Motorsport

    #     Usage: !unregister
    #     """
    #     if user_id is not None:
    #         if "Administrator" in [x.name for x in ctx.author.roles]:
    #             author = await ctx.guild.fetch_member(int(user_id))
    #         else:
    #             author = ctx.author
    #     else:
    #         author = ctx.author

    #     def check(m):
    #         return m.channel == ctx.channel and m.author == ctx.author

    #     try:
    #         await ctx.send(
    #             "Are you sure you want to unregister? All data will be ereased. (Yes/No)"
    #         )
    #         answer = await self.bot.wait_for("message", check=check, timeout=120)
    #         if answer.content.lower() == "yes":
    #             await self.database.member(author).clear()
    #             await ctx.send("You have unregistered your membership here.")
    #         else:
    #             await ctx.send("Nothing has been done.")
    #     except asyncio.TimeoutError:
    #         await ctx.send("You did not answer in time.")

    # # [p]membership orders
    # @membership.command(pass_context=True)
    # async def orders(self, ctx, user_id=None):
    #     """Check orders history with Motorsport
    #     """
    #     if user_id is not None:
    #         if "Bot-Developer" in [x.name for x in ctx.author.roles]:
    #             author = await ctx.guild.fetch_member(int(user_id))
    #         else:
    #             author = ctx.author
    #     else:
    #         author = ctx.author
    #     membershipinfo = await self.database.member(author).get_raw()
    #     shipping = ""
    #     collection = ""
    #     completed = ""
    #     try:
    #         if membershipinfo["Name"] != "":
    #             embed = discord.Embed(
    #                 title="Motorsport Orders", colour=author.top_role.colour
    #             )
    #             embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
    #             embed.set_author(
    #                 name=membershipinfo["Name"], icon_url=author.avatar_url
    #             )
    #             try:
    #                 for x in membershipinfo["Orders"]:
    #                     if x["Status"] == "Shipping":
    #                         shipping = shipping + "- {} (Order ID: {})\n".format(
    #                             x["Vehicle_Name"], x["Order_ID"]
    #                         )
    #                     if x["Status"] == "Completed":
    #                         collection = collection + "- {} (Order ID: {})\n".format(
    #                             x["Vehicle_Name"], x["Order_ID"]
    #                         )
    #                     if x["Status"] == "Completed":
    #                         completed = completed + "- {} (Order ID: {})\n".format(
    #                             x["Vehicle_Name"], x["Order_ID"]
    #                         )
    #                 shipping = utils.chat_formatting.pagify(
    #                     shipping, delims="\n", page_length=1000
    #                 )
    #                 collection = utils.chat_formatting.pagify(
    #                     collection, delims="\n", page_length=1000
    #                 )
    #                 completed = utils.chat_formatting.pagify(
    #                     completed, delims="\n", page_length=1000
    #                 )
    #                 for num, x in enumerate(shipping, 1):
    #                     x = "```diff\n" + x + "```"
    #                     embed.add_field(
    #                         name="Shipping ({})".format(num), value=x, inline=False
    #                     )
    #                 for num, x in enumerate(collection, 1):
    #                     x = "```diff\n" + x + "```"
    #                     embed.add_field(
    #                         name="Completed ({})".format(num), value=x, inline=False
    #                     )
    #                 for num, x in enumerate(completed, 1):
    #                     x = "```diff\n" + x + "```"
    #                     embed.add_field(
    #                         name="Completed ({})".format(num), value=x, inline=True
    #                     )
    #                 await ctx.send(embed=embed)
    #             except:
    #                 embed.add_field(name="", value="No history", inline=False)
    #         else:
    #             await ctx.send(
    #                 "Please register by using !membership register or start ordering with !order"
    #             )
    #     except:
    #         pass

    # @membership.command(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def importall(self, ctx, user_id=None):
    #     """Import all data from #orders channel to users
    #     """
    #     guild = ctx.guild
    #     channel = self.bot.get_channel(341936700366258177)
    #     message = await channel.history(limit=3000).flatten()
    #     counter = 0
    #     for x in message:
    #         try:
    #             message_data = x.embeds[0].to_dict()
    #             for y in message_data["fields"]:
    #                 if y["name"] == "Discord":
    #                     memberid = y["value"]
    #                 if y["name"] == "Vehicle Name":
    #                     car_name = y["value"]
    #                 if y["name"] == "Price":
    #                     price = y["value"].replace("$ ", "").replace(",", "")
    #                     price = int(float(price))
    #             new_memberid = (
    #                 memberid.replace("<", "")
    #                 .replace(">", "")
    #                 .replace("@", "")
    #                 .replace("!", "")
    #             )
    #             if user_id is not None:
    #                 if new_memberid == user_id:
    #                     member = guild.get_member(int(new_memberid))
    #                     spent = await self.database.member(member).Spent()
    #                     spent = spent + price
    #                     async with self.database.member(member).Orders() as orders:
    #                         orders.append(
    #                             {
    #                                 "Order_ID": x.id,
    #                                 "Vehicle_Name": car_name,
    #                                 "Price": price,
    #                                 "Status": "Completed",
    #                             }
    #                         )
    #                         counter = counter + 1
    #             else:
    #                 member = guild.get_member(int(new_memberid))
    #                 spent = await self.database.member(member).Spent()
    #                 spent = spent + price
    #                 async with self.database.member(member).Orders() as orders:
    #                     orders.append(
    #                         {
    #                             "Order_ID": x.id,
    #                             "Vehicle_Name": car_name,
    #                             "Price": price,
    #                             "Status": "Completed",
    #                         }
    #                     )
    #                     counter = counter + 1
    #         except:
    #             pass
    #     await ctx.send("Imported {}".format(counter))

    # @membership.command(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def clearorders(self, ctx, user_id=None):
    #     """Reset user's orders
    #     """
    #     guild = ctx.guild
    #     member = guild.get_member(int(user_id))
    #     await self.database.member(member).Orders.set([])
    #     await self.database.member(member).Spent.set(0)
    #     await ctx.send("Order history for {} has been cleared".format(member.mention))

    # @membership.command(pass_context=True)
    # @checks.is_owner()
    # async def resetall(self, ctx):
    #     """Reset membership database
    #     """
    #     await self.database.clear_all()
    #     await ctx.send("Cleared All")

    # @commands.group(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def membershipset(self, ctx):
    #     """Set user's data
    #     """
    #     pass

    # @membershipset.command(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def date(self, ctx, user_id: int, *, date: str):
    #     """Used to set user's registered date
    #     """
    #     author = await ctx.guild.fetch_member(user_id)
    #     await self.database.member(author).Joined_Date.set(date)
    #     await ctx.send(
    #         "The registered date for {} has been set to {}".format(author.mention, date)
    #     )
    #     MemberRanks = [x.name for x in author.roles]
    #     finalrank = [x for x in MemberRanks if x in self.cardlist.keys()]
    #     card_loc = "template/{}.png".format(self.cardlist[finalrank[-1]])
    #     img_loc = str(bundled_data_path(self) / card_loc)
    #     img = Image.open(img_loc)
    #     draw = ImageDraw.Draw(img)
    #     font_loc = str(bundled_data_path(self) / "template/BebasNeue.ttf")
    #     font = ImageFont.truetype(font_loc, 24)
    #     msg = str(await self.database.member(author).Name())
    #     draw.text((650, 183), msg, (44, 44, 44), font=font)
    #     msg = author.top_role.name
    #     draw.text((651, 253), msg, (44, 44, 44), font=font)
    #     msg = str(date)
    #     draw.text((650, 323), msg, (44, 44, 44), font=font)
    #     filename = "users/" + str(author.id) + ".png"
    #     img.save(str(bundled_data_path(self) / filename))

    # @membershipset.command(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def newcard(self, ctx, user_id: int):
    #     """Used to set user's registered date
    #     """
    #     author = await ctx.guild.fetch_member(user_id)
    #     MemberRanks = [x.name for x in author.roles]
    #     finalrank = [x for x in MemberRanks if x in self.cardlist.keys()]
    #     card_loc = "template/{}.png".format(self.cardlist[finalrank[-1]])
    #     img_loc = str(bundled_data_path(self) / card_loc)
    #     img = Image.open(img_loc)
    #     draw = ImageDraw.Draw(img)
    #     font_loc = str(bundled_data_path(self) / "template/BebasNeue.ttf")
    #     font = ImageFont.truetype(font_loc, 24)
    #     msg = str(await self.database.member(author).Name())
    #     draw.text((650, 183), msg, (44, 44, 44), font=font)
    #     msg = author.top_role.name
    #     draw.text((651, 253), msg, (44, 44, 44), font=font)
    #     msg = str(await self.database.member(author).Joined_Date())
    #     draw.text((650, 323), msg, (44, 44, 44), font=font)
    #     filename = "users/" + str(author.id) + ".png"
    #     img.save(str(bundled_data_path(self) / filename))
    #     image = discord.File(str(bundled_data_path(self) / filename))
    #     await ctx.send(file=image, content="This is the new card")

    # @membershipset.command(pass_context=True)
    # @commands.has_any_role("Administrator")
    # async def name(self, ctx, user_id: int, *, name: str):
    #     """Used to set user's name
    #     """
    #     author = await ctx.guild.fetch_member(user_id)
    #     await self.database.member(author).Name.set(name)
    #     await ctx.send(
    #         "The name for {} has been set to {}".format(author.mention, name)
    #     )
    #     MemberRanks = [x.name for x in author.roles]
    #     finalrank = [x for x in MemberRanks if x in self.cardlist.keys()]
    #     card_loc = "template/{}.png".format(self.cardlist[finalrank[-1]])
    #     img_loc = str(bundled_data_path(self) / card_loc)
    #     img = Image.open(img_loc)
    #     draw = ImageDraw.Draw(img)
    #     font_loc = str(bundled_data_path(self) / "template/BebasNeue.ttf")
    #     font = ImageFont.truetype(font_loc, 24)
    #     msg = name
    #     draw.text((650, 183), msg, (44, 44, 44), font=font)
    #     msg = author.top_role.name
    #     draw.text((651, 253), msg, (44, 44, 44), font=font)
    #     msg = str(await self.database.member(author).Joined_Date())
    #     draw.text((650, 323), msg, (44, 44, 44), font=font)
    #     filename = "users/" + str(author.id) + ".png"
    #     img.save(str(bundled_data_path(self) / filename))

    # @commands.command(pass_context=True)
    # async def cancelorder(self, ctx, Order_ID: int):
    #     async with self.database.member(ctx.author).Orders() as orders:
    #         try:
    #             if Order_ID in orders[0].values():
    #                 order_channel = self.bot.get_channel(341936700366258177)
    #                 message = await order_channel.fetch_message(Order_ID)
    #                 message_data = message.embeds[0].to_dict()
    #                 message.embeds[0].set_author(
    #                     name="~~"
    #                     + message_data["author"]["name"]
    #                     + "~~"
    #                     + " **(Cancelled)**",
    #                     icon_url=message_data["author"]["icon_url"],
    #                 )
    #                 orders[:] = [d for d in orders if d.get("Order_ID") != Order_ID]
    #                 try:
    #                     await message.edit(embed=message.embeds[0])
    #                     await message.clear_reactions()
    #                 except discord.errors.Forbidden:
    #                     pass
    #                 await ctx.send("Order #{} has been cancelled".format(Order_ID))
    #             else:
    #                 await ctx.send("Order #{} not found".format(Order_ID))
    #         except IndexError:
    #             await ctx.send("You have not placed any order yet")

    # @commands.command(pass_context=True, no_pm=True)
    # @commands.has_permissions(manage_roles=True)
    # async def givecustomer(self, ctx, user: discord.Member):

    #     """Used to give Customer to players"""
    #     author = ctx.message.author
    #     management = self.bot.get_channel(341936003029794826)
    #     customer_role = ctx.guild.get_role(343722834016862211)
    #     await user.add_roles(customer_role)
    #     embed = discord.Embed(
    #         title="Motorsport Management",
    #         colour=discord.Colour(0xFF00FF),
    #         description="Dear {},\n\nThank you for shopping at Premium Deluxe Motorsport, we would truly appreciate if you could spare some time to send us a picture of the vehicle you purchased with a small comment in our <#343722557381279745> channel.\n\nWe hope that your purchasing experience here was satisfactory, and a huge thanks to you for supporting Motorsports.\nHave a wonderful day & enjoy your new vehicle!".format(
    #             user.display_name
    #         ),
    #     )
    #     embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
    #     await self.database.member(user).Customer_Status.set(True)
    #     try:
    #         await user.send(embed=embed)
    #     except discord.errors.Forbidden:
    #         await management.send(
    #             content="**[Warning]** {} turned off his PM".format(user.mention)
    #         )
    #     await management.send(
    #         content="{} uses command !givecustomer to give {} {} role".format(
    #             author.mention, user.mention, customer_role.mention
    #         )
    #     )

    # @commands.command(pass_context=True, no_pm=True)
    # @commands.has_permissions(manage_roles=True)
    # async def givevip(self, ctx, user: discord.Member):

    #     """Used to give VIP to players"""
    #     author = ctx.message.author
    #     management = self.bot.get_channel(341936003029794826)
    #     VIP_role = ctx.guild.get_role(345786815959007234)
    #     await user.add_roles(VIP_role)
    #     embed = discord.Embed(
    #         title="Motorsport Management",
    #         colour=discord.Colour(0xFF0000),
    #         description="Dear {},\n\nBecause of your continuous support here at Motorsports, we are pleased to inform you that you are now a VIP customer! View our <#345600420883988481> channel for more details, take note that you are now entitled to VIP discounts!\nHave a fantastic day & enjoy your new perks!".format(
    #             user.display_name
    #         ),
    #     )
    #     embed.set_thumbnail(
    #         url="http://cdn.quotesgram.com/img/41/24/1219260287-icon_vip.png"
    #     )
    #     await self.database.member(user).VIP_Status.set(True)
    #     try:
    #         await user.send(embed=embed)
    #     except discord.errors.Forbidden:
    #         await management.send(
    #             content="**[Warning]** {} turned off his PM".format(user.mention)
    #         )
    #     await management.send(
    #         content="{} uses command !givevip to give {} {} role".format(
    #             author.mention, user.mention, VIP_role.mention
    #         )
    #     )

    # @commands.command(pass_context=True, no_pm=True)
    # @commands.has_permissions(manage_roles=True)
    # async def done(self, ctx, user: discord.Member):

    #     """Used to notify about stock ready to player"""
    #     embed = discord.Embed(
    #         title="Motorsport Notification",
    #         colour=discord.Colour(0xFF0000),
    #         description="Your brand new vehicle is ready for collection at Motorsports, the dealership located next to Mors Insurance.\nEnjoy! :smile:",
    #     )
    #     embed.set_thumbnail(url="https://i.imgur.com/xJyIgAQ.png")
    #     embed.set_image(url="https://i.imgur.com/NssiDxp.png")
    #     try:
    #         await user.send(embed=embed)
    #     except discord.errors.Forbidden:
    #         await ctx.send("**[Warning]** {} turned off his PM".format(user.mention))
