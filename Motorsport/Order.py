from discord.ext import tasks
from redbot.core import Config
import discord
import os
import asyncio
from discord.ext import commands
import json
from fuzzywuzzy import process
from redbot.core import commands
import random
from .Database import Database

class Order(Database):
    """Motorsport Order System"""
    def __init__(self):
        super().__init__()

    async def wait_for_answer(self, ctx, ordering_channel):
        msg = None
        while msg is None:

            def check(m: discord.Message):
                return m.author == ctx.author and m.channel.id == ordering_channel.id

            try:
                msg = await ctx.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await ordering_channel.send("Timeout! Please type !order to place order again")
                break
            if msg.content == 'exit':
                msg = None
                break                
        return msg

    async def order(self, ctx, car_name, ordering_channel):
        while True:
            guild = ctx.guild
            author = ctx.author
            order_channel = ctx.bot.get_channel(341936700366258177)
            if ordering_channel is None:
                guild = ctx.guild
                overwrites = {
                    author: discord.PermissionOverwrite(read_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    guild.default_role: discord.PermissionOverwrite(read_messages=False)
                }
                ordering_channel = await guild.create_text_channel('Ordering-{}'.format(random.randint(1,9999)),overwrites=overwrites)
            if any(r.name == 'VIP' for r in author.roles):
                info_embed = await ordering_channel.send("""Hi {}, Welcome to Premium Deluxe Motorsport **VIP** Ordering System""".format(author.mention))
                VIP = True
            else:
                info_embed = await ordering_channel.send("""Hi {}, Welcome to Premium Deluxe Motorsport Ordering System""".format(author.mention))
                VIP = False
                
            qembed = discord.Embed(colour=discord.Colour(0x984c87))
            qembed.set_author(name="""What is your First and Last name? (Character Name)""")
            question_embed = await ordering_channel.send(embed=qembed)
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                await ordering_channel.delete()
                return
            customer_name = msg.content
            await msg.delete()

            embed = discord.Embed(colour=discord.Colour(0x984c87))
            embed.set_thumbnail(url="http://www.buygosleep.com/wp-content/uploads/2016/01/Car-Icon.png")
            embed.set_author(name="""Motorsport Order Sheet""")
            embed.add_field(name="Customer Name", value=customer_name, inline=False)
            qembed = question_embed.embeds[0]
            qembed.set_author(name="""What is your phone number? (If you do not have your  phone, type 'None')""")
            await info_embed.edit(content="", embed=embed)
            await question_embed.edit(embed=qembed)
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                await ordering_channel.delete()
                return
            contact_number = msg.content
            await msg.delete()

            embed = info_embed.embeds[0]
            qembed = question_embed.embeds[0]
            embed.add_field(name="Contact Number", value=contact_number, inline=True)
            qembed.set_author(name="""Do you preferred to be contacted by Phone (In-game) or Email (Discord)?""")
            await info_embed.edit(embed=embed)
            await question_embed.edit(embed=qembed)
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                await ordering_channel.delete()
                return
            contact_method = msg.content
            await msg.delete()
            
            embed = info_embed.embeds[0]
            qembed = question_embed.embeds[0]
            embed.add_field(name="Contact", value=contact_method, inline=True)
            qembed.set_author(name="""Any questions and comments?""")
            await info_embed.edit(embed=embed)
            await question_embed.edit(embed=qembed)
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                await ordering_channel.delete()
                return
            customer_remarks = msg.content
            await msg.delete()

            embed = info_embed.embeds[0]
            qembed = question_embed.embeds[0]
            embed.add_field(name="Remarks", value=customer_remarks, inline=True)
            qembed.set_author(name="""What is the vehicle name?""")
            await info_embed.edit(embed=embed)
            await question_embed.edit(embed=qembed)
            selected_veh = None
            while selected_veh is None:    
                msg = await self.wait_for_answer(ctx, ordering_channel)
                if msg is None:
                    await asyncio.sleep(10.0)
                    await ordering_channel.delete()
                    return
                selected_veh, embed = await self.get_vehicle(ctx, car_name=msg.content)
                if selected_veh is None:
                    await msg.delete()
                    msg = await ordering_channel.send(embed=embed)
                    await msg.delete(delay=10.0)
                elif selected_veh['For_Sale'] == 'FALSE':
                    await msg.delete()
                    msg = await ordering_channel.send("Sorry! That vehicle is not for sell!")
                    selected_veh = None
                    await msg.delete(delay=5.0)
            await msg.delete()
            embed = info_embed.embeds[0]
            qembed = question_embed.embeds[0]
            embed.add_field(name="Vehicle Name", value="{} {}".format(selected_veh['Name'], "**[NOT FOR SALE]**" if selected_veh['For_Sale'] == 'FALSE' else ""), inline=False)
            embed.set_image(url=selected_veh['Vehicle Image'])
            embed.set_thumbnail(url=selected_veh['Brand Image'])
            embed.add_field(name="Brand", value=selected_veh['Brand'], inline=True)
            if VIP is True:
                embed.add_field(name="Price", value="$ {}".format(selected_veh['Price']['VIP']), inline=True)
            else:
                embed.add_field(name="Price", value="$ {}".format(selected_veh['Price']['Normal']), inline=True)
            embed.add_field(name="Vehicle Name", value=selected_veh['Name'], inline=False)
            
            qembed.set_author(name="Is this correct? (Yes/No)", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
            await info_embed.edit(embed=embed)
            await question_embed.edit(embed=qembed)
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                await ordering_channel.delete()
                return
            answer = msg.content
            await msg.delete()

            embed = info_embed.embeds[0]
            if answer.lower() == 'yes':
                if VIP is True:
                    embed2 = discord.Embed(colour=discord.Colour(0xFF0000))
                else:
                    embed2 = discord.Embed(colour=discord.Colour(0x7CFC00))
                embed2.set_thumbnail(url="http://www.buygosleep.com/wp-content/uploads/2016/01/Car-Icon.png")
                embed2.set_author(name=customer_name)
                embed2.set_footer(text="Posted by " + author.name + "#" + author.discriminator)
                embed2.add_field(name="Vehicle Name", value=selected_veh['Name'] + " ({})".format(selected_veh['Type']), inline=True)
                if VIP is True:
                    price = selected_veh['Price']['VIP']
                else:
                    price = selected_veh['Price']['Normal']
                embed2.add_field(name="Price", value="$ {}".format(price), inline=True)
                embed2.add_field(name="Preferred to be contacted by", value=contact_method, inline=True)
                embed2.add_field(name="Phone Number", value=contact_number, inline=True)
                embed2.add_field(name="Discord", value=author.mention, inline=True)
                embed2.add_field(name="Remarks", value=customer_remarks)
                if VIP == 1:
                    msg = await order_channel.send(content="@everyone, we have new order from **VIP** {}.".format(author.mention), embed=embed2)
                else:
                    msg = await order_channel.send(content="@everyone, we have new order from {}.".format(author.mention), embed=embed2)
                await msg.add_reaction("🚚")
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                await msg.add_reaction("🤝")
                await msg.add_reaction("💎")
                embed = discord.Embed(colour=discord.Colour(0x984c87), description="""Our sales team will contact you as soon as possible.""")
                embed.set_author(name="""Thank you for shopping with Premium Deluxe Motorsport""")
                embed.set_image(url='https://media1.tenor.com/images/22919ad969d4fcf8280c47f4c4d6a643/tenor.gif')
                await info_embed.delete()
                await question_embed.delete()
                async with self.membershipdb.member(author).Orders() as orders:
                    orders.append({"msg_id": msg.id, "Name": selected_veh['Name'], "Price": price, "Status": "Processing"})
                await ordering_channel.send(embed=embed)
                finished_order = True
                break
            else:
                await info_embed.delete()
                await question_embed.delete()
        return customer_name, ordering_channel, finished_order
        
                