import requests
from discord.ext import tasks
from redbot.core import Config
from redbot.core import utils
import discord
import os
import asyncio
from discord.ext import commands
import json
from fuzzywuzzy import process
from redbot.core import commands

class MOTORSPORT_STOCK(commands.Cog):
    """Motorsport Stock System"""

    def __init__(self, bot):
        self.bot = bot
        self.database = Config.get_conf(self, identifier=1)
        data = {"Stocks": [],
                "OldStocks": [],
                "Token": "",
        }
        self.database.register_guild(**data)
        self.prices = Config.get_conf(None, identifier=1, cog_name='MOTORSPORT_PRICE')
        self.check_stock.start()
    
    def cog_unload(self):
        self.check_stock.cancel()

    # def is_not_channel(idlist):
    #     def predicate(ctx):
    #         if ctx.message.channel.id not in idlist:
    #             return True
    #         else:
    #             return False
    #     return commands.check(predicate)
    
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def stock(self, ctx, *, vehicle_name): 
        """
        Used to search in-stock vehicle
        """
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            car_list = [d['Name'] for d in stocks]
        car_name_matched = process.extractBests(vehicle_name, car_list, score_cutoff=80, limit=2)
        not_matched = False
        multiple_match = False
        if str(car_name_matched) == '[]':
            not_matched = True
        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
            multiple_match = True
        if not_matched == False and multiple_match != True:
            stocks = await self.database.guild(ctx.guild).Stocks()
            for stock in stocks:
                if stock['Name'] == car_name_matched[0][0]:
                    await ctx.send("I have found {} {} in-stock for ${:,d}".format(stock['Stock'], stock['Name'], stock['Price']))
        else:
            if multiple_match != True:
                thesimilarresult = "__**Other vehicles in-stock**__\n"
                # car_list_new = {n.lower(): n for n in car_list}
                # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 5, 0.5)]
                car_name_matched = process.extract(vehicle_name, car_list, limit=5)
                if car_name_matched[0][0] != "Vehicle Name":
                    for i in range(len(list(car_name_matched))):
                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + "\n"
                    await ctx.send("""**Vehicle not found.\nThe vehicle might not be in-stock. Place your order by `!order`**\n\n""" + thesimilarresult)
                else:
                    await ctx.send("""**Vehicle not found.\nThe vehicle might not be in-stock. Place your order by `!order`**\n\n""")
            else:
                await ctx.send("""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.default)
    async def allstock(self, ctx):
        stocks = await self.database.guild(ctx.guild).Stocks()
        classlist = [x['Class'] for x in stocks]
        classlist = list(dict.fromkeys(classlist))
        pages = []
        fieldnumber = 0
        embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF00FF))
        embed.set_thumbnail(url='https://i.imgur.com/xJyIgAQ.png')
        for x in classlist:
            message = ""
            for y in stocks:
                if y['Class'] == x:
                    message = message + "{} ({} Qty): ${:,d}\n".format(y['Name'], y['Stock'], y['Price'])
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

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def fstock(self, ctx, *, vehicle_name):
        """
        Used to search in-stock vehicle
        """
        msg = await ctx.send("Updating vehicle stocks")
        shipment_channel = self.bot.get_channel(667348336277323787)
        tokens = await self.database.guild(ctx.guild).Token()
        await self.database.guild(ctx.guild).Stocks.set([])
        try:
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': tokens
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        except:
            await msg.edit(content="Error: Invalid Token. Geting new token...")
            url = "https://api.eclipse-rp.net/auth/login"
            with open('../data.txt') as thefile:
                data = thefile.read()
                payload = str(data).replace("\n", "")
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
            }
            response = requests.request("POST", url, headers=headers, data = payload)
            result_token = response.json()['token']
            await self.database.guild(ctx.guild).Token.set(str(result_token))
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': str(result_token)
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            for x in data:
                if x['Name'] == 'Motorsport':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
                if x['Name'] == 'DownTownBoats':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
        stocks = await self.database.guild(ctx.guild).Stocks()
        sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
        await self.database.guild(ctx.guild).Stocks.set(sorted_stocks)
        oldstocks = await self.database.guild(ctx.guild).OldStocks()
        not_same = ''
        price_change = ''
        stock_change = ''
        newstock_change = ''
        all_change = ''
        soldout_change = ''
        for x in stocks:
            newstock = True
            for y in oldstocks:
                if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
                    all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
                    , y['Price'], x['Price'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
                    stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
                    price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
                    newstock = False
            if newstock is True:
                newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
        for x in oldstocks:
            if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
                soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
        try:
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            await shipment_channel.send(not_same)
        except:
            pass
        await self.database.guild(ctx.guild).OldStocks.set(sorted_stocks)
        await msg.edit(content="Stock has been updated.")
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            car_list = [d['Name'] for d in stocks]
        car_name_matched = process.extractBests(vehicle_name, car_list, score_cutoff=80, limit=2)
        not_matched = False
        multiple_match = False
        if str(car_name_matched) == '[]':
            not_matched = True
        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
            multiple_match = True
        if not_matched == False and multiple_match != True:
            stocks = await self.database.guild(ctx.guild).Stocks()
            for stock in stocks:
                if stock['Name'] == car_name_matched[0][0]:
                    await ctx.send("I have found {} {} in-stock for ${:,d}".format(stock['Stock'], stock['Name'], stock['Price']))
        else:
            if multiple_match != True:
                thesimilarresult = "__**Other vehicles in-stock**__\n"
                # car_list_new = {n.lower(): n for n in car_list}
                # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 5, 0.5)]
                car_name_matched = process.extract(vehicle_name, car_list, limit=5)
                if car_name_matched[0][0] != "Vehicle Name":
                    for i in range(len(list(car_name_matched))):
                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + "\n"
                    await ctx.send("""**Vehicle not found.\nThe vehicle might not be in-stock. Place your order by `!order`**\n\n""" + thesimilarresult)
                else:
                    await ctx.send("""**Vehicle not found.\nThe vehicle might not be in-stock. Place your order by `!order`**\n\n""")
            else:
                await ctx.send("""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def fallstock(self, ctx):
        msg = await ctx.send("Updating vehicle stocks")
        shipment_channel = self.bot.get_channel(667348336277323787)
        tokens = await self.database.guild(ctx.guild).Token()
        await self.database.guild(ctx.guild).Stocks.set([])
        try:
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': tokens
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        except:
            await msg.edit(content="Error: Invalid Token. Geting new token...")
            url = "https://api.eclipse-rp.net/auth/login"
            with open('../data.txt') as thefile:
                data = thefile.read()
                payload = str(data).replace("\n", "")
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
            }
            response = requests.request("POST", url, headers=headers, data = payload)
            result_token = response.json()['token']
            await self.database.guild(ctx.guild).Token.set(str(result_token))
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': str(result_token)
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            for x in data:
                if x['Name'] == 'Motorsport':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
                if x['Name'] == 'DownTownBoats':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
        stocks = await self.database.guild(ctx.guild).Stocks()
        sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
        await self.database.guild(ctx.guild).Stocks.set(sorted_stocks)
        oldstocks = await self.database.guild(ctx.guild).OldStocks()
        not_same = ''
        price_change = ''
        stock_change = ''
        newstock_change = ''
        all_change = ''
        soldout_change = ''
        for x in stocks:
            newstock = True
            for y in oldstocks:
                if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
                    all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
                    , y['Price'], x['Price'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
                    stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
                    price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
                    newstock = False
            if newstock is True:
                newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
        for x in oldstocks:
            if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
                soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
        try:
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            await shipment_channel.send(not_same)
        except:
            pass
        await self.database.guild(ctx.guild).OldStocks.set(sorted_stocks)
        await msg.edit(content="Stock has been updated.")
        # message = 'All the stock available in Motorsport Right now\n'
        stocks = await self.database.guild(ctx.guild).Stocks()
        classlist = [x['Class'] for x in stocks]
        classlist = list(dict.fromkeys(classlist))
        pages = []
        fieldnumber = 0
        embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(0xFF00FF))
        embed.set_thumbnail(url='https://i.imgur.com/xJyIgAQ.png')
        for x in classlist:
            message = ""
            for y in stocks:
                if y['Class'] == x:
                    message = message + "{} ({} Qty): ${:,d}\n".format(y['Name'], y['Stock'], y['Price'])
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
        CONTROLS = {"⬅️": utils.menus.prev_page, "❌": utils.menus.close_menu, "➡️": utils.menus.next_page}
        await utils.menus.menu(ctx, pages, CONTROLS, timeout=60.0)
        themessage = await ctx.channel.history(after=msg.created_at, limit=1).flatten()
        try:
            await themessage[0].delete()
        except:
            pass
        await msg.delete()
        # for allstocks in stocks:
        #     if counting < 10:
        #         message = message + "{} ({} Qty): ${:,d}\n".format(allstocks['Name'], allstocks['Stock'], allstocks['Price'])
        #         counting = counting + 1
        #     else:
        #         await ctx.send(message)
        #         message = ''
        #         counting = 0
        # if counting > 0:
        #     await ctx.send(message)
    
    @commands.command(pass_context=True)
    @commands.guild_only()
    async def checkprice(self, ctx):
        msg = await ctx.send("Updating vehicle stocks")
        shipment_channel = self.bot.get_channel(667348336277323787)
        tokens = await self.database.guild(ctx.guild).Token()
        await self.database.guild(ctx.guild).Stocks.set([])
        try:
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': tokens
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        except:
            await msg.edit(content="Error: Invalid Token. Geting new token...")
            url = "https://api.eclipse-rp.net/auth/login"
            with open('../data.txt') as thefile:
                data = thefile.read()
                payload = str(data).replace("\n", "")
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
            }
            response = requests.request("POST", url, headers=headers, data = payload)
            result_token = response.json()['token']
            await self.database.guild(ctx.guild).Token.set(str(result_token))
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': str(result_token)
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            for x in data:
                if x['Name'] == 'Motorsport':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
                if x['Name'] == 'DownTownBoats':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
        stocks = await self.database.guild(ctx.guild).Stocks()
        sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
        await self.database.guild(ctx.guild).Stocks.set(sorted_stocks)
        oldstocks = await self.database.guild(ctx.guild).OldStocks()
        not_same = ''
        price_change = ''
        stock_change = ''
        newstock_change = ''
        all_change = ''
        soldout_change = ''
        counting = 0
        for x in stocks:
            newstock = True
            for y in oldstocks:
                if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
                    all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
                    , y['Price'], x['Price'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
                    stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
                    price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
                    newstock = False
            if newstock is True:
                newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
        for x in oldstocks:
            if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
                soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
        try:
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            await shipment_channel.send(not_same)
        except:
            pass
        await self.database.guild(ctx.guild).OldStocks.set(sorted_stocks)
        await msg.edit(content="Stock has been updated.")
        counting = 0
        message = ""
        oldstocks = await self.database.guild(ctx.guild).OldStocks()
        Prices = await self.prices.guild(ctx.guild).Prices()
        category = [a['Type'] for a in oldstocks]
        category = list(dict.fromkeys(category))
        detected = False
        for z in category:
            message = "```fix\n{}```\n>>> ".format(z)
            counting = 0
            for x in oldstocks:
                for y in Prices:
                    if x['Name'] == y['Vehicle Name'] and ' $ {:,} '.format(x['Price']) != y['Price'] and x['Type'] == z:
                        message = message + "**{}** has the wrong price set (${:,}).\nCorrect Price:```{}```".format(x['Name'], x['Price'], y['Price'].replace(',','').replace('$','').replace(' ',''))
                        detected = True
                        if counting < 10:
                            counting = counting + 1
                        else:
                            await ctx.send(message)
                            message = '>>> '
                            counting = 0
            if counting > 0:
                await ctx.send(message)
        if detected is False:
            await ctx.send("If you see nothing. That's mean the price is right :D")
            
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.has_any_role("Owner", "Bot-Developer", "Bot-Admin")
    async def updatestocks(self, ctx):
        msg = await ctx.send("Updating vehicle stocks")
        shipment_channel = self.bot.get_channel(667348336277323787)
        tokens = await self.database.guild(ctx.guild).Token()
        await self.database.guild(ctx.guild).Stocks.set([])
        try:
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': tokens
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        except:
            await msg.edit(content="Error: Invalid Token. Geting new token...")
            url = "https://api.eclipse-rp.net/auth/login"
            with open('../data.txt') as thefile:
                data = thefile.read()
                payload = str(data).replace("\n", "")
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
            }
            response = requests.request("POST", url, headers=headers, data = payload)
            result_token = response.json()['token']
            await self.database.guild(ctx.guild).Token.set(str(result_token))
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': str(result_token)
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        async with self.database.guild(ctx.guild).Stocks() as stocks:
            for x in data:
                if x['Name'] == 'Motorsport':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
                if x['Name'] == 'DownTownBoats':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
        stocks = await self.database.guild(ctx.guild).Stocks()
        sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
        await self.database.guild(ctx.guild).Stocks.set(sorted_stocks)
        oldstocks = await self.database.guild(ctx.guild).OldStocks()
        not_same = ''
        price_change = ''
        stock_change = ''
        newstock_change = ''
        all_change = ''
        soldout_change = ''
        for x in stocks:
            newstock = True
            for y in oldstocks:
                if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
                    all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
                    , y['Price'], x['Price'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
                    stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
                    price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
                    newstock = False
            if newstock is True:
                newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
        for x in oldstocks:
            if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
                soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
        try:
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            await shipment_channel.send(not_same)
        except:
            pass
        await self.database.guild(ctx.guild).OldStocks.set(sorted_stocks)
        await msg.edit(content="Stock has been updated.")
    
    @tasks.loop(seconds=300.0)
    async def check_stock(self):
        shipment_channel = self.bot.get_channel(667348336277323787)
        print("Background Update Works")
        guild_id = self.bot.get_guild(341928926098096138)
        tokens = await self.database.guild(guild_id).Token()
        await self.database.guild(guild_id).Stocks.set([])
        try:
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': tokens
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        except:
            url = "https://api.eclipse-rp.net/auth/login"
            with open('../data.txt') as thefile:
                data = thefile.read()
                payload = str(data).replace("\n", "")
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
            }
            response = requests.request("POST", url, headers=headers, data = payload)
            result_token = response.json()['token']
            await self.database.guild(guild_id).Token.set(str(result_token))
            url = "https://api.eclipse-rp.net/basic/vehicledealerships"
            payload = {}
            headers = {
            'Accept': 'application/json, text/plain, */*',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'token': str(result_token)
            }
            response = requests.request("GET", url, headers=headers, data = payload)
            data = response.json()
            data = data['dealerships']
        async with self.database.guild(guild_id).Stocks() as stocks:
            for x in data:
                if x['Name'] == 'Motorsport':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
                if x['Name'] == 'DownTownBoats':
                    for y in x['VehicleStocks']:
                        if y['v']['Stock'] != 0:
                            stocks.append(y['v'])
        stocks = await self.database.guild(guild_id).Stocks()
        sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
        await self.database.guild(guild_id).Stocks.set(sorted_stocks)
        print("Updated Stocks")
        print("Comparing Stocks")

        oldstocks = await self.database.guild(guild_id).OldStocks()
        not_same = ''
        price_change = ''
        stock_change = ''
        newstock_change = ''
        all_change = ''
        soldout_change = ''
        for x in stocks:
            newstock = True
            for y in oldstocks:
                if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
                    all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
                    , y['Price'], x['Price'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
                    stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
                    newstock = False
                elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
                    price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
                    newstock = False
            if newstock is True:
                newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
        for x in oldstocks:
            if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
                soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
        print("Comparing Done")
        try:
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            await shipment_channel.send(not_same)
        except:
            pass
        await self.database.guild(guild_id).OldStocks.set(sorted_stocks)
        print("Done")

    @check_stock.before_loop
    async def before_check_stock(self):
        print('waiting...')
        await self.bot.wait_until_ready()
