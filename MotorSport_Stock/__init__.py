from .MotorSport_Stock import MOTORSPORT_STOCK
import asyncio


def setup(bot):
    bot.add_cog(MOTORSPORT_STOCK(bot))
