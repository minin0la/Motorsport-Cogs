from .MotorSport_Customers import MOTORSPORT_CUSTOMERS


def setup(bot):
    bot.add_cog(MOTORSPORT_CUSTOMERS(bot))
