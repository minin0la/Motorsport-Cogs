import requests
from discord.ext import tasks
from redbot.core import Config
import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import MemberConverter
import json
from fuzzywuzzy import process
from redbot.core import commands

class MOTORSPORT_REACTION(commands.Cog):
    """Motorsport Reaction System"""

    def __init__(self, bot):
        self.bot = bot
        self.membership = Config.get_conf(None, identifier=1, cog_name="MOTORSPORT_CUSTOMERS")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if payload.channel_id == 341936700366258177 and payload.member.bot is not True:
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
                async with self.membership.member(member).Orders() as orders:
                    for x in orders:
                        if x['Order_ID'] == payload.message_id:
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
                await self.membership.member(member).Customer_Status.set(True)
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
                await self.membership.member(member).VIP_Status.set(True)
                try:
                    await member.send(embed=embed)
                    await order_channel.send(content="VIP rank notification has been sent to {}".format(member.mention))
                except discord.errors.Forbidden:
                    await order_channel.send("**[Warning]** {} turned off his PM".format(member.mention))
