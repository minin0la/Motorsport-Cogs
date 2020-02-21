from .MotorSport_Price import MOTORSPORT_PRICE


def setup(bot):
    bot.add_cog(MOTORSPORT_PRICE(bot))
