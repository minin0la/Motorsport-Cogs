from .MotorSport_Reaction import MOTORSPORT_REACTION
import asyncio


def setup(bot):
    bot.add_cog(MOTORSPORT_REACTION(bot))
