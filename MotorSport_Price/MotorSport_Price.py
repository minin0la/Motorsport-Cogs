import discord
import random
import pygsheets
from discord.ext import commands
import asyncio
from fuzzywuzzy import process
import os
from discord.ext import tasks
from redbot.core import Config
from redbot.core import commands
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from redbot.core import utils
# from MotorSport_Order import MOTORSPORT_ORDER


gc = pygsheets.authorize(service_file='client_secret.json')


class MOTORSPORT_PRICE(commands.Cog):
    """Its all about Motorsport - Price System"""

    def __init__(self, bot):
        self.bot = bot
        self.prices = Config.get_conf(None, identifier=1, cog_name='MOTORSPORT_DATABASE')
    
    

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def price(self, ctx, *, car_name: str):
        """Used to search price"""

        pages = []
        prices = await self.prices.guild(ctx.guild).Vehicles()
        car_list = [d['Name'] for d in prices]
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
                    embed = discord.Embed(title="{} {}".format(price['Name'], "**[NOT FOR SALE]**" if price['For_Sale'] == 'FALSE' else ""), colour=discord.Colour(0x984c87), description=price['Type'])
                    embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                    embed.set_image(url=price['Vehicle Image'])
                    embed.set_thumbnail(url=price['Brand Image'])
                    embed.add_field(name="Brand", value=price['Brand'], inline=True)
                    if ctx.channel.id == 343448488715223040:
                        embed.add_field(name="Price", value="$ {:,.2f}".format(price['Price']['Normal']), inline=True)
                    elif ctx.channel.id == 345788278131261442:
                        embed.add_field(name="VIP Price", value="$ {:,.2f}".format(price['Price']['VIP']), inline=True)
                    elif ctx.channel.category_id == 360808237802455041:
                        embed.add_field(name="Price", value="$ {:,.2f}".format(price['Price']['Normal']), inline=True)
                        embed.add_field(name="VIP Price", value="$ {:,.2f}".format(price['Price']['VIP']), inline=True)
                    if price['Stock'] is not None:
                        embed.add_field(name="Stock ({} Qty)".format(price['Stock']), value="$ {:,.2f}".format(price['Price']['Stock_Price']), inline=True)
                    
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
        else:
            if multiple_match != True:
                thesimilarresult = "__**Did you mean?**__\n"
                car_name_matched = process.extract(car_name, car_list, limit=5)
                if car_name_matched[0][0] != "Vehicle Name":
                    for i in range(len(list(car_name_matched))):
                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                    await ctx.send("""**Vehicle not found\nTry to provide more details on your search**\n\n""" + thesimilarresult)
                else:
                    await ctx.send("""**Vehicle not found\nTry to provide more details on your search**\n\n""")
            else:
                await ctx.send("""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))
    
    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.has_any_role("Owner","Administrator")
    @commands.guild_only()
    async def pricelist(self, ctx, *, class_name: str):
        """Used to search price"""
        await ctx.send("Printing")
        prices = await self.prices.guild(ctx.guild).Vehicles()
        for price in prices:
            if price["Type"] == class_name:
                embed = discord.Embed(title="{} {}".format(price['Name'], "**[NOT FOR SALE]**" if price['For_Sale'] == 'FALSE' else ""), colour=discord.Colour(0x984c87), description=price['Type'])
                embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                embed.set_image(url=price['Vehicle Image'])
                embed.set_thumbnail(url=price['Brand Image'])
                embed.add_field(name="Brand", value=price['Brand'], inline=True)
                embed.add_field(name="For Sale?", value=price['For_Sale'], inline=True)
                embed.add_field(name="Price", value="$ {:,.2f}".format(price['Price']['Normal']), inline=True)
                embed.add_field(name="Storage (Trunk)", value=price['Storage']['Trunk'], inline=True)
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
                await ctx.send(embed=embed)        
                await ctx.send(embed=embed2)