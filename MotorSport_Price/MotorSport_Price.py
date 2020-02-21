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

gc = pygsheets.authorize(service_file='../client_secret.json')


class MOTORSPORT_PRICE(commands.Cog):
    """Its all about Motorsport - Price System"""

    def __init__(self, bot):
        self.bot = bot
        self.check_prices.start()
        self.database = Config.get_conf(self, identifier=1)
        data = {"Prices": []}
        self.database.register_guild(**data)
    
    def cog_unload(self):
        self.check_prices.cancel()

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def price(self, ctx, *, car_name: str):
        """Used to search price"""

        prices = await self.database.guild(ctx.guild).Prices()
        car_list = [d['Vehicle Name'] for d in prices]
        car_name_matched = process.extractBests(car_name, car_list, score_cutoff=80, limit=2)
        not_matched = False
        multiple_match = False
        if str(car_name_matched) == '[]':
            not_matched = True
        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
            multiple_match = True
        if not_matched == False and multiple_match != True:
            for price in prices:
                if price["Vehicle Name"] == car_name_matched[0][0]:
                    embed = discord.Embed(title=price['Vehicle Name'], colour=discord.Colour(0x984c87), description=price['Types'])
                    embed.set_image(url=price['Vehicle Image'])
                    embed.set_thumbnail(url=price['Brand Image'])
                    embed.add_field(name="Brand:", value=price['Brand'], inline=True)
                    embed.add_field(name="Price:", value=price['Price'], inline=True)
                    embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                    embed2 = discord.Embed(colour=discord.Colour(0x984c87))
                    embed2.set_image(url=price['Performance Image'])
                    embed2.add_field(name="Capacity:", value=price['Capacity'], inline=True)
                    embed2.add_field(name="Drive:", value=price['Drive'], inline=True)
                    await ctx.send(embed=embed)
                    await ctx.send(embed=embed2)
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
    @commands.guild_only()
    async def vprice(self, ctx, *, car_name: str):

        """Used to search VIP price"""
        prices = await self.database.guild(ctx.guild).Prices()
        car_list = [d['Vehicle Name'] for d in prices]
        car_name_matched = process.extractBests(car_name, car_list, score_cutoff=80, limit=2)
        not_matched = False
        multiple_match = False
        if str(car_name_matched) == '[]':
            not_matched = True
        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
            multiple_match = True
        if not_matched == False and multiple_match != True:
            for price in prices:
                if price["Vehicle Name"] == car_name_matched[0][0]:
                    embed = discord.Embed(title=price['Vehicle Name'], colour=discord.Colour(0x984c87), description=price['Types'])
                    embed.set_image(url=price['Vehicle Image'])
                    embed.set_thumbnail(url=price['Brand Image'])
                    embed.add_field(name="Brand:", value=price['Brand'], inline=True)
                    embed.add_field(name="VIP Price:", value=price['VIP Price'], inline=True)
                    embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                    embed2 = discord.Embed(colour=discord.Colour(0x984c87))
                    embed2.set_image(url=price['Performance Image'])
                    embed2.add_field(name="Capacity:", value=price['Capacity'], inline=True)
                    embed2.add_field(name="Drive:", value=price['Drive'], inline=True)
                    await ctx.send(embed=embed)
                    await ctx.send(embed=embed2)
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
    @commands.guild_only()
    @commands.has_any_role("Owner", "Bot-Developer", "Bot-Admin")
    async def updateprice(self, ctx):

        status_message = "Updating vehicle Price\n"
        loadingbar = "**▒▒▒▒▒▒▒▒▒▒ (0%)**"
        the_msg = status_message + loadingbar
        msg = await ctx.send(the_msg)
        
        status_message = "Accessing **Motorsports Sales**\n"
        loadingbar = "**▒▒▒▒▒▒▒▒▒▒ (0%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        sh = gc.open_by_key('12gmECNatiWtDeGt5Oc3Zw7_CVP8kXxdwW50nqQ_Gfzg')
        
        status_message = "Opening **Bot Data Sheet**\n"
        loadingbar = "**▒▒▒▒▒▒▒▒▒▒ (0%)**"
        await msg.edit(content=the_msg)
        wks = sh.worksheet_by_title('Bot Data Sheet')
        
        status_message = "Getting **Vehicle Name**\n"
        loadingbar = "**█▒▒▒▒▒▒▒▒▒ (10%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        vehicle_name = wks.get_col(1)
        
        status_message = "Getting **Vehicle Price**\n"
        loadingbar = "**██▒▒▒▒▒▒▒▒ (20%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        price = wks.get_col(2)
        
        status_message = "Getting **Vehicle Types**\n"
        loadingbar = "**███▒▒▒▒▒▒▒ (30%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        types = wks.get_col(3)
        
        status_message = "Getting **Vehicle Brand**\n"
        loadingbar = "**████▒▒▒▒▒▒ (40%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        brand = wks.get_col(4)
        
        status_message = "Getting **Vehicle Capacity**\n"
        loadingbar = "**█████▒▒▒▒▒ (50%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        capacity = wks.get_col(5)
        
        status_message = "Getting **Vehicle Drive**\n"
        loadingbar = "**██████▒▒▒▒ (60%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        drive = wks.get_col(6)
        
        status_message = "Getting **Vehicle Images**\n"
        loadingbar = "**███████▒▒▒ (70%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        vehicle_image = wks.get_col(7)
        
        status_message = "Getting **Vehicle Brand Images**\n"
        loadingbar = "**████████▒▒ (80%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        brand_image = wks.get_col(8)
        
        status_message = "Getting **Vehicle Performance Images**\n"
        loadingbar = "**█████████▒ (90%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        performance_image = wks.get_col(9)
        
        status_message = "Getting **VIP Price**\n"
        loadingbar = "**██████████ (100%)**"
        the_msg = status_message + loadingbar
        await msg.edit(content=the_msg)
        vip_price = wks.get_col(10)
        
        result = []
        for i in range(len(list(vehicle_name))):
            result.append({"Vehicle Name": vehicle_name[i], "Price": price[i], "Types": types[i], "Brand": brand[i], "Capacity": capacity[i], "Drive": drive[i], "Vehicle Image": vehicle_image[i], "Brand Image": brand_image[i], "Performance Image": performance_image[i], "VIP Price": vip_price[i]})
        await self.database.guild(ctx.guild).Prices.set(result)

        await msg.edit(content="**The vehicle price has been updated**")
    
    @tasks.loop(seconds=300.0)
    async def check_prices(self):
        print("Updating Price")
        guild_id = self.bot.get_guild(341928926098096138)
        sh = gc.open_by_key('12gmECNatiWtDeGt5Oc3Zw7_CVP8kXxdwW50nqQ_Gfzg')
        wks = sh.worksheet_by_title('Bot Data Sheet')
        vehicle_name = wks.get_col(1)
        price = wks.get_col(2)
        types = wks.get_col(3)
        brand = wks.get_col(4)
        capacity = wks.get_col(5)
        drive = wks.get_col(6)
        vehicle_image = wks.get_col(7)
        brand_image = wks.get_col(8)
        performance_image = wks.get_col(9)
        vip_price = wks.get_col(10)
        result = []
        for i in range(len(list(vehicle_name))):
            result.append({"Vehicle Name": vehicle_name[i], "Price": price[i], "Types": types[i], "Brand": brand[i], "Capacity": capacity[i], "Drive": drive[i], "Vehicle Image": vehicle_image[i], "Brand Image": brand_image[i], "Performance Image": performance_image[i], "VIP Price": vip_price[i]})
        await self.database.guild(guild_id).Prices.set(result)
        print("Updated Price")
    
    @check_prices.before_loop
    async def before_check_prices(self):
        print('waiting...')
        await self.bot.wait_until_ready()
