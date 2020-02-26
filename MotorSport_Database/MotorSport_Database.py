
import discord
from discord.ext import tasks
from discord.ext import commands
from redbot.core import Config
from redbot.core import utils
from redbot.core import commands

import requests
import os
import asyncio
import json
from fuzzywuzzy import process
import pygsheets
import random

from .Order import Order

class MOTORSPORT_DATABASE(commands.Cog):
    """Motorsport Database System"""

    def __init__(self, bot):
        self.bot = bot
        # self.update_vehicle.start()
        self.database = Config.get_conf(self, identifier=1)
        data = {"Vehicles": [],
                "OldStocks": [],
                "Token": "",
        }
        self.database.register_guild(**data)
        self.gc = pygsheets.authorize(service_file="client_secret.json")
        super().__init__()
    
    def cog_unload(self):
        self.update_vehicle.cancel()

    async def vehicle_price(self):
        print("Get Price")
        sh = self.gc.open_by_key("12gmECNatiWtDeGt5Oc3Zw7_CVP8kXxdwW50nqQ_Gfzg")
        wks = sh.worksheet_by_title("Bot Data Sheet")
        vehicle_name = wks.get_col(1, include_tailing_empty=False)
        price = wks.get_col(2, include_tailing_empty=False)
        types = wks.get_col(3, include_tailing_empty=False)
        brand = wks.get_col(4, include_tailing_empty=False)
        capacity = wks.get_col(5, include_tailing_empty=False)
        drive = wks.get_col(6, include_tailing_empty=False)
        vehicle_image = wks.get_col(7, include_tailing_empty=False)
        brand_image = wks.get_col(8, include_tailing_empty=False)
        performance_image = wks.get_col(9, include_tailing_empty=False)
        vip_price = wks.get_col(10, include_tailing_empty=False)
        glovebox = wks.get_col(11, include_tailing_empty=False)
        trunk = wks.get_col(12, include_tailing_empty=False)
        for_sale = wks.get_col(14, include_tailing_empty=False)
        veh_price = []

        for i in range(1, len(list(vehicle_name))):
            try:
                price_value = price[i].replace("$ ", "").replace(",", "")
                price_value = int(float(price_value))
                vip_price_value = vip_price[i].replace("$ ", "").replace(",", "")
                vip_price_value = int(float(vip_price_value))
            except ValueError:
                price_value = None
                vip_price_value = None
            veh_price.append(
                {
                    "Name": vehicle_name[i],
                    "Price": {
                        "Normal": price_value,
                        "VIP": vip_price_value,
                        "Cost": None,
                        "Stock_Price": None,
                    },
                    "Speed": {
                        "Laptime": {"Overall": None, "Class": None, "Value": None,},
                        "Top_Speed": {"Overall": None, "Class": None, "Value": None,},
                    },
                    "Storage":{
                        "Glovebox": glovebox[i],
                        "Trunk": trunk[i]
                        
                    },
                    "Type": types[i],
                    "Brand": brand[i],
                    "Capacity": capacity[i],
                    "Drive": drive[i],
                    "Vehicle Image": vehicle_image[i],
                    "Brand Image": brand_image[i],
                    "Performance Image": performance_image[i],
                    "Stock": None,
                    "For_Sale": for_sale[i]
                }
            )
        return veh_price
    
    async def vehicle_stock(self):
        print("Get stock")
        guild = self.bot.get_guild(341928926098096138)
        tokens = await self.database.guild(guild).Token()
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
            with open('data.txt') as thefile:
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
            await self.database.guild(guild).Token.set(str(result_token))
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
            data = data["dealerships"]
        stocks = []
        for x in data:
            if x["Name"] == "Motorsport":
                for y in x["VehicleStocks"]:
                    if y["v"]["Stock"] != 0:
                        stocks.append(y["v"])
            if x["Name"] == "DownTownBoats":
                for y in x["VehicleStocks"]:
                    if y["v"]["Stock"] != 0:
                        stocks.append(y["v"])
        sorted_stocks = sorted(stocks, key=lambda k: k["Name"])
        return sorted_stocks


    async def vehicle_speed(self):
        print("Get Speed")
        sh = self.gc.open_by_url(
            "https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4"
        )
        wks = sh.worksheet("id", "60309153")
        laptime_overall = wks.get_col(1, include_tailing_empty=False)
        laptime_inclass = wks.get_col(2, include_tailing_empty=False)
        vehicle_name_laptime = wks.get_col(4, include_tailing_empty=False)
        laptime = wks.get_col(5, include_tailing_empty=False)
        wks = sh.worksheet("id", "1859578320")
        topspeed_overall = wks.get_col(1, include_tailing_empty=False)
        topspeed_inclass = wks.get_col(2, include_tailing_empty=False)
        vehicle_name_topspeed = wks.get_col(4, include_tailing_empty=False)
        topspeed = wks.get_col(6, include_tailing_empty=False)
        return laptime_overall, laptime_inclass, vehicle_name_laptime, laptime, topspeed_overall, topspeed_inclass, vehicle_name_topspeed, topspeed

    
    async def combinedata(self, veh_price, stocks, speed):
        guild = self.bot.get_guild(341928926098096138)
        laptime_overall, laptime_inclass, vehicle_name_laptime, laptime, topspeed_overall, topspeed_inclass, vehicle_name_topspeed, topspeed = speed

        for x in veh_price:
            imported = False
            for y in stocks:
                if y["Name"] == x["Name"]:
                    x["Price"]["Cost"] = y["Cost"]
                    x["Price"]["Stock_Price"] = y["Price"]
                    x["Stock"] = y["Stock"]
                    imported = True
            if imported is False:
                x["Price"]["Cost"] = None
                x["Price"]["Stock_Price"] = None
                x["Stock"] = None

        importingerror = []
        for x in veh_price:
            try:
                a = vehicle_name_laptime.index(x["Name"])
                b = vehicle_name_topspeed.index(x["Name"])
                value = float(topspeed[b]) * 1.60934
                x["Speed"] = {
                    "Laptime": {
                        "Overall": laptime_overall[a],
                        "Class": laptime_inclass[a],
                        "Value": laptime[a],
                    },
                    "Top_Speed": {
                        "Overall": topspeed_overall[b],
                        "Class": topspeed_inclass[b],
                        "Value": value,
                    },
                }
            except ValueError:
                importingerror.append(x)

        for x in importingerror:
            car_name_matched = process.extractBests(
                x["Name"], vehicle_name_topspeed, score_cutoff=80, limit=1
            )
            try:
                a = vehicle_name_laptime.index(car_name_matched[0][0])
                b = vehicle_name_topspeed.index(car_name_matched[0][0])
                value = float(topspeed[b]) * 1.60934
                x["Speed"] = {
                    "Laptime": {
                        "Overall": laptime_overall[a],
                        "Class": laptime_inclass[a],
                        "Value": laptime[a],
                    },
                    "Top_Speed": {
                        "Overall": topspeed_overall[b],
                        "Class": topspeed_inclass[b],
                        "Value": value,
                    },
                }
            except ValueError:
                error_log = error_log + x["Name"] + " not imported for speed\n"

        for x in veh_price:
            for y in importingerror:
                if y['Name'] == x['Name']:
                    x = y
        await self.database.guild(guild).Vehicles.set(veh_price)
        print("Done")
    
    @tasks.loop(seconds=300.0)
    async def update_vehicle(self):
        veh_price = await self.vehicle_price()
        stocks = await self.vehicle_stock()
        speed = await self.vehicle_speed()
        await self.combinedata(veh_price, stocks, speed)
    
    @update_vehicle.before_loop
    async def before_update_vehicle(self):
        print('waiting...')
        await self.bot.wait_until_ready()
    
    @commands.command(pass_context=True)
    async def updatevehicle(self, ctx):
        await ctx.send("Please wait...")
        veh_price = await self.vehicle_price()
        stocks = await self.vehicle_stock()
        speed = await self.vehicle_speed()
        await ctx.send("Done getting data. Combine now")
        await self.combinedata(veh_price, stocks, speed)

    @commands.command(pass_context=True)
    async def order(self, ctx):
        await Order().order(ctx, car_name=None, database=self.database, ordering_channel=None)
        
    # @tasks.loop(seconds=300.0)
    # async def check_stock(self):
    #     shipment_channel = self.bot.get_channel(667348336277323787)
    #     print("Background Update Works")
    #     guild_id = self.bot.get_guild(341928926098096138)
    #     tokens = await self.database.guild(guild_id).Token()
    #     await self.database.guild(guild_id).Stocks.set([])
    #     try:
    #         url = "https://api.eclipse-rp.net/basic/vehicledealerships"
    #         payload = {}
    #         headers = {
    #         'Accept': 'application/json, text/plain, */*',
    #         'DNT': '1',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    #         'token': tokens
    #         }
    #         response = requests.request("GET", url, headers=headers, data = payload)
    #         data = response.json()
    #         data = data['dealerships']
    #     except:
    #         url = "https://api.eclipse-rp.net/auth/login"
    #         with open('../data.txt') as thefile:
    #             data = thefile.read()
    #             payload = str(data).replace("\n", "")
    #         headers = {
    #         'Accept': 'application/json, text/plain, */*',
    #         'DNT': '1',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    #         'Content-Type': 'application/json;charset=UTF-8'
    #         }
    #         response = requests.request("POST", url, headers=headers, data = payload)
    #         result_token = response.json()['token']
    #         await self.database.guild(guild_id).Token.set(str(result_token))
    #         url = "https://api.eclipse-rp.net/basic/vehicledealerships"
    #         payload = {}
    #         headers = {
    #         'Accept': 'application/json, text/plain, */*',
    #         'DNT': '1',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    #         'token': str(result_token)
    #         }
    #         response = requests.request("GET", url, headers=headers, data = payload)
    #         data = response.json()
    #         data = data['dealerships']
    #     async with self.database.guild(guild_id).Stocks() as stocks:
    #         for x in data:
    #             if x['Name'] == 'Motorsport':
    #                 for y in x['VehicleStocks']:
    #                     if y['v']['Stock'] != 0:
    #                         stocks.append(y['v'])
    #             if x['Name'] == 'DownTownBoats':
    #                 for y in x['VehicleStocks']:
    #                     if y['v']['Stock'] != 0:
    #                         stocks.append(y['v'])
    #     stocks = await self.database.guild(guild_id).Stocks()
    #     sorted_stocks = sorted(stocks, key=lambda k: k['Name'])
    #     await self.database.guild(guild_id).Stocks.set(sorted_stocks)
    #     print("Updated Stocks")
    #     print("Comparing Stocks")

    #     oldstocks = await self.database.guild(guild_id).OldStocks()
    #     not_same = ''
    #     price_change = ''
    #     stock_change = ''
    #     newstock_change = ''
    #     all_change = ''
    #     soldout_change = ''
    #     for x in stocks:
    #         newstock = True
    #         for y in oldstocks:
    #             if x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] == y['Stock']:
    #                 newstock = False
    #             elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] != y['Stock']:
    #                 all_change = all_change + "❗️ New change to {}: Qty {} > {} and Price {} > {}\n".format(x['Name'], y['Stock'], x['Stock']
    #                 , y['Price'], x['Price'])
    #                 newstock = False
    #             elif x["Vehicle"] == y["Vehicle"] and x['Price'] == y['Price'] and x['Stock'] != y['Stock']:
    #                 stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
    #                 newstock = False
    #             elif x["Vehicle"] == y["Vehicle"] and x['Price'] != y['Price'] and x['Stock'] == y['Stock']:
    #                 price_change = price_change + "💵 New change to {}: Price {} > {}\n".format(x['Name'], y['Price'], x['Price'])
    #                 newstock = False
    #         if newstock is True:
    #             newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {}\n".format(x['Name'], x['Stock'], x['Price'])
    #     for x in oldstocks:
    #         if not any(d['Vehicle'] == x['Vehicle'] for d in stocks):
    #             soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
    #     print("Comparing Done")
    #     try:
    #         not_same = newstock_change + stock_change + price_change + all_change + soldout_change
    #         await shipment_channel.send(not_same)
    #     except:
    #         pass
    #     await self.database.guild(guild_id).OldStocks.set(sorted_stocks)
    #     print("Done")

    # @check_stock.before_loop
    # async def before_check_stock(self):
    #     print('waiting...')
    #     await self.bot.wait_until_ready()
