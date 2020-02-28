import discord
import os
from discord.ext import commands
from redbot.core import commands
from redbot.core import Config
from redbot.core import utils
from redbot.core import checks
import asyncio

class MOTORSPORT_PARTNERSHIP(commands.Cog):
    """Its all about Motorsport - Partnership Systems"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def allpartnership(self, ctx):
        LSCGuild = self.bot.get_guild(463034981476990987)
        WeazelGuild = self.bot.get_guild(577618549976203303)
        LSCRole = discord.utils.get(LSCGuild.roles, name='Staff')
        WeazelRole = discord.utils.get(WeazelGuild.roles, name='Weazel News')
        await ctx.send("LSC Guild")
        async for x in LSCGuild.fetch_members():
            if LSCRole in x.roles:
                await ctx.send("{} (Staff)".format(x.name))

        await ctx.send("Weazel News Guild")
        async for x in WeazelGuild.fetch_members():
            if WeazelRole in x.roles:
                await ctx.send("{} (Weazel News)".format(x.name))
    
    @commands.command(pass_context=True)
    async def partner(self, ctx):
        author = ctx.author
        Minin0laGuild = self.bot.get_guild(676076481260290079)
        StaffRole = discord.utils.get(Minin0laGuild.roles, name='Staff')
        member = Minin0laGuild.get_member(ctx.author.id)
        if member is not None and StaffRole in member.roles:
            LSrole = ctx.guild.get_role(676091425393475640)
            await author.add_roles(LSrole)
            embed = discord.Embed(title="Motorsport Management", colour=discord.Colour(
                0xFF0000), description="Dear {},\n\nDue to your position at your place of employment, we are pleased to inform you that you are now a Motorsport Partner™️. View our <#345600420883988481> channel for more details, take note that you are now entitled to VIP discounts!\nHave a fantastic day & enjoy your new perks!".format(author.display_name))
            embed.set_thumbnail(
                url="https://i.imgur.com/maeMy11.png")
            try:
                await author.send(embed=embed)
            except discord.errors.Forbidden:
                pass
        else:
            await ctx.send("Access Denied")
