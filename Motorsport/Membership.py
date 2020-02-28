import os
import asyncio
import datetime

# PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# discord
import discord
from discord.ext import commands

# redbot
from redbot.core import commands
from redbot.core import Config
from redbot.core import utils
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path

class Membership:
    """Its all about Motorsport - Customer Systems"""

    def __init__(self):
        self.membershipdb = Config.get_conf(self, identifier=2)
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