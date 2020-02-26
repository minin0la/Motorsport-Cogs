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

class Order:
    """Motorsport Order System"""

    def __init__(self):
        super().__init__

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
    
    async def get_price(self, ctx, car_name, database, ordering_channel):
        pages = []
        prices = await database.guild(ctx.guild).Vehicles()
        car_list = [d['Name'] for d in prices]
        selected_veh = None
        multiple_match_msg = None
        while selected_veh is None:
            msg = await self.wait_for_answer(ctx, ordering_channel)
            if msg is None:
                selected_veh = None
                break
            car_name = msg.content
            if multiple_match_msg is not None:
                await multiple_match_msg.delete()
            car_name_matched = process.extractBests(car_name, car_list, score_cutoff=80, limit=2)
            not_matched = False
            multiple_match = False
            if str(car_name_matched) == '[]':
                not_matched = True
            if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
                multiple_match = True
            if not_matched == False and multiple_match != True:
                for price in prices:
                    if price["Name"] == car_name_matched[0][0]:
                        selected_veh = price
            else:
                if multiple_match != True:
                    thesimilarresult = "__**Did you mean?**__\n"
                    car_name_matched = process.extract(car_name, car_list, limit=5)
                    if car_name_matched[0][0] != "Vehicle Name":
                        for i in range(len(list(car_name_matched))):
                            thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                        embed = discord.Embed(colour=discord.Colour(0x984c87), description='```{}```'.format(thesimilarresult))
                        embed.set_author(name="""Vehicle not found\nTry to provide more details on your search\n\n""", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                        await msg.delete()
                        multiple_match_msg = await ordering_channel.send(embed=embed)
                    else:
                        embed = discord.Embed(colour=discord.Colour(0x984c87))
                        embed.set_author(name="""Vehicle not found\nTry to provide more details on your search\n\n""", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                        await msg.delete()
                        multiple_match_msg = await ordering_channel.send(embed=embed)
                else:
                    embed = discord.Embed(colour=discord.Colour(0x984c87), description='```{} ({}%)\n{} ({}%)```'.format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))
                    embed.set_author(name="""I have matched more than one result.""", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                    await msg.delete()
                    multiple_match_msg = await ordering_channel.send(embed=embed)
        return selected_veh, msg
    
    async def updateembed(self, ctx, msg):
        sd

    async def order(self, ctx, car_name, database, ordering_channel):
        guild = ctx.guild
        author = ctx.author
        order_channel = ctx.bot.get_channel(341936700366258177)
        if ordering_channel is None:
            guild = ctx.guild
            overwrites = {
                guild.me: discord.PermissionOverwrite(read_messages=True),
                guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
            ordering_channel = await guild.create_text_channel('Ordering-{}'.format(random.randint(1,9999)),overwrites=overwrites)
        if any(r.name == 'VIP' for r in author.roles):
            welcome_msg = await ordering_channel.send("""Hi {}, Welcome to Premium Deluxe Motorsport **VIP** Ordering System""".format(author.mention))
            VIP = True
        else:
            welcome_msg = await ordering_channel.send("""Hi {}, Welcome to Premium Deluxe Motorsport Ordering System""".format(author.mention))
            VIP = False
        embed = discord.Embed(colour=discord.Colour(0x984c87))
        embed.set_thumbnail(url="http://www.buygosleep.com/wp-content/uploads/2016/01/Car-Icon.png")
        embed.set_author(name="""What is your First and Last name? (Character Name)""", icon_url=author.avatar_url)
        info_embed = await ordering_channel.send(embed=embed)
        msg = await self.wait_for_answer(ctx, ordering_channel)
        if msg is None:
            await ordering_channel.delete()
            return
        customer_name = msg.content
        await msg.delete()
        embed = info_embed.embeds[0]
        embed.add_field(name="Customer Name", value=customer_name, inline=False)
        
        embed.set_author(name="""What is your phone number? (If you do not have your  phone, type 'None')""", icon_url=author.avatar_url)
        await info_embed.edit(embed=embed)
        msg = await self.wait_for_answer(ctx, ordering_channel)
        if msg is None:
            await ordering_channel.delete()
            return
        contact_number = msg.content
        await msg.delete()
        embed = info_embed.embeds[0]
        embed.add_field(name="Contact Number", value=contact_number, inline=True)
        
        embed.set_author(name="""Do you preferred to be contacted by Phone (In-game) or Email (Discord)?""", icon_url=author.avatar_url)
        await info_embed.edit(embed=embed)
        msg = await self.wait_for_answer(ctx, ordering_channel)
        if msg is None:
            await ordering_channel.delete()
            return
        contact_method = msg.content
        await msg.delete()
        embed = info_embed.embeds[0]
        embed.add_field(name="Contact", value=contact_method, inline=True)
        
        embed.set_author(name="""Any questions and comments?""", icon_url=author.avatar_url)
        await info_embed.edit(embed=embed)
        msg = await self.wait_for_answer(ctx, ordering_channel)
        if msg is None:
            await ordering_channel.delete()
            return
        customer_remarks = msg.content
        await msg.delete()
        embed = info_embed.embeds[0]
        embed.add_field(name="Remarks", value=customer_remarks, inline=True)

        embed.set_author(name="""What is the vehicle name?""", icon_url=author.avatar_url)
        await info_embed.edit(embed=embed)
        selected_veh, msg = await self.get_price(ctx, car_name=car_name, database=database, ordering_channel=ordering_channel)
        if selected_veh is None:
            await ordering_channel.delete()
            return
        await msg.delete()
        embed = info_embed.embeds[0]
        embed.add_field(name="Vehicle Name", value="{} {}".format(selected_veh['Name'], "**[NOT FOR SALE]**" if selected_veh['For_Sale'] == 'FALSE' else ""), inline=False)
        embed.set_image(url=selected_veh['Vehicle Image'])
        embed.set_thumbnail(url=selected_veh['Brand Image'])
        embed.add_field(name="Brand", value=selected_veh['Brand'], inline=True)
        if VIP is True:
            embed.add_field(name="Price", value="$ {:,.2f}".format(selected_veh['Price']['VIP']), inline=True)
        else:
            embed.add_field(name="Price", value="$ {:,.2f}".format(selected_veh['Price']['Normal']), inline=True)
        embed.add_field(name="Vehicle Name", value=selected_veh['Name'], inline=False)
        
        embed.set_author(name="Is this correct? (Yes/No)", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
        await info_embed.edit(embed=embed)
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
            embed2.set_author(name=customer_name, icon_url=author.avatar_url)
            embed2.set_footer(text="Posted by " + author.name + "#" + author.discriminator)
            embed2.add_field(name="Vehicle Name", value=selected_veh['Name'] + " ({})".format(selected_veh['Type']), inline=True)
            if VIP is True:
                embed2.add_field(name="Price", value="$ {:,.2f}".format(selected_veh['Price']['VIP']), inline=True)
            else:
                embed2.add_field(name="Price", value="$ {:,.2f}".format(selected_veh['Price']['Normal']), inline=True)
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
            embed.set_author(name="""Thank you for shopping with Premium Deluxe Motorsport""", icon_url=author.avatar_url)
            embed.set_image(url='https://media1.tenor.com/images/22919ad969d4fcf8280c47f4c4d6a643/tenor.gif')
            await welcome_msg.delete()
            await info_embed.delete()
            await ordering_channel.send(embed=embed)
            await self.wait_for_answer(ctx, order_channel)
            await ordering_channel.delete()
        else:
            await welcome_msg.delete()
            await info_embed.delete()
            await self.order(ctx, car_name=None, database=database, ordering_channel=ordering_channel)
            
    
        
                