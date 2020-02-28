
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

class Database:
    """Motorsport Database System"""

    def __init__(self):
        self.database = Config.get_conf(self, identifier=1)
        data = {"Vehicles": [],
                "OldStocks": [],
                "Token": "",
        }
        self.database.register_guild(**data)
        self.gc = pygsheets.authorize(service_file="/root/client_secret.json")
        self.membershipdb = Config.get_conf(self, identifier=1)
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
            with open('/root/data.txt') as thefile:
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
        return veh_price

    async def comparingstocks(self, veh_price):
        shipment_channel = self.bot.get_channel(667348336277323787)
        guild = self.bot.get_guild(341928926098096138)
        oldstocks = await self.database.guild(guild).Vehicles()
        if oldstocks:
            not_same = ''
            price_change = ''
            stock_change = ''
            newstock_change = ''
            all_change = ''
            soldout_change = ''
            for x in veh_price:
                for y in oldstocks:
                    if x["Name"] == y["Name"]:
                        if x['Stock'] is None and y['Stock'] is not None:
                            soldout_change = soldout_change + "📢 This item has sold out! {}\n".format(x['Name'])
                        elif x['Stock'] is not None and y['Stock'] is None:
                            newstock_change = newstock_change + "🚛 New stock arrived for {}: Qty {} and Price {} {}\n".format(x['Name'], x['Stock'], x['Price']['Normal'], "✅" if x['Price']['Normal'] == x['Price']['Stock_Price'] else "")
                        elif x['Stock'] is not None and y['Stock'] is not None:        
                            if x['Price']['Stock_Price'] != y['Price']['Stock_Price']:
                                price_change = price_change + "💵 New change to {}: Price {} > {} {}\n".format(x['Name'], y['Price'], x['Price']['Normal'], "✅" if x['Price']['Normal'] == x['Price']['Stock_Price'] else "")
                            if x['Stock']!= y['Stock']:
                                stock_change = stock_change + "⚖️ New change to {}: Qty {} > {}\n".format(x['Name'], y['Stock'], x['Stock'])
            not_same = newstock_change + stock_change + price_change + all_change + soldout_change
            not_same = utils.chat_formatting.pagify(not_same, delims="\n")
            for x in not_same:
                await shipment_channel.send(x)
        
        await self.database.guild(guild).Vehicles.set(veh_price)
        print("Done")    

    async def get_vehicle(self, ctx, car_name):
        prices = await self.database.guild(ctx.guild).Vehicles()
        car_list = [d['Name'] for d in prices]
        selected_veh = None
        multiple_match_embed = None
        car_name_matched = process.extractBests(car_name, car_list, score_cutoff=80, limit=2)
        matched = False
        multiple_match = False
        if car_name_matched:
            matched = True
        if len(list(car_name_matched)) > 1 and car_name_matched[0][1] != 100:
            multiple_match = True
        if matched is True and multiple_match is not True:
            for price in prices:
                if price["Name"] == car_name_matched[0][0]:
                    selected_veh = price
        else:
            if multiple_match is not True:
                thesimilarresult = ""
                car_name_matched = process.extract(car_name, car_list, limit=5)
                for i in range(len(list(car_name_matched))):
                    thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                embed = discord.Embed(colour=discord.Colour(0x984c87), description='```{}```'.format(thesimilarresult))
                embed.set_author(name="""Vehicle not found\nTry to provide more details on your search\n\n""", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                multiple_match_embed = embed
            else:
                embed = discord.Embed(colour=discord.Colour(0x984c87), description='```{} ({}%)\n{} ({}%)```'.format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))
                embed.set_author(name="""I have matched more than one result.""", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
                multiple_match_embed = embed
        return selected_veh, multiple_match_embed