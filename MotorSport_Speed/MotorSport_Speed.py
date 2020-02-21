from discord.ext import tasks
from redbot.core import Config
import discord
import pygsheets
import random
import os
import asyncio
from discord.ext import commands
import json
from fuzzywuzzy import process
from redbot.core import commands

gc = pygsheets.authorize(service_file='/root/client_secret.json')

class MOTORSPORT_SPEED(commands.Cog):
    """Motorsport Order System"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def speed(self, ctx, *, car_name: str):

        """Used to check vehicle speed"""
        msg = await ctx.send("""**Please wait while I refine your search entries.**""")
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4')
        wks = sh.worksheet('id', '999161401')
        car_list = wks.get_col(4)
        # car_list_new = {n.lower(): n for n in car_list}
        # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 1, 0.6)]
        car_name_matched = process.extractBests(car_name, car_list, score_cutoff=80, limit=2)
        multiple_match = False
        if str(car_name_matched) == '[]':
            location = '[]'
        elif len(list(car_name_matched)) > 1 and car_name_matched[0][1] == car_name_matched[1][1]:
            location = '[]'
            multiple_match = True
        else:
            await msg.edit(content="""**You are looking for {}.\nPlease wait while I am getting the updated date for {} from the database created by Broughy1322 (https://www.youtube.com/broughy).**""".format(car_name_matched[0][0], car_name_matched[0][0]))
            # await asyncio.sleep(2)
            location = wks.find(car_name_matched[0][0], matchEntireCell=True)
        if str(location) != '[]':
            location = location[0].row
            value = wks.get_row(location)
            value = ['No Data' if x is '' else x for x in value]
            if value[5] != 'No Data':
                speed = float(value[5]) * 1.60934
                speed = '{0:.2f} km/h'.format(speed)
            else:
                speed = 'No Data'               
            embed = discord.Embed(title=value[3], colour=discord.Colour(0x984c87), description=value[2]+'\nThe vehicle is fully upgraded')
            embed.set_thumbnail(url='https://cdn.pixabay.com/photo/2016/06/15/15/02/info-1459077_960_720.png')
            embed.add_field(name="Position In Class:", value=value[1], inline=True)
            embed.add_field(name="Lap Time (Circuit Race):", value=value[4] + ' (m:ss.000)', inline=True)
            embed.add_field(name="Top Speed (Drag Race):", value=speed, inline=True)
            embed.set_footer(text="Data created by Broughy1322 (https://www.youtube.com/broughy)")
            embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            if multiple_match != True:
                thesimilarresult = "__**Did you mean?**__\n"
                # car_list_new = {n.lower(): n for n in car_list}
                # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 5, 0.5)]
                car_name_matched = process.extract(car_name, car_list, limit=5)
                if car_name_matched[0][0] != "Vehicle Name":
                    for i in range(len(list(car_name_matched))):
                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                    await msg.edit(content="""**Vehicle not found\nTry to provide more details on your search**\n\n""" + thesimilarresult)
                else:
                    await msg.edit(content="""**Vehicle not found\nTry to provide more details on your search**\n\n""")
            else:
                await msg.edit(content="""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def fastest(self, ctx, *, class_name: str):

        """Used to check fastest vehicle by Class"""
        msg = await ctx.send("""**Please wait while I refine your search entries.**""")
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4')
        wks = sh.worksheet('id', '999161401')
        car_list = wks.get_col(3)
        # car_list_new = {n.lower(): n for n in car_list}
        # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 1, 0.6)]
        car_name_matched = process.extractBests(class_name, car_list, score_cutoff=80, limit=2)
        multiple_match = False
        if str(car_name_matched) == '[]':
            location = '[]'
        elif len(list(car_name_matched)) > 1 and car_name_matched[0][1] != car_name_matched[1][1]:
            location = '[]'
            multiple_match = True
        else:
            await msg.edit(content="""**You are looking for fastest {}.\nPlease wait while I am getting the updated date for {} from the database created by Broughy1322 (https://www.youtube.com/broughy).**""".format(car_name_matched[0][0], car_name_matched[0][0]))
            # await asyncio.sleep(2)
            location = wks.find(car_name_matched[0][0], matchEntireCell=True)
        if str(location) != '[]':
            location = location[0].row
            value = wks.get_row(location)
            value = ['No Data' if x is '' else x for x in value]
            if value[5] != 'No Data':
                speed = float(value[5]) * 1.60934
                speed = '{0:.2f} km/h'.format(speed)
            else:
                speed = 'No Data'               
            embed = discord.Embed(title=value[3], colour=discord.Colour(0x984c87), description=value[2]+'\nThe vehicle is fully upgraded')
            embed.set_thumbnail(url='https://cdn.pixabay.com/photo/2016/06/15/15/02/info-1459077_960_720.png')
            embed.add_field(name="Position In Class:", value=value[1], inline=True)
            embed.add_field(name="Lap Time (Circuit Race):", value=value[4] + ' (m:ss.000)', inline=True)
            embed.add_field(name="Top Speed (Drag Race):", value=speed, inline=True)
            embed.set_footer(text="Data created by Broughy1322 (https://www.youtube.com/broughy)")
            embed.set_author(name="Premium Deluxe Motorsport", icon_url="https://media.discordapp.net/attachments/341936003029794826/342238781874896897/DuluxeMotorsportLogo2.png")
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            if multiple_match != True:
                thesimilarresult = "__**Did you mean?**__\n"
                # car_list_new = {n.lower(): n for n in car_list}
                # car_name_matched = [car_list_new[r] for r in difflib.get_close_matches(car_name.lower(), car_list_new, 5, 0.5)]
                car_name_matched = process.extract(class_name, car_list, limit=5)
                if car_name_matched[0][0] != "Vehicle Name":
                    for i in range(len(list(car_name_matched))):
                        thesimilarresult = thesimilarresult + str(car_name_matched[i][0]) + ' ' + "(" + str(car_name_matched[i][1]) + "%)\n"
                    await msg.edit(content="""**Vehicle not found\nTry to provide more details on your search**\n\n""" + thesimilarresult)
                else:
                    await msg.edit(content="""**Vehicle not found\nTry to provide more details on your search**\n\n""")
            else:
                await msg.edit(content="""**I have matched more than one result.**\n{} ({}%)\n{} ({}%)""".format(car_name_matched[0][0], car_name_matched[0][1], car_name_matched[1][0], car_name_matched[1][1]))